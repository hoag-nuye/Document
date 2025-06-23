# Multi-Tenant MCP Server với Authentication

Hệ thống MCP server hỗ trợ multi-tenant với authentication và authorization, cho phép mỗi người dùng có các tool riêng biệt và database riêng trên cùng một port.

## Tính năng

- **Multi-tenant**: Mỗi user có MCP server riêng tại endpoint `/username/mcp`
- **Single port**: Tất cả users sử dụng chung một port (8000)
- **Authentication**: Hệ thống đăng ký/đăng nhập với JWT token
- **Authorization**: Mỗi user chỉ có thể truy cập MCP của chính mình
- **Database isolation**: Mỗi user có database riêng biệt
- **Tool isolation**: Mỗi user có các tool riêng, không ảnh hưởng lẫn nhau
- **Dynamic registration**: Có thể đăng ký user mới trong runtime
- **Path-based routing**: Sử dụng URL path để phân biệt users

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Tạo file `.env` với thông tin MySQL và JWT secret:
```env
MYSQL_PASSWORD=your_mysql_password
JWT_SECRET=your-super-secret-jwt-key-change-this
```

3. Chạy server:
```bash
python server.py
```

## Cấu trúc URL

- **Root**: `http://localhost:8000/` - Thông tin server và endpoints
- **User MCP**: `http://localhost:8000/{username}/mcp` - MCP server cho user cụ thể (cần authentication)
- **API endpoints**:
  - `POST /register` - Đăng ký user mới
  - `POST /login` - Đăng nhập
  - `GET /me` - Thông tin user hiện tại (cần authentication)
  - `GET /users` - Danh sách users (admin only, cần authentication)

## Luồng hoạt động

### 1. Đăng ký User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "User newuser registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "endpoint": "http://127.0.0.1:8000/newuser/mcp",
  "database": "user_management_test_newuser"
}
```

### 2. Đăng nhập User
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "username": "newuser",
    "email": "newuser@example.com",
    "role": "user",
    "database": "user_management_test_newuser"
  }
}
```

## Tích hợp với AI Agent

### Cách 1: Sử dụng JWT Token trong Header

Khi AI Agent kết nối đến MCP server, cần thêm JWT token vào Authorization header:

```python
import requests

# Đăng nhập để lấy token
login_response = requests.post("http://localhost:8000/login", json={
    "username": "newuser",
    "password": "password123"
})

token = login_response.json()["access_token"]

# Kết nối MCP với token
headers = {
    "Authorization": f"Bearer {token}"
}

# Tất cả requests đến MCP endpoint phải có header này
mcp_response = requests.post(
    "http://localhost:8000/newuser/mcp",
    headers=headers,
    json={"method": "tools/list"}
)
```

### Cách 2: Cấu hình MCP Client với Authentication

Cập nhật file `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mysql-user-management-newuser": {
      "url": "http://localhost:8000/newuser/mcp",
      "name": "MySQL User Management - newuser",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
      }
    }
  }
}
```

**Lưu ý:** Token có thời hạn 7 ngày, cần cập nhật khi hết hạn.

### Cách 3: Tự động hóa với Script

Tạo script để tự động đăng nhập và cập nhật MCP config:

```python
#!/usr/bin/env python3
import requests
import json
import os

def login_and_update_mcp_config(username, password):
    # Đăng nhập
    response = requests.post("http://localhost:8000/login", json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        
        # Cập nhật MCP config
        mcp_config = {
            "mcpServers": {
                f"mysql-user-management-{username}": {
                    "url": f"http://localhost:8000/{username}/mcp",
                    "name": f"MySQL User Management - {username}",
                    "transport": "streamable-http",
                    "headers": {
                        "Authorization": f"Bearer {token}"
                    }
                }
            }
        }
        
        # Lưu vào file
        config_path = os.path.expanduser("~/.cursor/mcp.json")
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"MCP config updated for user {username}")
        return True
    else:
        print("Login failed")
        return False

# Sử dụng
login_and_update_mcp_config("newuser", "password123")
```

## Tools có sẵn

Mỗi user sẽ có các tool sau:

### 1. `add_user`
Thêm user mới vào database
```python
add_user(name: str, email: str, role: str) -> dict
```

### 2. `update_user` 
Cập nhật thông tin user
```python
update_user(user_id: int, name: str, email: str, role: str, password: str = "") -> dict
```

### 3. `delete_user`
Xóa user khỏi database
```python
delete_user(user_id: int) -> dict
```

### 4. `search_users_by_name`
Tìm kiếm user theo tên
```python
search_users_by_name(name: str) -> List[dict]
```

### 5. `search_users_by_column`
Tìm kiếm user theo cột (id, email, name, role, password)
```python
search_users_by_column(column_name: UserColumn, value: str) -> List[dict]
```

### 6. `get_all_users`
Lấy tất cả users từ database
```python
get_all_users() -> List[dict]
```

### 7. `get_user_info`
Lấy thông tin user hiện tại
```python
get_user_info() -> dict
```

## Ví dụ sử dụng

### 1. Kết nối MCP client

Trong Cursor, MCP client sẽ tự động kết nối đến endpoint của user:
- `http://localhost:8000/nguyennh5/mcp` cho user nguyennh5
- `http://localhost:8000/nguyennh6/mcp` cho user nguyennh6

**Lưu ý:** Cần có JWT token hợp lệ trong Authorization header.

### 2. Sử dụng tools

Mỗi user sẽ thấy các tool riêng của mình và có thể sử dụng chúng để quản lý database riêng.

### 3. Database isolation

- User `nguyennh5` sử dụng database `user_management_test_nguyennh5`
- User `nguyennh6` sử dụng database `user_management_test_nguyennh6`

## Kiến trúc

```
Multi-Tenant MCP Server (Port 8000)
├── FastAPI App với Authentication
│   ├── / - Root endpoint
│   ├── /register - Đăng ký user
│   ├── /login - Đăng nhập
│   ├── /me - Thông tin user (protected)
│   ├── /users - Danh sách users (admin only)
│   ├── /nguyennh5/mcp - MCP server cho nguyennh5 (protected)
│   │   ├── Database: user_management_test_nguyennh5
│   │   └── Tools: add_user, update_user, delete_user, ...
│   └── /nguyennh6/mcp - MCP server cho nguyennh6 (protected)
│       ├── Database: user_management_test_nguyennh6
│       └── Tools: add_user, update_user, delete_user, ...
```

## Bảo mật

### 1. Authentication
- JWT token có thời hạn 7 ngày
- Password được hash bằng SHA-256
- Token chứa username để verify quyền truy cập

### 2. Authorization
- Mỗi user chỉ có thể truy cập MCP của chính mình
- Middleware kiểm tra token và user ownership
- Trả về 401/403 nếu không có quyền

### 3. Database Isolation
- Mỗi user có database riêng biệt
- Không có quyền truy cập chéo giữa users
- Các tool chỉ hoạt động trên database của user tương ứng

## Testing

Chạy test script để kiểm tra hệ thống:

```bash
python test_auth.py
```

Test script sẽ kiểm tra:
- Server running
- User registration
- User login
- Token validation
- MCP access
- Unauthorized access blocking
- Wrong user access blocking

## Troubleshooting

1. **Lỗi kết nối MySQL**: Kiểm tra file `.env` và thông tin MySQL
2. **Token expired**: Đăng nhập lại để lấy token mới
3. **Access denied**: Kiểm tra token có đúng user không
4. **User not found**: Đăng ký user trước khi sử dụng
5. **Port đã được sử dụng**: Kiểm tra xem port 8000 có đang được sử dụng bởi ứng dụng khác không

## Phát triển

Để thêm tool mới cho tất cả users, chỉnh sửa method `_init_tools()` trong class `UserMCPServer`.

## Quản lý Users

### Xem thông tin user hiện tại
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/me
```

### Đăng ký user mới
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

Server sẽ tự động:
- Tạo database cho user mới
- Khởi tạo MCP server cho user tại `/newuser/mcp`
- Tạo JWT token cho user
- Trả về thông tin endpoint và token

## Ưu điểm của hệ thống

1. **Bảo mật cao**: Authentication và authorization đầy đủ
2. **Hiệu quả**: Chỉ cần một port duy nhất cho tất cả users
3. **Đơn giản**: Dễ dàng quản lý và cấu hình
4. **Scalable**: Có thể thêm nhiều users mà không cần thêm port
5. **Resource-friendly**: Tiết kiệm tài nguyên hệ thống
6. **Standard**: Tuân theo chuẩn HTTP routing và JWT