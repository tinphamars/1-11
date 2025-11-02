import logging
import warnings
import chromadb
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Any, List
import asyncio

# Suppress ChromaDB telemetry warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*telemetry.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*capture.*")

from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    TextLoader,
    PythonLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
)

from app.core.config import Settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling document processing and vector storage"""

    def __init__(self, settings: Settings):
        self.settings = settings

        # Initialize embeddings using sentence-transformers
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'}
        )

        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )


        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(settings.collection_name)
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=settings.collection_name,
                metadata={"description": "RAG documents collection"}
            )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Thread pool for file processing
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def auto_load_documents(self) -> Dict[str, Any]:
        """Auto-load documents from the default documents folder"""
        documents_folder = Path(self.settings.documents_folder)

        if not documents_folder.exists():
            logger.warning(f"Documents folder does not exist: {documents_folder}")
            return {
                "processed_files": 0,
                "total_chunks": 0,
                "details": [f"Documents folder not found: {documents_folder}"]
            }

        # Default file patterns for supported extensions
        file_patterns = [f"*{ext}" for ext in self.settings.supported_extensions]
        logger.info(f"Auto-loading documents from: {documents_folder}")

        result = await self.process_documents(str(documents_folder), file_patterns)

        if result["processed_files"] > 0:
            logger.info(f"Auto-loaded {result['processed_files']} files, {result['total_chunks']} chunks")
        else:
            logger.warning("No documents were auto-loaded")

        return result

    async def process_documents(self, folder_path: str, file_patterns: List[str]) -> Dict[str, Any]:
        """Process documents from a folder and add them to the vector database"""
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # Find matching files
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(folder.rglob(pattern))

        # Filter by supported extensions and file size
        valid_files = []
        for file_path in files_to_process:
            if file_path.is_file():
                if file_path.suffix.lower() in self.settings.supported_extensions:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    if file_size_mb <= self.settings.max_file_size_mb:
                        valid_files.append(file_path)

        if not valid_files:
            return {
                "processed_files": 0,
                "total_chunks": 0,
                "details": ["No valid files found to process"]
            }

        # Process files concurrently
        tasks = [self._process_single_file(file_path) for file_path in valid_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_documents = []
        processed_count = 0
        error_details = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_details.append(f"Error processing {valid_files[i]}: {str(result)}")
            else:
                all_documents.extend(result)
                processed_count += 1

        # Add documents to the vector database
        if all_documents:
            await self._add_documents_to_db(all_documents)

        return {
            "processed_files": processed_count,
            "total_chunks": len(all_documents),
            "details": error_details if error_details else []
        }

    async def _process_single_file(self, file_path: Path) -> List[Document]:
        """Process a single file and return document chunks"""
        try:
            # Load document based on file type
            loader = self.get_loader(file_path)

            loop = asyncio.get_event_loop()
            documents = await loop.run_in_executor(self.executor, loader.load)

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Add metadata
            for chunk in chunks:
                chunk.metadata.update({
                    "source": str(file_path),
                    "file_type": file_path.suffix,
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size
                })

            return chunks

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def get_loader(self, file_path: Path):
        """Get appropriate document loader based on file extension"""
        extension = file_path.suffix.lower()

        if extension == ".py":
            return PythonLoader(str(file_path))
        elif extension == ".md":
            return TextLoader(str(file_path), encoding="utf-8")
        elif extension == ".json":
            return JSONLoader(str(file_path), jq_schema=".")
        elif extension == ".docx":
            return UnstructuredWordDocumentLoader(str(file_path))
        elif extension == ".pdf":
            return PyPDFLoader(str(file_path))
        else:
            # Default loader for text and similar files
            return TextLoader(str(file_path), encoding="utf-8")
        
    
    async def _add_documents_to_db(self, documents: List[Document]):
        """Add documents to ChromaDB vector database"""
        if not documents:
            return

        # Extract texts and metadata
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Generate embeddings asynchronously
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            self.embeddings.embed_documents,
            texts
        )

        # Generate unique IDs
        ids = [f"doc_{i}_{abs(hash(text[:100]))}" for i, text in enumerate(texts)]

        # Add to ChromaDB collection
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to ChromaDB collection.")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise

    async def search_similar_documents(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if k is None:
            k = self.settings.retrieval_k

        # Generate query embedding
        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(
            self.executor,
            self.embeddings.embed_query,
            query
        )

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        similar_docs = []
        if results.get("documents") and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                similar_docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1 - distance,   # Convert distance to similarity score
                    "rank": i + 1
                })

        return similar_docs

    async def get_status(self) -> Dict[str, Any]:
        """Get status of the document database"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.settings.collection_name,
                "document_count": count,
                "status": "healthy" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Error getting database status: {e}")
            return {
                "collection_name": self.settings.collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            }

    async def clear_database(self):
        """Clear all documents from the database"""
        try:
            # Delete and recreate the collection
            self.chroma_client.delete_collection(self.settings.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.settings.collection_name,
                metadata={"description": "RAG documents collection"}
            )
            logger.info("ChromaDB collection cleared and recreated successfully.")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
            logger.info("Executor shutdown completed.")
