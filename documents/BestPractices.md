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