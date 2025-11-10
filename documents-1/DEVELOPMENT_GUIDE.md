# 🚀 DEPLOYMENT_GUIDE.md  
**Tài liệu triển khai cho [PROJECT_NAME]**

---

## 1. Kiến trúc tổng quan
Hệ thống **[PROJECT_NAME]** được xây dựng theo kiến trúc **microservices**, gồm các thành phần chính:  
- **Frontend:** Next.js / Angular.  
- **Backend API:** Node.js (Express/NestJS).  
- **Database:** PostgreSQL.  
- **Cache:** Redis.  
- **Message Queue:** RabbitMQ (nếu áp dụng).  
- **Storage:** AWS S3 hoặc tương đương.  
- **CI/CD:** GitHub Actions / GitLab CI / Jenkins.  

Mục tiêu là **triển khai linh hoạt, dễ mở rộng, an toàn và tự động hóa**.

---

## 2. Môi trường
| Môi trường | URL / Domain | Mục đích | Ghi chú |
|-------------|--------------|-----------|---------|
| **Local** | localhost:3000 | Phát triển | Sử dụng Docker Compose |
| **Staging** | staging.[project].com | Kiểm thử nội bộ | Kết nối API giả hoặc thật |
| **Production** | [project].com | Triển khai chính thức | Có load balancer, auto scaling |

---

## 3. Prerequisites
Trước khi triển khai, đảm bảo:
- Node.js >= 18  
- Docker & Docker Compose  
- Kubernetes CLI (`kubectl`)  
- Helm (nếu dùng chart)  
- Quyền truy cập CI/CD repository  
- Tệp `.env` hợp lệ cho từng môi trường  

---

## 4. Build & Release
### Build local
```bash
npm install
npm run build
