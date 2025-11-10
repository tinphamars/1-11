
## 🔧 Các Thành Phần Kỹ Thuật

### 1. Text Splitter

**RecursiveCharacterTextSplitter** chia text thông minh:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Kích thước mỗi chunk
    chunk_overlap=200,      # Overlap để giữ ngữ cảnh
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Ưu tiên chia theo paragraph
)
```

**Ví dụ:**

```
Original text (2500 chars):
"# Hệ Thống Quản Lý\n\n## Tổng Quan\nHệ thống giúp...[800 chars]...\n\n## Tính Năng\n### Quản Lý Nhân Viên\n...[1200 chars]...\n\n## API\nEndpoints chính..."

After splitting:
Chunk 1 (1000 chars): "# Hệ Thống Quản Lý\n\n## Tổng Quan..."
                        └─ overlap 200 chars ─┐
Chunk 2 (1000 chars):                    "...Hệ thống giúp...\n\n## Tính Năng..."
                                          └─ overlap 200 chars ─┐
Chunk 3 (700 chars):                                      "...### Quản Lý...\n\n## API..."
```

**Tại sao cần overlap?**

- Giữ ngữ cảnh giữa các chunks
- Tránh mất thông tin ở ranh giới
- Tăng khả năng tìm kiếm chính xác

### 2. Document Loaders

```python
def _get_loader(file_path):
    """Chọn loader phù hợp theo extension"""
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
vector = embeddings.embed_query("Hệ thống quản lý nhân viên")
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

#### Khởi tạo

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

#### Thêm documents

```python
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Text 1", "Text 2"],
    metadatas=[{"source": "file1.md"}, {"source": "file2.md"}],
    ids=["doc_0", "doc_1"]
)
```

#### Tìm kiếm

```python
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)
```

## ⚡ Tối Ưu Hóa

### 1. Concurrent Processing

```python
# Xử lý nhiều files song song
tasks = [_process_single_file(file) for file in valid_files]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. Thread Pool for I/O

```python
executor = ThreadPoolExecutor(max_workers=4)

# Chạy blocking operations trong thread pool
embeddings = await asyncio.get_event_loop().run_in_executor(
    executor, 
    openai_embeddings.embed_documents, 
    texts
)
```

### 3. Batch Processing

```python
# Tạo embeddings theo batch thay vì từng cái một
BATCH_SIZE = 100

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i + BATCH_SIZE]
    embeddings = create_embeddings(batch)
    save_to_db(embeddings)
```

### 4. Caching

ChromaDB tự động cache:
- Lưu persistent trên disk
- Không cần reload khi restart
- Tìm kiếm nhanh với index

## 📊 Metrics & Monitoring

### Metrics Quan Trọng

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
Quá nhỏ (< 500):  Mất ngữ cảnh, nhiều chunks không cần thiết
Tối ưu (800-1200): Cân bằng ngữ cảnh và độ chính xác
Quá lớn (> 2000):  GPT có thể bị overwhelm, chậm
```

### 2. Retrieval K Value

```python
k = 3:  Nhanh, ít context, có thể thiếu thông tin
k = 5:  Cân bằng tốt (khuyến nghị)
k = 10: Nhiều context, nhưng có thể có noise
```

### 3. Temperature Settings

```
0.0 - 0.3:  Deterministic, chính xác, lặp lại
0.5 - 0.7:  Cân bằng (khuyến nghị cho RAG)
0.8 - 1.0:  Sáng tạo, nhưng có thể sai lệch
```

### 4. Context Window Management

```
GPT-4o-mini: 128k tokens context window
Mỗi token ≈ 4 chars

Ví dụ:
5 documents × 1000 chars = 5000 chars ≈ 1250 tokens
System prompt: ~500 tokens
User message: ~50 tokens
Response budget: ~1000 tokens
────────────────────────────────────────
Total: ~2800 tokens (còn rất nhiều cho context)
```
