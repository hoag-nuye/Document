from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Multi-Tenant Test")

@app.get("/")
def read_root():
    return {
        "message": "Simple Multi-Tenant Test Server",
        "endpoints": [
            "/nguyennh5/mcp",
            "/nguyennh6/mcp"
        ]
    }

@app.get("/nguyennh5/mcp")
def nguyennh5_mcp():
    return {
        "user": "nguyennh5",
        "database": "user_management_test_nguyennh5",
        "message": "MCP endpoint for nguyennh5"
    }

@app.get("/nguyennh6/mcp")
def nguyennh6_mcp():
    return {
        "user": "nguyennh6", 
        "database": "user_management_test_nguyennh6",
        "message": "MCP endpoint for nguyennh6"
    }

@app.get("/users")
def get_users():
    return {
        "users": [
            {
                "username": "nguyennh5",
                "endpoint": "/nguyennh5/mcp"
            },
            {
                "username": "nguyennh6",
                "endpoint": "/nguyennh6/mcp"
            }
        ]
    }

if __name__ == "__main__":
    print("Starting simple multi-tenant test server...")
    uvicorn.run(app, host="127.0.0.1", port=8000) 