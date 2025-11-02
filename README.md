# RAG Chatbot API

API chatbot sử dụng RAG để trả lời câu hỏi dựa trên tài liệu của dự án.

## Tính năng

- Tự động xử lý tài liệu từ thư mục `documents/`
- Chat với tài liệu để hỏi đáp về nội dung
- Hỗ trợ nhiều định dạng: `.py`, `.md`, `.txt`, `.json`, `.yml`, `.docx`, `.pdf`
- Chạy dễ dàng với Docker

## Cài đặt

### 1. Tạo file `.env`

Tạo file `.env` trong thư mục gốc với nội dung:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.l
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_TYPE=openai
```

**Lưu ý:**
- `OPENAI_BASE_URL`: URL endpoint của bạn (nếu dùng custom endpoint)
- `OPENAI_MODEL`: Tên model hoặc deployment name
- `OPENAI_API_TYPE`: `openai` (cho custom endpoint) hoặc `azure` (cho Azure OpenAI)

### 2. Chạy với Docker

```bash
docker compose up -d --build
```

### 3. Kiểm tra

Mở trình duyệt: http://localhost:8000/docs

## Sử dụng

### Thêm tài liệu

Đặt các file vào thư mục `documents/`. API sẽ tự động xử lý khi khởi động.

### Chat với tài liệu

```bash
POST http://localhost:8000/chat

{
  "message": "Làm thế nào để cài đặt dự án này?"
}
```

### Làm mới tài liệu

Nếu bạn thêm/sửa file trong `documents/`:

```bash
POST http://localhost:8000/documents/refresh
```

## API Endpoints

- `GET /` - Thông tin API
- `GET /health` - Kiểm tra trạng thái
- `POST /chat` - Chat với tài liệu
- `POST /documents/refresh` - Làm mới tài liệu
- `GET /documents/status` - Xem trạng thái database
- `GET /documents/folder-info` - Xem thông tin folder
- `DELETE /documents/clear` - Xóa tất cả tài liệu

Tài liệu API đầy đủ: http://localhost:8000/docs

## Cấu hình (tùy chọn)

Thêm vào file `.env` nếu muốn tùy chỉnh:

```env
# Thư mục tài liệu
DOCUMENTS_FOLDER=./documents

# Tự động tải khi khởi động
AUTO_LOAD_ON_STARTUP=true

# Số lượng tài liệu liên quan lấy về
RETRIEVAL_K=5

# Nhiệt độ mặc định
DEFAULT_TEMPERATURE=0.7
```

## Xử lý lỗi

### Lỗi kết nối

- Kiểm tra `OPENAI_API_KEY` đã đúng chưa
- Kiểm tra `OPENAI_BASE_URL` đã đúng chưa
- Kiểm tra network có truy cập được endpoint không

### Xem logs

```bash
docker compose logs -f rag-chatbot-api
```

## Cấu trúc project

```
AI_ab/
├── app/                  # Code chính
├── documents/            # Thư mục tài liệu
├── chroma_db/            # Database (tự động tạo)
├── .env                  # File cấu hình (cần tạo)
├── docker-compose.yml
└── Dockerfile
```

## Lưu ý

- Tài liệu được lưu trong ChromaDB vector database
- Lịch sử chat lưu trong memory (sẽ mất khi restart)
- Để production, nên thay memory storage bằng database
