import warnings
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# Suppress ChromaDB telemetry warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*telemetry.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*capture.*")

# Configure logging
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)

from app.core.config import get_settings
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    HealthResponse
)

# Global service instances
document_service: Optional[DocumentService] = None
chat_service: Optional[ChatService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global document_service, chat_service

    document_service = None
    chat_service = None

    try:
        settings = get_settings()

        # Initialize services
        try:
            print("🔄 Initializing document service...")
            document_service = DocumentService(settings)
            print("✅ Document service initialized")
        except Exception as e:
            print(f"❌ Failed to initialize document service: {str(e)}")
            raise

        try:
            print("🔄 Initializing chat service...")
            chat_service = ChatService(settings, document_service)
            print("✅ Chat service initialized")
        except Exception as e:
            print(f"❌ Failed to initialize chat service: {str(e)}")
            raise

        # Auto-load documents if enabled
        if settings.auto_load_on_startup:
            print("🔄 Auto-loading documents from 'documents' folder...")
            try:
                result = await document_service.auto_load_documents()
                if result["processed_files"] > 0:
                    print(f"✅ Auto-loaded {result['processed_files']} files, {result['total_chunks']} chunks")
                else:
                    print("ℹ️ No documents found to auto-load")
            except Exception as e:
                print(f"⚠️ Warning: Error auto-loading documents: {str(e)}")
                print("⚠️ Continuing startup without auto-loaded documents...")

        print("🚀 RAG Chatbot API initialized successfully")
    except Exception as e:
        print(f"❌ Fatal error during startup: {str(e)}")
        import traceback
        traceback.print_exc()
        # Re-raise to prevent the app from starting in an invalid state
        # But wrap it to provide better error context
        raise RuntimeError(f"Failed to initialize application: {str(e)}") from e

    try:
        yield  # --- app runs here ---
    finally:
        # Cleanup
        try:
            if document_service:
                await document_service.cleanup()
            print("🛑 RAG Chatbot API shutdown complete")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="A RAG (Retrieval-Augmented Generation) chatbot API for project documentation and source code analysis.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)
origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # List of allowed origins
    allow_credentials=True,          # Allow cookies, authorization headers
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all HTTP headers
)
# Dependency injection for FastAPI
def get_document_service() -> DocumentService:
    """Dependency to get document service"""
    if document_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not initialized"
        )
    return document_service


def get_chat_service() -> ChatService:
    """Dependency to get chat service"""
    if chat_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service not initialized"
        )
    return chat_service


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information"""
    return HealthResponse(
        status="healthy",
        message="RAG Chatbot API is running",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All services are operational",
        version="1.0.0"
    )


@app.post("/documents/refresh", response_model=DocumentUploadResponse)
async def refresh_documents(
    service: DocumentService = Depends(get_document_service)
):
    """
    Refresh documents by re-loading from the default documents folder.
    This will clear existing documents and reload everything.
    """
    try:
        # Clear existing documents first
        await service.clear_database()

        # Auto-load documents again
        result = await service.auto_load_documents()

        return DocumentUploadResponse(
            success=True,
            message=f"Successfully refreshed {result['processed_files']} documents",
            processed_files=result["processed_files"],
            total_chunks=result["total_chunks"],
            details=result.get("details", [])
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing documents: {str(e)}"
        )

@app.get("/documents/folder-info")
async def get_documents_folder_info(
    service: DocumentService = Depends(get_document_service)
):
    """Get information about the documents folder"""
    try:
        settings = get_settings()
        docs_folder = Path(settings.documents_folder)

        if not docs_folder.exists():
            return {
                "folder_path": str(docs_folder.absolute()),
                "exists": False,
                "files_count": 0,
                "supported_files": [],
            }

        # Count files by extension
        files_info = {}
        total_files = 0
        supported_files = []

        for file_path in docs_folder.rglob("*"):
            if file_path.is_file():
                total_files += 1
                ext = file_path.suffix.lower()
                files_info[ext] = files_info.get(ext, 0) + 1

                if ext in settings.supported_extensions:
                    supported_files.append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(docs_folder)),
                        "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                        "extension": ext
                    })

        return {
            "folder_path": str(docs_folder.absolute()),
            "exists": True,
            "total_files": total_files,
            "files_by_extension": files_info,
            "supported_files_count": len(supported_files),
            "supported_files": supported_files[:20],  # Limit to first 20 for display
            "auto_load_enabled": settings.auto_load_on_startup
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get folder info: {str(e)}"
        )

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    request: DocumentUploadRequest,
    service: DocumentService = Depends(get_document_service)
):
    """Upload and process documents from a specified folder"""
    try:
        result = await service.process_documents(
            folder_path=request.folder_path,
            file_patterns=request.file_patterns
        )

        return DocumentUploadResponse(
            success=True,
            message=f"Processed {result['processed_files']} files successfully.",
            processed_files=result["processed_files"],
            total_chunks=result["total_chunks"],
            details=result.get("details", [])
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload documents: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Chat with the RAG system about the uploaded documents.
    The system will retrieve relevant context and generate responses.
    """
    try:
        response = await chat_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        return ChatResponse(
            response=response["answer"],
            conversation_id=response["conversation_id"],
            sources=response.get("sources", []),
            metadata=response.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@app.get("/documents/status")
async def get_document_status(
    service: DocumentService = Depends(get_document_service)
):
    """Get the status of the document database"""
    try:
        status_info = await service.get_status()
        return JSONResponse(content=status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@app.delete("/documents/clear")
async def clear_documents(
    service: DocumentService = Depends(get_document_service)
):
    """Clear all documents from the vector database"""
    try:
        await service.clear_database()
        return JSONResponse(content={"message": "Document database cleared successfully"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000, reload=True,
        debug=settings.debug)