# Hướng dẫn tích hợp MCP Server với AI Agent

## Tổng quan

Hệ thống MCP server đã được bảo mật với authentication và authorization. Mỗi user chỉ có thể truy cập MCP server của chính mình thông qua JWT token.

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
# Ví dụ với Python
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

## Bảo mật

### 1. Token Security
- JWT token có thời hạn 7 ngày
- Token chứa username để verify quyền truy cập
- Mỗi user chỉ có thể truy cập MCP của chính mình

### 2. Middleware Protection
- Tất cả requests đến `/username/mcp` đều được verify
- Kiểm tra token validity và user ownership
- Trả về 401/403 nếu không có quyền

### 3. Database Isolation
- Mỗi user có database riêng biệt
- Không có quyền truy cập chéo giữa users

## API Endpoints

### Public Endpoints
- `POST /register` - Đăng ký user mới
- `POST /login` - Đăng nhập
- `GET /` - Thông tin server

### Protected Endpoints
- `GET /me` - Thông tin user hiện tại
- `GET /users` - Danh sách users (admin only)
- `/{username}/mcp` - MCP server (cần token của user đó)

## Troubleshooting

### 1. Token Expired
```bash
# Đăng nhập lại để lấy token mới
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

### 2. Access Denied
- Kiểm tra token có đúng user không
- Đảm bảo token chưa hết hạn
- Verify username trong URL path

### 3. User Not Found
- Đăng ký user trước khi sử dụng
- Kiểm tra user đã được khởi tạo MCP server chưa

## Ví dụ hoàn chỉnh

### 1. Đăng ký và sử dụng MCP
```bash
# 1. Đăng ký user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# 2. Lấy token từ response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# 3. Sử dụng MCP với token
curl -X POST "http://localhost:8000/testuser/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

### 2. Tích hợp với AI Agent
```python
import requests

class SecureMCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def call_mcp(self, username, method, params=None):
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/{username}/mcp",
            headers=headers,
            json={"method": method, "params": params or {}}
        )
        return response.json()

# Sử dụng
client = SecureMCPClient()
if client.login("testuser", "password123"):
    result = client.call_mcp("testuser", "tools/list")
    print(result)
```

## Lưu ý quan trọng

1. **Token Management**: Luôn lưu trữ token an toàn
2. **Token Refresh**: Tự động refresh token khi gần hết hạn
3. **Error Handling**: Xử lý lỗi 401/403 một cách graceful
4. **Logging**: Log các hoạt động authentication để audit
5. **Rate Limiting**: Cân nhắc thêm rate limiting cho login/register 