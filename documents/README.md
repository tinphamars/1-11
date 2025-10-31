# 🧑‍💼 Hệ Thống Quản Lý Nhân Viên (Employee Management System)

Hệ thống giúp doanh nghiệp quản lý toàn diện thông tin nhân sự, phòng ban, báo cáo và phân quyền người dùng.  
Cung cấp giao diện hiện đại, thân thiện và dễ mở rộng cho tổ chức từ nhỏ đến lớn.

---

## ⚙️ Đặc Trưng Chính

### 🏢 Quản lý phòng ban
- Tạo, sửa, xóa và phân loại phòng ban.  
- Gắn nhân viên vào từng phòng.  
- Theo dõi tổng số nhân viên và vai trò trong mỗi phòng ban.

### 👥 Quản lý nhân viên
- Lưu trữ **thông tin cá nhân** (họ tên, ngày sinh, liên hệ, địa chỉ).  
- Quản lý **thông tin công việc** (chức vụ, lương, ngày vào làm, hợp đồng).  
- Lưu lại **lịch sử công tác** và thay đổi chức vụ.  
- Quản lý **tài liệu nhân sự** (CV, hợp đồng, chứng chỉ, đánh giá hiệu suất).

### 📊 Báo cáo & Thống kê
- Thống kê nhân sự theo phòng ban, giới tính, độ tuổi, thâm niên.  
- Báo cáo biến động nhân sự theo tháng/quý/năm.  
- Phân tích hiệu suất làm việc, tỷ lệ nghỉ việc.  
- Xuất báo cáo dưới dạng **PDF**, **Excel**.

### 🔐 Bảo mật & Phân quyền
- Xác thực bằng **JWT** (Access + Refresh Token).  
- **RBAC** (Role-Based Access Control) phân quyền theo vai trò.  
- **Audit log** ghi lại hoạt động người dùng.  
- Mã hóa mật khẩu bằng **bcrypt**.  
- Hạn chế tốc độ truy cập (**Rate Limiting**) và bảo vệ API.

---

## 🧰 Công Nghệ Sử Dụng

**Backend:**
- FastAPI  
- SQLAlchemy  
- PostgreSQL  
- Redis  
- Celery

**Frontend:**
- React.js  
- Material-UI  
- Redux Toolkit  
- Axios

**DevOps:**
- Docker  
- Docker Compose  
- Nginx  
- GitHub Actions

---

## 🖥️ Yêu Cầu Hệ Thống

- Python ≥ 3.10  
- Node.js ≥ 18  
- PostgreSQL ≥ 14  
- Docker ≥ 24  
- Docker Compose ≥ 2.15

---

## 🐳 Hướng Dẫn Cài Đặt Bằng Docker

```bash
# 1. Clone dự án
git clone https://github.com/your-org/employee-management-system.git
cd employee-management-system

# 2. Tạo file môi trường
cp .env.example .env

# 3. Khởi chạy Docker Compose
docker compose up -d

# 4. Truy cập ứng dụng
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
