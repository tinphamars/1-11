# RAG Chatbot API

API chatbot thông minh sử dụng kỹ thuật **RAG (Retrieval-Augmented Generation)** để trả lời câu hỏi dựa trên tài liệu dự án một cách chính xác và hiệu quả.

## 🚀 Tính năng nổi bật
- 🧠 Tự động xử lý tài liệu từ thư mục `documents/`
- 💬 Chat tương tác với tài liệu để hỏi đáp về nội dung
- 📄 Hỗ trợ đa định dạng: `.py`, `.md`, `.txt`, `.json`, `.yml`, `.docx`, `.pdf`
- 🐳 Triển khai dễ dàng với Docker
- ⚡ Xử lý real-time với vector database

---

## ⚙️ Quick Start

### 1. Cấu hình môi trường
Tạo file `.env` trong thư mục gốc:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.l
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_TYPE=openai

# Application Settings
DOCUMENTS_FOLDER=./documents
AUTO_LOAD_ON_STARTUP=true
RETRIEVAL_K=5
DEFAULT_TEMPERATURE=0.7
```

### 2. Chạy với Docker
```bash
docker compose up -d --build
```

### 3. Kiểm tra hoạt động
Truy cập: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💬 Sử dụng API

### Chat với tài liệu
```bash
POST http://localhost:8000/chat

{
  "message": "Làm thế nào để cài đặt dự án này?",
  "temperature": 0.7
}
```

### Làm mới tài liệu
Khi thêm/sửa file trong `documents/`:

```bash
POST http://localhost:8000/documents/refresh
```

---

## 📡 API Endpoints

| Method | Endpoint | Mô tả |
|--------|-----------|-------|
| GET | `/` | Thông tin API |
| GET | `/health` | Kiểm tra trạng thái hệ thống |
| POST | `/chat` | Chat với tài liệu |
| POST | `/documents/refresh` | Làm mới tài liệu |
| GET | `/documents/status` | Xem trạng thái database |
| GET | `/documents/folder-info` | Xem thông tin folder |
| DELETE | `/documents/clear` | Xóa tất cả tài liệu |

Tài liệu API đầy đủ: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Cấu hình chi tiết

### Cài đặt OpenAI
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.l
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_TYPE=openai
```

### Tùy chỉnh ứng dụng
```env
# Đường dẫn thư mục tài liệu
DOCUMENTS_FOLDER=./documents

# Tự động tải khi khởi động
AUTO_LOAD_ON_STARTUP=true

# Số lượng tài liệu liên quan tìm kiếm
RETRIEVAL_K=5

# Độ sáng tạo của model (0.0 - 1.0)
DEFAULT_TEMPERATURE=0.7
```

---

## 🧩 Xử lý sự cố

### Lỗi kết nối thường gặp

| Lỗi | Giải pháp |
|------|------------|
| API Key sai | Kiểm tra `OPENAI_API_KEY` |
| URL không đúng | Xác nhận `OPENAI_BASE_URL` |
| Network issues | Kiểm tra kết nối mạng đến endpoint |

### Kiểm tra logs
```bash
# Xem logs real-time
docker compose logs -f rag-chatbot-api

# Xem logs với timestamps
docker compose logs -t rag-chatbot-api
```

---

## 🗂️ Cấu trúc project
```text
AI_ab/
├── app/                  # Code chính của ứng dụng
├── documents/            # Thư mục chứa tài liệu
├── chroma_db/            # Vector database (tự động tạo)
├── .env                  # File cấu hình (cần tạo thủ công)
├── docker-compose.yml    # Docker compose configuration
└── Dockerfile            # Docker image build file
```

---

## ⚠️ Lưu ý quan trọng
- Tài liệu được lưu trữ trong **ChromaDB vector database**
- Lịch sử chat được lưu trong **memory** (sẽ mất khi restart service)
- Để sử dụng trong môi trường **production**, nên thay thế memory storage bằng **database thật**
- Khuyến nghị **backup dữ liệu quan trọng** trong thư mục `documents/`
