
## 🔧 Technical Components

### 1. Text Splitter

**RecursiveCharacterTextSplitter** intelligently splits text:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Size of each chunk
    chunk_overlap=200,      # Overlap to maintain context
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Prioritize paragraph splitting
)
```

**Example:**

```
Original text (2500 chars):
"# Management System\n\n## Overview\nSystem helps...[800 chars]...\n\n## Features\n### Employee Management\n...[1200 chars]...\n\n## API\nMain endpoints..."

After splitting:
Chunk 1 (1000 chars): "# Management System\n\n## Overview..."
                        └─ overlap 200 chars ─┐
Chunk 2 (1000 chars):                    "...System helps...\n\n## Features..."
                                          └─ overlap 200 chars ─┐
Chunk 3 (700 chars):                                      "...### Employee...\n\n## API..."
```

**Why is overlap needed?**

- Maintain context between chunks
- Avoid information loss at boundaries
- Increase accurate search capability

### 2. Document Loaders

```python
def _get_loader(file_path):
    """Select appropriate loader by extension"""
    extension = file_path.suffix.lower()
    
    loaders = {
        ".py": PythonLoader,
        ".md": UnstructuredMarkdownLoader,
        ".json": JSONLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".yaml": TextLoader,
        ".yml": TextLoader,
        ".rst": TextLoader
    }
    
    return loaders.get(extension, TextLoader)(str(file_path))
```

### 3. OpenAI Integration

#### Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    openai_api_key=settings.openai_api_key,
    model="text-embedding-ada-002"
)

# Single text
vector = embeddings.embed_query("Employee management system")
# → [0.023, -0.891, ...] (1536 dimensions)

# Multiple texts
vectors = embeddings.embed_documents([
    "Text 1",
    "Text 2",
    "Text 3"
])
# → [[...], [...], [...]]
```

#### Chat Completion

```python
import openai

client = openai.OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key=settings.openai_api_key
)

response = client.chat.completions.create(
    model="GPT-4o-mini",
    messages=[
        {"role": "system", "content": "System prompt with context..."},
        {"role": "user", "content": "User question..."}
    ],
    temperature=0.7,
    max_tokens=1000
)

answer = response.choices[0].message.content
```

### 4. ChromaDB Operations

#### Initialization

```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="documents",
    metadata={"description": "RAG documents collection"}
)
```

#### Adding documents

```python
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Text 1", "Text 2"],
    metadatas=[{"source": "file1.md"}, {"source": "file2.md"}],
    ids=["doc_0", "doc_1"]
)
```

#### Searching

```python
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)
```

## ⚡ Optimization

### 1. Concurrent Processing

```python
# Process multiple files in parallel
tasks = [_process_single_file(file) for file in valid_files]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. Thread Pool for I/O

```python
executor = ThreadPoolExecutor(max_workers=4)

# Run blocking operations in thread pool
embeddings = await asyncio.get_event_loop().run_in_executor(
    executor, 
    openai_embeddings.embed_documents, 
    texts
)
```

### 3. Batch Processing

```python
# Create embeddings in batches instead of one by one
BATCH_SIZE = 100

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i + BATCH_SIZE]
    embeddings = create_embeddings(batch)
    save_to_db(embeddings)
```

### 4. Caching

ChromaDB automatically caches:
- Persistent storage on disk
- No need to reload on restart
- Fast search with indexing

## 📊 Metrics & Monitoring

### Important Metrics

```python
# Document processing
- documents_processed_total
- documents_failed_total
- chunks_created_total
- processing_time_seconds

# Search
- search_queries_total
- search_latency_seconds
- search_results_count

# Chat
- chat_requests_total
- chat_response_time_seconds
- tokens_used_total
- context_relevance_score
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info level
logger.info(f"Auto-loaded {count} files, {chunks} chunks")

# Warning level
logger.warning(f"File too large: {file_path}")

# Error level
logger.error(f"Failed to process {file_path}: {error}")
```

## 🎯 Best Practices

### 1. Chunk Size Optimization

```
Too small (< 500):  Loss of context, unnecessary chunks
Optimal (800-1200): Balance context and accuracy
Too large (> 2000):  GPT may be overwhelmed, slow
```

### 2. Retrieval K Value

```python
k = 3:  Fast, less context, may miss information
k = 5:  Good balance (recommended)
k = 10: More context, but may have noise
```

### 3. Temperature Settings

```
0.0 - 0.3:  Deterministic, accurate, repeatable
0.5 - 0.7:  Balanced (recommended for RAG)
0.8 - 1.0:  Creative, but may deviate
```

### 4. Context Window Management

```
GPT-4o-mini: 128k tokens context window
Each token ≈ 4 chars

Example:
5 documents × 1000 chars = 5000 chars ≈ 1250 tokens
System prompt: ~500 tokens
User message: ~50 tokens
Response budget: ~1000 tokens
────────────────────────────────────────
Total: ~2800 tokens (plenty left for context)
```
