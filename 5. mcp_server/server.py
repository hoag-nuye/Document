from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Dict
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
from enum import Enum as PyEnum
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import asyncio
import threading
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-this')

# Global dictionary to store user MCP servers
user_mcp_servers: Dict[str, 'UserMCPServer'] = {}

# Security
security = HTTPBearer()

# User models
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    database: str

class UserColumn(PyEnum):
    id = "id"
    email = "email"
    username = "username"
    role = "role"
    password = "password"

class UserMCPServer:
    def __init__(self, username: str, email: str, password: str, database: str):
        self.username = username
        self.email = email
        self.password = password
        self.database = database
        
        # Create MCP server for this user with path-based routing
        self.mcp = FastMCP(
            f"MySQL User Management - {username}",
            transport="streamable-http",
            host="127.0.0.1",
            port=8000,
            path=f"/{username}/mcp",
            prefix=""
        )
        
        # Initialize tools for this user
        self._init_tools()
        
    def get_db_connection(self):
        """Get database connection for this specific user"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
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
        def add_user(name: str, email: str, role: str) -> dict:
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
        def update_user(user_id: int, name: str, email: str, role: str, password: str = "") -> dict:
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
            """Search for users by column_name (id, email, name, role, password)"""
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor(dictionary=True)
                if column_name not in UserColumn:
                    return [{"status": "error", "message": "Invalid column name"}]
                query = f"SELECT * FROM users WHERE {column_name.value} LIKE %s"
                cursor.execute(query, (f"%{value}%",))
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
            """Get current user information"""
            return {
                "username": self.username,
                "email": self.email,
                "database": self.database,
                "endpoint": f"/{self.username}/mcp"
            }

# Create FastAPI app
app = FastAPI(title="Multi-Tenant MCP Server with Authentication")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(payload: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user"""
    username = payload.get("sub")
    if username not in user_mcp_servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "username": username,
        "email": user_mcp_servers[username].email,
        "database": user_mcp_servers[username].database
    }

# Database management
def get_auth_db_connection():
    """Get connection to authentication database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD,
            database='mcp_auth_db'
        )
        return connection
    except Error as e:
        print(f"Error connecting to auth database: {e}")
        return None

def init_auth_database():
    """Initialize authentication database"""
    try:
        # Create auth database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS mcp_auth_db")
        connection.commit()
        cursor.close()
        connection.close()
        
        # Create users table
        conn = get_auth_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(100) DEFAULT 'user',
                    database_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("Authentication database initialized successfully")
    except Error as e:
        print(f"Error initializing auth database: {e}")

def create_user_database(database_name: str):
    """Create a new database for a user"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Database {database_name} created successfully")
        return True
    except Error as e:
        print(f"Error creating database {database_name}:", e)
        return False

def initialize_user_server(username: str, email: str, password: str, database: str):
    """Initialize MCP server for a specific user"""
    # Create database if it doesn't exist
    create_user_database(database)
    
    # Create user MCP server
    user_server = UserMCPServer(username, email, password, database)
    
    # Initialize database tables
    user_server.init_db()
    
    # Store the server
    user_mcp_servers[username] = user_server
    
    print(f"MCP server initialized for user {username} at /{username}/mcp")
    return user_server

# API Endpoints
@app.post("/register", response_model=dict)
def register_user(user_data: UserRegister):
    """Register a new user"""
    conn = get_auth_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    
    # Check if username already exists
    cursor.execute("SELECT * FROM auth_users WHERE username = %s", (user_data.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    cursor.execute("SELECT * FROM auth_users WHERE email = %s", (user_data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create database name
    database_name = f"user_management_test_{user_data.username}"
    
    try:
        # Insert user into auth database
        cursor.execute(
            "INSERT INTO auth_users (username, email, password_hash, database_name) VALUES (%s, %s, %s, %s)",
            (user_data.username, user_data.email, password_hash, database_name)
        )
        conn.commit()
        
        # Initialize MCP server for user
        user_server = initialize_user_server(user_data.username, user_data.email, user_data.password, database_name)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_data.username},
            expires_delta=timedelta(days=7)
        )
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"User {user_data.username} registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "endpoint": f"http://127.0.0.1:8000/{user_data.username}/mcp",
            "database": database_name
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=dict)
def login_user(user_data: UserLogin):
    """Login user"""
    conn = get_auth_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    
    # Check user credentials
    password_hash = hash_password(user_data.password)
    cursor.execute(
        "SELECT * FROM auth_users WHERE username = %s AND password_hash = %s",
        (user_data.username, password_hash)
    )
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(days=7)
    )
    
    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "database": user["database_name"]
        }
    }

@app.get("/me", response_model=dict)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "status": "success",
        "user": current_user,
        "endpoint": f"http://127.0.0.1:8000/{current_user['username']}/mcp"
    }

@app.get("/")
def read_root():
    """Root endpoint showing available users"""
    return {
        "message": "Multi-Tenant MCP Server with Authentication",
        "endpoints": {
            "register": "/register",
            "login": "/login", 
            "me": "/me",
            "users": "/users"
        }
    }

@app.get("/users")
def get_users(current_user: dict = Depends(get_current_user)):
    """Get list of all registered users (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_auth_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, email, role, database_name, created_at FROM auth_users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {
        "status": "success",
        "users": users
    }

# Secure MCP endpoint middleware
@app.middleware("http")
async def secure_mcp_endpoints(request: Request, call_next):
    """Middleware to secure MCP endpoints"""
    path = request.url.path
    
    # Check if this is an MCP endpoint
    if "/mcp" in path:
        # Extract username from path
        path_parts = path.split("/")
        if len(path_parts) >= 3:
            username = path_parts[1]  # /username/mcp
            
            # Check if user exists
            if username not in user_mcp_servers:
                return JSONResponse(
                    status_code=404,
                    content={"error": "User not found"}
                )
            
            # Verify authentication
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Authentication required"}
                )
            
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                token_username = payload.get("sub")
                
                # Check if token belongs to the correct user
                if token_username != username:
                    return JSONResponse(
                        status_code=403,
                        content={"error": "Access denied to this user's MCP"}
                    )
                    
            except jwt.PyJWTError:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid token"}
                )
    
    response = await call_next(request)
    return response

# Initialize servers for users from mcp.json
def initialize_all_users():
    """Initialize MCP servers for all users defined in mcp.json"""
    # This would typically read from a configuration file or database
    # For now, we'll hardcode the users from your mcp.json
    
    users_config = [
        {
            "username": "nguyennh5",
            "email": "nguyennh5@runsystem.net",
            "password": "032401",
            "database": "user_management_test_nguyennh5"
        },
        {
            "username": "nguyennh6",
            "email": "nguyennh6@runsystem.net", 
            "password": "032401",
            "database": "user_management_test_nguyennh6"
        }
    ]
    
    for user_config in users_config:
        initialize_user_server(
            user_config["username"],
            user_config["email"], 
            user_config["password"],
            user_config["database"]
        )

# Mount MCP servers to FastAPI
def mount_mcp_servers():
    """Mount all MCP servers to the FastAPI app"""
    for username, user_server in user_mcp_servers.items():
        # Mount the MCP server's app to the main FastAPI app
        app.mount(f"/{username}/mcp", user_server.mcp.app)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Initialize authentication database
        init_auth_database()
        
        # Initialize all users
        initialize_all_users()
        
        # Mount MCP servers to FastAPI
        mount_mcp_servers()
        
        logger.info("Starting Multi-Tenant MCP server with authentication on 127.0.0.1:8000")
        logger.info(f"Available users: {list(user_mcp_servers.keys())}")
        
        # Run the FastAPI server
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Server stopped")