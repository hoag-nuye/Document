# region CONFIGURATION
from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Dict
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
from enum import Enum as PyEnum
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import json
import asyncio

# Load environment variables
load_dotenv()
MYSQL_USER_DB = os.getenv('MYSQL_USER_DB', 'user_management')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_password')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')

# Global dictionary to store user MCP servers
user_mcp_servers: Dict[str, 'UserMCPServer'] = {}

# Create FastAPI app
app = FastAPI(title="Multi-User MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# endregion

# region Pydantic MODELS (SERVER API)
class AddUserRequest(BaseModel):
    username: str
    database: str

class AddUserResponse(BaseModel):
    status: str
    message: str
    endpoint: str

class DeleteUserRequest(BaseModel):
    username: str

class DeleteUserResponse(BaseModel):
    status: str
    message: str

class UserInfo(BaseModel):
    username: str
    database: str
    endpoint: str

class GetUsersResponse(BaseModel):
    status: str
    users: list[UserInfo]
# endregion

# region USER MCP SERVER CLASS (USER MCP SERVERS)

class TenantColumn(PyEnum):
    id = "id"
    tenant_name = "tenant_name"
    database_name = "database_name"
    database_infor_table = "database_info"

class UserColumn(PyEnum):
    id = "id"
    email = "email"
    username = "username"
    role = "role"
    password = "password"

class UserMCPServer:
    def __init__(self, username: str, database: str):
        self.username = username
        self.database = database
        
        # Create FastMCP server for this user
        self.mcp = FastMCP(
            f"MySQL User Management - {username}",
            stateless_http=True, 
        )
        
        # Initialize tools for this user
        self._init_tools()
        # Build tool_map: name -> function thực sự
        self.tool_map = {}
        tool_registry = getattr(self.mcp._tool_manager, "_tools", {})
        for name, tool_obj in tool_registry.items():
            if hasattr(tool_obj, "fn") and callable(tool_obj.fn):
                self.tool_map[name] = tool_obj.fn
        # print("self.mcp:", self.mcp)
        # print("dir(self.mcp):", dir(self.mcp))
        # print("self.mcp._tools:", getattr(self.mcp, '_tools', None))
        # print("self.mcp.tools:", getattr(self.mcp, 'tools', None))
        # print("dir(self.mcp._tool_manager):", dir(self.mcp._tool_manager))
        # print("self.mcp._tool_manager.__dict__:", self.mcp._tool_manager.__dict__)
    def get_db_connection(self):
        """Get database connection for this specific user"""
        try:
            connection = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=self.database
            )
            
            if connection.is_connected():
                print(f"Connection to MySQL database {self.database} was successful!")
                return connection
                
        except Error as e:
            print(f"Error while connecting to MySQL for user {self.username}:", e)
            return None
    
    def init_db(self):
        """Initialize database for this user"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(100) NOT NULL,
                password VARCHAR(255)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database initialized for user {self.username}")
    
    def _init_tools(self):
        """Initialize all tools for this user"""
        
        @self.mcp.tool()
        def add_user(name: str, email: str, role: str) -> dict: # noqa: F401
            """Add a new user to the database"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)",
                    (name, email, role)
                )
                conn.commit()
                user_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return {"status": "success", "message": f"User added with ID: {user_id}"}
            except mysql.connector.Error as err:
                return {"status": "error", "message": str(err)}

        @self.mcp.tool()
        def update_user(user_id: int, name: str, email: str, role: str, password: str = "") -> dict: # noqa: F401
            """Update an existing user's information"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                if password:
                    cursor.execute(
                        "UPDATE users SET name = %s, email = %s, role = %s, password = %s WHERE id = %s",
                        (name, email, role, password, user_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s",
                        (name, email, role, user_id)
                    )
                conn.commit()
                cursor.close()
                conn.close()
                return {"status": "success", "message": f"User {user_id} updated successfully"}
            except mysql.connector.Error as err:
                return {"status": "error", "message": str(err)}

        @self.mcp.tool()
        def delete_user(user_id: int) -> dict:
            """Delete a user from the database"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return {"status": "success", "message": f"User {user_id} deleted successfully"}
            except mysql.connector.Error as err:
                return {"status": "error", "message": str(err)}

        @self.mcp.tool()
        def search_users_by_name(name: str) -> List[dict]:
            """Search for users by name"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM users WHERE name LIKE %s",
                    (f"%{name}%",)
                )
                users = cursor.fetchall()
                cursor.close()
                conn.close()
                return users
            except mysql.connector.Error as err:
                return [{"status": "error", "message": str(err)}]

        @self.mcp.tool()
        def search_users_by_column(column_name: UserColumn, value: str) -> List[dict]:
            """Search for users by any column"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    f"SELECT * FROM users WHERE {column_name.value} LIKE %s",
                    (f"%{value}%",)
                )
                users = cursor.fetchall()
                cursor.close()
                conn.close()
                return users
            except mysql.connector.Error as err:
                return [{"status": "error", "message": str(err)}]

        @self.mcp.tool()
        def get_all_users() -> List[dict]:
            """Get all users from the database"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users")
                users = cursor.fetchall()
                cursor.close()
                conn.close()
                return users
            except mysql.connector.Error as err:
                return [{"status": "error", "message": str(err)}]

        @self.mcp.tool()
        def get_user_info() -> dict:
            """Get information about the current MCP server user"""
            return {
                "username": self.username,
                "database": self.database,
                "endpoint": f"http://127.0.0.1:8001/{self.username}/mcp"
            }
        # print("All attributes of self.mcp:", dir(self.mcp))

# endregion

# region DATABASE UTILS (USER MCP SERVERS)
def create_user_database(database_name: str):
    """Create a new database for a user"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database {database_name} created successfully!")
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"Error creating database {database_name}:", e)
        return False

def initialize_user_server(username: str, database: str):
    """Initialize MCP server for a specific user"""
    try:
        # Create database if it doesn't exist
        create_user_database(database)
        
        # Create user MCP server
        user_server = UserMCPServer(username, database)
        
        # IMPORTANT: Initialize FastMCP session manager and tool registry
        user_server.mcp.streamable_http_app()
        
        # Initialize database tables
        user_server.init_db()
        
        # Store in global dictionary
        user_mcp_servers[username] = user_server
        
        print(f"MCP server initialized for user: {username}")
        return True
        
    except Exception as e:
        print(f"Error initializing MCP server for user {username}:", e)
        return False

# endregion

# region FASTAPI ENDPOINTS (SERVER)
@app.get("/")
def read_root():
    """Root endpoint showing available users"""
    return {
        "message": "Multi-User MCP Server",
        "available_users": list(user_mcp_servers.keys()),
        "endpoints": {
            "user_mcp": "/{username}/mcp",
            "add_user": "/add_user",
            "list_users": "/users"
        }
    }

@app.get("/users", response_model=GetUsersResponse)
def get_users():
    return GetUsersResponse(
        status="success",
        users=[
            UserInfo(
                username=username,
                database=server.database,
                endpoint=f"http://127.0.0.1:8001/{username}/mcp"
            )
            for username, server in user_mcp_servers.items()
        ]
    )

@app.post("/add_user", response_model=AddUserResponse)
async def add_user_endpoint(req: AddUserRequest):
    username = req.username
    database = req.database
    if not username or not database:
        raise HTTPException(status_code=400, detail="Missing username or database")
    if username in user_mcp_servers:
        raise HTTPException(status_code=400, detail=f"User {username} already exists")
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_USER_DB
        )
        cursor = connection.cursor()
        table = TenantColumn.database_infor_table.value 
        col1 = TenantColumn.tenant_name.value
        col2 = TenantColumn.database_name.value
        cursor.execute(
            f"INSERT INTO {table} ({col1}, {col2}) VALUES (%s, %s)",
            (username, database)
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user to user_servers DB: {e}")
    success = initialize_user_server(username, database)
    if success:
        create_proxy_endpoint(username, user_mcp_servers[username])
        return AddUserResponse(
            status="success",
            message=f"User {username} added successfully",
            endpoint=f"http://127.0.0.1:8001/{username}/mcp"
        )
    else:
        raise HTTPException(status_code=500, detail=f"Failed to initialize user {username}")

@app.post("/delete_user", response_model=DeleteUserResponse)
async def delete_user_endpoint(req: DeleteUserRequest):
    username = req.username
    if username not in user_mcp_servers:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    database = user_mcp_servers[username].database
    try:
        # Xóa khỏi bảng user_servers
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_USER_DB
        )
        cursor = connection.cursor()
        table = TenantColumn.database_infor_table.value 
        col1 = TenantColumn.tenant_name.value
        col2 = TenantColumn.database_name.value
        cursor.execute(
            f"DELETE FROM {table} WHERE {col1} = %s",
            (username,)
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        pass  # Có thể log lỗi nếu cần
    try:
        # Xóa database user
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {database}")
            cursor.close()
            connection.close()
    except Exception as e:
        pass

    # Remove proxy endpoints first
    remove_proxy_endpoint(username)
    
    # Then remove user from memory
    del user_mcp_servers[username]

    return DeleteUserResponse(status="success", message=f"User {username} and database {database} deleted (if existed)")

# endregion

# region MCP PROXY HANDLERS (USER MCP SERVERS)
def create_proxy_endpoint(username: str, user_server):
    """Create proxy endpoints for FastMCP that properly handle MCP protocol"""
    
    @app.get(f"/{username}/mcp")
    async def mcp_get_proxy(request: Request):
        """Handle GET requests for SSE stream according to MCP protocol"""
        # Check if client accepts SSE
        accept_header = request.headers.get("accept", "")
        if "text/event-stream" not in accept_header:
            raise HTTPException(status_code=405, detail="Method Not Allowed - SSE not supported")
        
        # Create SSE stream for the user's MCP server
        async def generate_sse():
            try:
                # Get the SSE app from FastMCP
                sse_app = user_server.mcp.streamable_http_app()
                
                # Create a mock request for the SSE app
                scope = {
                    "type": "http",
                    "method": "GET",
                    "path": "/",
                    "headers": [(b"accept", b"text/event-stream")],
                    "query_string": b""
                }
                
                # This is a simplified approach - in practice, you'd need to properly
                # integrate the SSE app with FastAPI
                yield f"data: {json.dumps({'type': 'connected', 'user': username})}\n\n"
                
                # Keep connection alive
                while True:
                    await asyncio.sleep(1)
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    @app.post(f"/{username}/mcp")
    async def mcp_post_proxy(request: Request):
        """Handle POST requests for JSON-RPC messages according to MCP protocol"""
        try:
            # Check if client accepts JSON
            accept_header = request.headers.get("accept", "")
            if "application/json" not in accept_header and "text/event-stream" not in accept_header:
                raise HTTPException(status_code=400, detail="Accept header must include application/json or text/event-stream")
            
            body = await request.json()
            
            # Handle different types of JSON-RPC messages
            if isinstance(body, list):
                # Batch request
                responses = []
                for message in body:
                    response = await handle_mcp_message(user_server, message)
                    if response:
                        responses.append(response)
                
                if not responses:
                    # Only notifications/responses - return 202 Accepted
                    return JSONResponse(status_code=202, content=None)
                else:
                    # Contains requests - return responses
                    return JSONResponse(content=responses[0] if len(responses) == 1 else responses)
            else:
                # Single message
                response = await handle_mcp_message(user_server, body)
                if response is None:
                    # Notification - return 202 Accepted
                    return JSONResponse(status_code=202, content=None)
                else:
                    # Request - return response
                    return JSONResponse(content=response)
                    
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": None
                }
            )

def remove_proxy_endpoint(username: str):
    """Dynamically removes the MCP proxy endpoints for a given user."""
    routes_to_remove = [
        route for route in app.routes
        if hasattr(route, 'path') and route.path == f"/{username}/mcp"
    ]
    if routes_to_remove:
        for route in routes_to_remove:
            app.routes.remove(route)
        logging.info(f"Removed MCP proxy endpoints for user: {username}")
    else:
        logging.warning(f"No MCP proxy endpoints found for user: {username}")

async def handle_mcp_message(user_server, message):
    logger = logging.getLogger("mcp-proxy")
    if not isinstance(message, dict):
        logger.error(f"Invalid message type: {type(message)}")
        return None
    
    method = message.get("method")
    params = message.get("params", {})
    msg_id = message.get("id")
    logger.info(f"Received method: {method}, params: {params}, id: {msg_id}")
    
    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": f"MySQL User Management - {user_server.username}",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            tools = []
            # Chỉ lấy các tool đã đăng ký (ưu tiên _tools)

            tool_list = await user_server.mcp.list_tools()
            for tool in tool_list:
                if hasattr(tool, "__mcp_tool_info__"):
                    tools.append(tool.__mcp_tool_info__)
                else:
                     # Ưu tiên lấy tên từ .name, nếu không có thì lấy class name
                    tool_name = getattr(tool, "name", None) or getattr(tool, "__name__", None) or tool.__class__.__name__
                    tools.append({
                        "name": tool_name,
                        "description": f"Tool: {tool_name}",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    })
            # logger.info(f"tools/list result: {tools}")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": tools
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

            tool_func = user_server.tool_map.get(tool_name)
            if tool_func:
                try:
                    result = tool_func(**tool_args)
                    logger.info(f"Tool {tool_name} result: {result}")
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution error: {str(e)}"
                        }
                    }
            else:
                logger.error(f"Tool '{tool_name}' not found in tool_map")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        elif method == "notifications/cancel":
            logger.info("Received cancel notification")
            return None
        else:
            logger.error(f"Unknown method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
    except Exception as e:
        logger.error(f"Exception in handle_mcp_message: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

# endregion

# region INITIALIZE USERS MCP SERVERS (USER MCP SERVERS)
# Initialize default users
import mysql.connector

def initialize_default_users():
    """Initialize MCP servers for default users from MYSQL_USER_DB"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_USER_DB
        )
        cursor = connection.cursor(dictionary=True)
        # Giả sử bảng tên là 'user_servers' với các cột: username, database
        table = TenantColumn.database_infor_table.value
        col1 = TenantColumn.tenant_name.value
        col2 = TenantColumn.database_name.value
        cursor.execute(f"SELECT {col1}, {col2} FROM {table}")
        user_rows = cursor.fetchall()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error loading user MCP servers from DB: {e}")
        user_rows = []

    for user_config in user_rows:
        initialize_user_server(
            user_config[col1],
            user_config[col2]
        )

# endregion

# region MAIN ENTRYPOINT (SERVER)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Initialize default users
        initialize_default_users()
        
        # Create proxy endpoints for each user
        for username, user_server in user_mcp_servers.items():
            print(f"Creating proxy endpoints for user: {username}")
            create_proxy_endpoint(username, user_server)
        
        logger.info("Starting Multi-User MCP server on 127.0.0.1:8001")
        logger.info(f"Available users: {list(user_mcp_servers.keys())}")
        logger.info("MCP endpoints:")
        for username in user_mcp_servers.keys():
            logger.info(f"  - {username}: http://127.0.0.1:8001/{username}/mcp")
        
        # Run the FastAPI server
        uvicorn.run(app, host="127.0.0.1", port=8001)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Server stopped")

# endregion