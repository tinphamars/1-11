# API_DOCUMENTATION - Employee Management System

---

## 1. Tổng quan
Hệ thống quản lý nhân sự (EMS) cho phép quản lý nhân viên, phòng ban, và báo cáo.  
- Protocol: **HTTPS / JSON**  
- Response chuẩn: `application/json`  
- Auth: JWT Bearer Token  

---

## 2. Base URLs
| Environment | URL |
|-------------|-----|
| Local       | `http://localhost:3000/api` |
| Staging     | `https://staging.ems.example.com/api` |
| Production  | `https://ems.example.com/api` |

---

## 3. Auth
- **Login**: `POST /auth/login` → nhận `access_token` + `refresh_token`  
- **Refresh**: `POST /auth/refresh` → nhận token mới  
- **Logout**: `POST /auth/logout` → invalidate token  

**Header mẫu:**  
```http
Authorization: Bearer <access_token>
