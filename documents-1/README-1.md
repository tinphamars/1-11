# Kiến Trúc & Cách Hoạt Động của RAG Chatbot API

## 📋 Tổng Quan

RAG (Retrieval-Augmented Generation) Chatbot API là hệ thống AI kết hợp việc tìm kiếm thông tin từ documents với khả năng sinh text của GPT để trả lời câu hỏi một cách chính xác và có ngữ cảnh.

### Nguyên Tắc Hoạt Động

```
Documents → Embeddings → Vector DB → Search → Context → GPT → Answer
```

## 🏗️ Kiến Trúc Hệ Thống

### Sơ Đồ Tổng Quan

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG CHATBOT API                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   FastAPI    │      │   Swagger    │                    │
│  │   Endpoints  │◄────►│   UI/Docs    │                    │
│  └──────┬───────┘      └──────────────┘                    │
│         │                                                    │
│         ├──────────┬──────────────┬──────────────┐         │
│         ▼          ▼              ▼              ▼          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │   Chat   │ │ Document │ │  Upload  │ │  Status  │     │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘     │
│       │            │             │                          │
│       └────────────┼─────────────┘                          │
│                    ▼                                         │
│         ┌─────────────────────┐                            │
│         │   ChromaDB          │                            │
│         │   Vector Database   │                            │
│         └─────────────────────┘                            │
│                    │                                         │
│                    ▼                                         │
│         ┌─────────────────────┐                            │
│         │   OpenAI API        │                            │
│         │   - Embeddings      │                            │
│         │   - Chat GPT        │                            │
│         └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Quy Trình Hoạt Động Chi Tiết

### Phase 1: Khởi Động & Load Documents

```mermaid
graph TD
    A[Start Application] --> B[Load .env Config]
    B --> C[Initialize Services]
    C --> D{AUTO_LOAD_ON_STARTUP?}
    D -->|Yes| E[Scan ./documents folder]
    D -->|No| F[Ready to accept requests]
    E --> G[Find all supported files]
    G --> H[Process each file]
    H --> I[Split into chunks]
    I --> J[Generate embeddings]
    J --> K[Save to ChromaDB]
    K --> F
```

#### Bước 1: Quét Thư Mục Documents

```python
# Trong document_service.py

def auto_load_documents():
    """
    Tự động load documents từ thư mục mặc định
    """
    # 1. Xác định thư mục
    documents_folder = Path("./documents")
    
    # 2. Tìm tất cả files theo pattern
    file_patterns = ["*.py", "*.md", "*.txt", "*.json", 
                     "*.yaml", "*.docx", "*.pdf"]
    
    # 3. Lọc file hợp lệ
    valid_files = []
    for pattern in file_patterns:
        for file_path in documents_folder.rglob(pattern):
            # Kiểm tra size
            if file_path.stat().st_size <= MAX_FILE_SIZE_MB * 1024 * 1024:
                valid_files.append(file_path)
    
    # 4. Xử lý từng file
    for file_path in valid_files:
        process_single_file(file_path)
```

#### Bước 2: Xử Lý File

```python
def _process_single_file(file_path):
    """
    Xử lý một file duy nhất
    """
    # 1. Chọn loader phù hợp
    loader = _get_loader(file_path)
    
    # 2. Load nội dung
    documents = loader.load()
    
    # 3. Split thành chunks
    chunks = text_splitter.split_documents(documents)
    
    # 4. Thêm metadata
    for chunk in chunks:
        chunk.metadata = {
            "source": str(file_path),
            "file_type": file_path.suffix,
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size
        }
    
    return chunks
```

**Ví dụ thực tế:**

```
File: employee_management_system/README.md (5,120 bytes)
    ↓
Load content: "# Hệ Thống Quản Lý Nhân Viên\n\n## Tổng Quan..."
    ↓
Split into chunks (chunk_size=1000, overlap=200):
    Chunk 1: "# Hệ Thống Quản Lý Nhân Viên\n\n## Tổng Quan..."
    Chunk 2: "...## Đặc Trưng Chính\n### Quản Lý Phòng Ban..."
    Chunk 3: "...### Quản Lý Nhân Viên\n- Thông tin cá nhân..."
    Chunk 4: "...## Công Nghệ Sử Dụng\n- FastAPI..."
    Chunk 5: "...## API Endpoints\nPOST /employees..."
    Chunk 6: "...## Bảo Mật\n- JWT Token..."
    ↓
Total: 6 chunks
```

#### Bước 3: Tạo Embeddings

```python
def _add_documents_to_db(documents):
    """
    Chuyển đổi text thành vector embeddings
    """
    # 1. Trích xuất text từ chunks
    texts = [doc.page_content for doc in documents]
    
    # 2. Gọi OpenAI Embedding API
    embeddings = openai_embeddings.embed_documents(texts)
    
    # 3. Lưu vào ChromaDB
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=[doc.metadata for doc in documents],
        ids=[f"doc_{i}_{hash(text[:100])}" for i, text in enumerate(texts)]
    )
```

**Embedding là gì?**

Embedding chuyển đổi text thành vector số để máy tính hiểu ngữ nghĩa:

```
Text: "Hệ thống quản lý nhân viên giúp theo dõi thông tin nhân sự"
    ↓ OpenAI text-embedding-ada-002
Vector (1536 chiều): 
[0.023, -0.891, 0.234, 0.567, -0.123, 0.789, ..., 0.456]
           ↑
    Mỗi số đại diện cho một "khía cạnh" ngữ nghĩa
```

**Tại sao cần Embeddings?**

- Text có ngữ nghĩa giống nhau → Vector gần nhau
- Cho phép tìm kiếm theo ý nghĩa, không chỉ từ khóa
- "nhân viên" và "người lao động" → vectors tương tự

### Phase 2: Chat & Trả Lời Câu Hỏi

```mermaid
graph TD
    A[User Question] --> B[Create Query Embedding]
    B --> C[Search ChromaDB]
    C --> D[Get Top K Similar Documents]
    D --> E[Build Context]
    E --> F[Call GPT with Context]
    F --> G[Generate Answer]
    G --> H[Return Response + Sources]
```

#### Bước 1: Nhận Câu Hỏi

```http
POST /chat
Content-Type: application/json

{
  "message": "Làm sao để tạo nhân viên mới trong hệ thống?",
  "conversation_id": null,
  "max_tokens": 1000,
  "temperature": 0.7
}
```

#### Bước 2: Tạo Query Embedding

```python
# Trong document_service.py

def search_similar_documents(query, k=5):
    """
    Tìm documents tương tự với câu hỏi
    """
    # 1. Tạo embedding cho câu hỏi
    query_embedding = openai_embeddings.embed_query(query)
    
    # query_embedding = [0.123, -0.456, 0.789, ...]
```

#### Bước 3: Tìm Kiếm Vector Similarity

```python
    # 2. Tìm trong ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,  # Lấy top 5
        include=["documents", "metadatas", "distances"]
    )
```

**Vector Similarity Search hoạt động thế nào?**

```
Query Vector:     [0.1, 0.9, 0.2, ...]

Document Vectors in DB:
Doc 1: [0.12, 0.88, 0.19, ...]  → Cosine similarity: 0.96 ✓ (Very similar)
Doc 2: [0.5, 0.3, 0.8, ...]     → Cosine similarity: 0.75 ✓ (Similar)
Doc 3: [-0.8, 0.1, -0.9, ...]   → Cosine similarity: 0.32 ✗ (Not similar)
Doc 4: [0.11, 0.91, 0.21, ...]  → Cosine similarity: 0.98 ✓ (Most similar!)
Doc 5: [0.2, 0.7, 0.3, ...]     → Cosine similarity: 0.85 ✓ (Similar)

→ Return top 5: Doc 4, Doc 1, Doc 5, Doc 2, (Doc 6...)
```

**Kết quả tìm kiếm:**

```json
[
  {
    "content": "## API Endpoints\n\n### Employees\n```\nPOST /api/v1/employees\n```\nTạo nhân viên mới với thông tin: fullName, email, phone, departmentId...",
    "metadata": {
      "source": "./documents/employee_management_system/docs/API_DOCUMENTATION.md",
      "file_name": "API_DOCUMENTATION.md"
    },
    "score": 0.92
  },
  {
    "content": "class Employee:\n    fullName: str\n    email: str\n    phone: str\n    departmentId: int\n    position: str\n    hireDate: date\n    salary: float",
    "metadata": {
      "source": "./documents/employee_management_system/models/employee.py"
    },
    "score": 0.88
  },
  {
    "content": "### Thêm Nhân Viên Mới\n\n1. Truy cập menu Employees\n2. Click nút 'Thêm mới'\n3. Điền form với thông tin bắt buộc\n4. Upload CV nếu có\n5. Click 'Lưu'",
    "metadata": {
      "source": "./documents/employee_management_system/docs/USER_GUIDE.md"
    },
    "score": 0.85
  }
]
```

#### Bước 4: Xây Dựng Context

```python
# Trong chat_service.py

def chat(message, conversation_id=None):
    """
    Xử lý chat với RAG
    """
    # 1. Tìm documents liên quan
    similar_docs = document_service.search_similar_documents(
        message, 
        k=5
    )
    
    # 2. Xây dựng context từ documents tìm được
    context = "\n\n---\n\n".join([
        f"Document {i+1} (Source: {doc['metadata']['file_name']}):\n{doc['content']}"
        for i, doc in enumerate(similar_docs)
    ])
```

**Context được tạo:**

```
Document 1 (Source: API_DOCUMENTATION.md):
## API Endpoints

### Employees
```
POST /api/v1/employees
```
Tạo nhân viên mới với thông tin: fullName, email, phone, departmentId...

---

Document 2 (Source: employee.py):
class Employee:
    fullName: str
    email: str
    phone: str
    departmentId: int
    position: str
    hireDate: date
    salary: float

---

Document 3 (Source: USER_GUIDE.md):
### Thêm Nhân Viên Mới

1. Truy cập menu Employees
2. Click nút 'Thêm mới'
3. Điền form với thông tin bắt buộc
4. Upload CV nếu có
5. Click 'Lưu'
```

#### Bước 5: Gọi GPT

```python
    # 3. Tạo messages cho GPT
    messages = [
        {
            "role": "system",
            "content": f"""Bạn là trợ lý AI thông minh, giúp người dùng trả lời câu hỏi về dự án dựa trên tài liệu được cung cấp.

Dựa vào context sau để trả lời câu hỏi của người dùng:

{context}

Hướng dẫn:
- Trả lời chính xác dựa trên context
- Nếu không tìm thấy thông tin, nói rõ
- Trích dẫn nguồn khi có thể
- Trả lời bằng tiếng Việt rõ ràng, dễ hiểu"""
        },
        {
            "role": "user",
            "content": message
        }
    ]
    
    # 4. Gọi OpenAI GPT
    response = openai_client.chat.completions.create(
        model="GPT-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    answer = response.choices[0].message.content
```

#### Bước 6: Trả Về Kết Quả

```json
{
  "response": "Để tạo nhân viên mới trong hệ thống, bạn có thể thực hiện theo các cách sau:\n\n**1. Qua Giao Diện Web:**\n- Truy cập menu 'Employees'\n- Click nút 'Thêm mới'\n- Điền form với các thông tin bắt buộc: Họ tên, Email, Số điện thoại, Phòng ban, Chức vụ\n- Upload CV nếu có\n- Click 'Lưu'\n\n**2. Qua API:**\n```\nPOST /api/v1/employees\n{\n  \"fullName\": \"Nguyễn Văn A\",\n  \"email\": \"a.nguyen@company.com\",\n  \"phone\": \"0912345678\",\n  \"departmentId\": 1,\n  \"position\": \"Developer\",\n  \"hireDate\": \"2024-01-15\",\n  \"salary\": 15000000\n}\n```\n\n**Các trường bắt buộc:**\n- fullName (Họ tên)\n- email (Email hợp lệ)\n- phone (Số điện thoại)\n- departmentId (ID phòng ban)\n\n*Nguồn: API_DOCUMENTATION.md, USER_GUIDE.md*",
  
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  
  "sources": [
    {
      "content": "## API Endpoints...",
      "metadata": {
        "source": "./documents/employee_management_system/docs/API_DOCUMENTATION.md",
        "file_name": "API_DOCUMENTATION.md"
      },
      "score": 0.92,
      "rank": 1
    },
    {
      "content": "class Employee:...",
      "metadata": {
        "source": "./documents/employee_management_system/models/employee.py"
      },
      "score": 0.88,
      "rank": 2
    },
    {
      "content": "### Thêm Nhân Viên Mới...",
      "metadata": {
        "source": "./documents/employee_management_system/docs/USER_GUIDE.md"
      },
      "score": 0.85,
      "rank": 3
    }
  ],
  
  "metadata": {
    "model": "GPT-4o-mini",
    "tokens_used": 856,
    "retrieval_count": 3,
    "processing_time_ms": 1250
  }
}
```

## 🗄️ Cấu Trúc ChromaDB

### Collection Schema

```python
Collection: "documents"
├── Metadata
│   ├── name: "documents"
│   ├── description: "RAG documents collection"
│   └── created_at: "2024-10-30T10:30:00Z"
│
└── Documents (Chunks)
    ├── Document ID: "doc_0_abc123def456"
    │   ├── Embedding: [1536 dimensions float array]
    │   ├── Text: "Hệ thống quản lý nhân viên là..."
    │   └── Metadata:
    │       ├── source: "./documents/README.md"
    │       ├── file_type: ".md"
    │       ├── file_name: "README.md"
    │       ├── file_size: 5120
    │       └── chunk_index: 0
    │
    ├── Document ID: "doc_1_ghi789jkl012"
    │   ├── Embedding: [1536 dimensions]
    │   ├── Text: "## Đặc Trưng Chính..."
    │   └── Metadata: {...}
    │
    └── ... (nhiều documents khác)
```

### Ví Dụ Thực Tế

```json
{
  "id": "doc_42_a1b2c3d4e5f6",
  "embedding": [
    0.023145, -0.891234, 0.234567, 0.567890, -0.123456,
    0.789012, 0.345678, -0.901234, 0.456789, 0.012345,
    // ... 1526 số nữa (tổng 1536)
  ],
  "document": "POST /api/v1/employees\n\nTạo nhân viên mới trong hệ thống.\n\n**Request Body:**\n```json\n{\n  \"fullName\": \"string\",\n  \"email\": \"string\",\n  \"phone\": \"string\",\n  \"departmentId\": \"integer\",\n  \"position\": \"string\",\n  \"hireDate\": \"date\",\n  \"salary\": \"float\"\n}\n```\n\n**Response:** 201 Created",
  "metadata": {
    "source": "./documents/employee_management_system/docs/API_DOCUMENTATION.md",
    "file_type": ".md",
    "file_name": "API_DOCUMENTATION.md",
    "file_size": 15840,
    "chunk_index": 7
  }
}
```

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

## 🔍 Troubleshooting

### Vấn Đề Thường Gặp

#### 1. Documents không được load

**Triệu chứng:**
```
⚠️ No documents found to auto-load
```

**Nguyên nhân & Giải pháp:**
- Thư mục `./documents` trống → Thêm files
- File extension không được hỗ trợ → Kiểm tra `SUPPORTED_EXTENSIONS`
- File quá lớn → Tăng `MAX_FILE_SIZE_MB`

#### 2. Tìm kiếm không chính xác

**Triệu chứng:**
- Câu trả lời không liên quan
- Documents trả về score thấp

**Giải pháp:**
- Giảm `chunk_size` để tăng độ chi tiết
- Tăng `RETRIEVAL_K` để có nhiều context hơn
- Kiểm tra quality của documents (có đủ thông tin?)

#### 3. Response chậm

**Triệu chứng:**
- API timeout
- Latency cao

**Giải pháp:**
- Giảm `RETRIEVAL_K`
- Giảm `max_tokens` trong response
- Sử dụng cache cho queries phổ biến
- Scale horizontal với load balancer

#### 4. OpenAI API errors

**Triệu chứng:**
```
401 Unauthorized
429 Rate Limit Exceeded
500 Internal Server Error
```

**Giải pháp:**
- Kiểm tra `OPENAI_API_KEY`
- Thêm retry logic với exponential backoff
- Monitor usage quota
- Sử dụng fallback model

## 📚 Tài Liệu Tham Khảo

### Technologies

- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **ChromaDB**: https://docs.trychroma.com/
- **OpenAI API**: https://platform.openai.com/docs

### Papers & Concepts

- **RAG (Retrieval-Augmented Generation)**: 
  - Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
  
- **Vector Embeddings**:
  - Understanding semantic search and vector databases
  
- **Chunking Strategies**:
  - Optimal document segmentation for RAG systems

### Community

- **LangChain Discord**: Discussions about RAG patterns
- **ChromaDB Community**: Vector database optimization
- **OpenAI Forum**: API best practices

---

## 🚀 Kết Luận

RAG Chatbot API kết hợp sức mạnh của:

1. **Vector Search** (ChromaDB): Tìm kiếm ngữ nghĩa nhanh và chính xác
2. **Embeddings** (OpenAI): Chuyển đổi text thành vectors có ý nghĩa
3. **LLM** (GPT): Sinh câu trả lời tự nhiên dựa trên context
4. **Document Processing** (LangChain): Xử lý đa dạng định dạng files

Hệ thống này cho phép:
- ✅ Trả lời câu hỏi chính xác dựa trên documents
- ✅ Tự động cập nhật khi thêm tài liệu mới
- ✅ Scale tốt với lượng documents lớn
- ✅ Trích dẫn nguồn minh bạch
- ✅ Dễ dàng tích hợp vào ứng dụng

**Happy Coding! 🎉**