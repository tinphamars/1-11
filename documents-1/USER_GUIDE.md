# 🧭 USER_GUIDE.md — Hệ Thống Quản Lý Nhân Viên (Employee Management System)

---

## 1. Mục tiêu & Phạm vi

**Đối tượng người đọc:**
- 👩‍💼 **Nhân viên (Employee):** Dành cho người dùng muốn xem và cập nhật hồ sơ cá nhân.
- 👨‍💼 **HR Manager:** Dành cho người quản lý nhân sự, chịu trách nhiệm theo dõi và cập nhật thông tin nhân viên, phòng ban, báo cáo.
- 🧑‍💻 **Admin:** Dành cho người quản trị hệ thống, có toàn quyền cấu hình và quản lý tài khoản.

**Phạm vi tài liệu:**  
Tài liệu hướng dẫn chi tiết cách sử dụng hệ thống Employee Management System (EMS) bao gồm các thao tác từ đăng nhập, quản lý hồ sơ, xuất báo cáo cho đến bảo mật và xử lý sự cố.

---

## 2. Tổng quan hệ thống

Hệ thống EMS được thiết kế nhằm hỗ trợ doanh nghiệp trong việc quản lý nhân sự tập trung và hiệu quả.  
**Chức năng lõi:** Quản lý hồ sơ nhân viên, phòng ban, báo cáo và phân quyền.  
**Triết lý thiết kế:** “Trực quan – Chính xác – An toàn”.  
**Lợi ích:**  
- Giảm thiểu thao tác thủ công.  
- Tăng tốc độ truy xuất thông tin.  
- Hỗ trợ ra quyết định dựa trên dữ liệu.

---

## 3. Vai trò & Quyền hạn

| Chức năng | Admin | HR Manager | Employee |
|------------|:------:|:-----------:|:--------:|
| Xem danh sách nhân viên | ✅ | ✅ | ✅ |
| Thêm / chỉnh sửa hồ sơ | ✅ | ✅ | ❌ |
| Xóa hoặc vô hiệu hóa tài khoản | ✅ | ✅ (giới hạn) | ❌ |
| Tạo / chỉnh sửa phòng ban | ✅ | ✅ | ❌ |
| Xem / tạo báo cáo | ✅ | ✅ | ❌ |
| Quản lý phân quyền | ✅ | ❌ | ❌ |
| Upload / tải xuống tài liệu | ✅ | ✅ | ✅ |
| Gửi thông báo nội bộ | ✅ | ✅ | ✅ |
| Truy cập nhật ký hoạt động (Audit Log) | ✅ | ❌ | ❌ |

**Các hành động bị giới hạn:**
- Employee không thể chỉnh sửa thông tin người khác.  
- HR không được thay đổi cấu hình hệ thống.  
- Admin không chỉnh sửa thông tin cá nhân nhân viên nếu không có lý do hợp lệ.

---

## 4. Quy trình Onboarding

1. **Tạo tài khoản:**  
   - HR hoặc Admin tạo tài khoản mới cho nhân viên.  
2. **Đăng nhập lần đầu:**  
   - Người dùng cần đổi mật khẩu mặc định.  
   - Bật xác thực hai yếu tố (2FA) nếu hệ thống yêu cầu.  
3. **Thiết lập hồ sơ cá nhân:**  
   - Cập nhật thông tin cơ bản: họ tên, phòng ban, vị trí, liên hệ.

---

## 5. Giao diện & Điều hướng

### 5.1 Trang Dashboard  
Hiển thị tổng quan về số lượng nhân viên, phòng ban, thông báo và KPI.

### 5.2 Thanh menu chính  
- **Employees:** Quản lý nhân viên.  
- **Departments:** Quản lý phòng ban.  
- **Reports:** Tạo và xem báo cáo.  
- **Settings:** Cài đặt cá nhân hoặc hệ thống.

### 5.3 Tìm kiếm nhanh, bộ lọc và phân trang  
- **Search bar:** Tìm theo tên, ID, hoặc phòng ban.  
- **Filters:** Lọc theo trạng thái, vị trí, hoặc ngày gia nhập.  
- **Pagination:** Phân trang danh sách nhân viên dài.

---

## 6. Quản lý Nhân viên

- **Thêm nhân viên mới:**  
  - Điền các trường bắt buộc: Họ tên, Email, Phòng ban, Ngày vào làm.  
- **Chỉnh sửa hồ sơ:** HR và Admin có quyền cập nhật thông tin nhân viên.  
- **Upload tài liệu:**  
  - Định dạng hỗ trợ: `.pdf`, `.docx`, `.jpg`, `.png`.  
  - Dung lượng tối đa: **10MB/tệp**.  
- **Lịch sử thăng chức / điều chuyển:**  
  - Ghi nhận tự động khi cập nhật vị trí hoặc phòng ban.  
- **Xóa / Vô hiệu hóa tài khoản:**  
  - **Xóa:** Xóa vĩnh viễn dữ liệu.  
  - **Vô hiệu hóa:** Giữ dữ liệu nhưng không cho đăng nhập.

---

## 7. Quản lý Phòng ban

- **Tạo / Chỉnh sửa / Hợp nhất / Vô hiệu hóa** phòng ban.  
- **Gán trưởng phòng (Assign / Reassign):** Phân công người phụ trách.  
- **Báo cáo theo phòng ban:** Thống kê nhân sự, chi phí, năng suất.

---

## 8. Báo cáo & Thống kê

- **Loại báo cáo:** Nhân sự, Chi phí, Lương, Nghỉ việc.  
- **Bộ lọc thời gian:** Lựa chọn theo tháng, quý, năm.  
- **Xuất dữ liệu:**
  ```bash
  # Ví dụ xuất báo cáo nhân sự ra CSV
  export_report --type=employee --format=csv
