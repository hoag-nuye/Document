#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_server():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Server is running")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        print(f"✅ Register response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Token: {result.get('access_token', 'No token')[:50]}...")
            return result.get('access_token')
        else:
            print(f"❌ Register failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Register error: {e}")
        return None

def test_login():
    """Test user login"""
    try:
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        print(f"✅ Login response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Token: {result.get('access_token', 'No token')[:50]}...")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_me_endpoint(token):
    """Test /me endpoint with token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"✅ /me response: {response.status_code}")
        if response.status_code == 200:
            print(f"User info: {response.json()}")
            return True
        else:
            print(f"❌ /me failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ /me error: {e}")
        return False

def test_mcp_access(token):
    """Test MCP endpoint access"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/testuser/mcp", headers=headers, json={
            "method": "tools/list"
        })
        print(f"✅ MCP access response: {response.status_code}")
        if response.status_code == 200:
            print("✅ MCP access successful")
            return True
        else:
            print(f"❌ MCP access failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ MCP access error: {e}")
        return False

def test_unauthorized_access():
    """Test unauthorized access to MCP"""
    try:
        # Try to access MCP without token
        response = requests.post(f"{BASE_URL}/testuser/mcp", json={
            "method": "tools/list"
        })
        print(f"✅ Unauthorized access response: {response.status_code}")
        if response.status_code == 401:
            print("✅ Unauthorized access correctly blocked")
            return True
        else:
            print(f"❌ Unauthorized access not blocked: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Unauthorized access test error: {e}")
        return False

def test_wrong_user_access(token):
    """Test access to another user's MCP"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # Try to access nguyennh5's MCP with testuser's token
        response = requests.post(f"{BASE_URL}/nguyennh5/mcp", headers=headers, json={
            "method": "tools/list"
        })
        print(f"✅ Wrong user access response: {response.status_code}")
        if response.status_code == 403:
            print("✅ Wrong user access correctly blocked")
            return True
        else:
            print(f"❌ Wrong user access not blocked: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wrong user access test error: {e}")
        return False

def main():
    print("🧪 Testing Multi-Tenant MCP Server with Authentication")
    print("=" * 60)
    
    # Test 1: Server running
    if not test_server():
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Register user
    token = test_register()
    if not token:
        print("Skipping other tests due to registration failure")
        return
    
    print("\n" + "=" * 60)
    
    # Test 3: Login user
    login_token = test_login()
    if not login_token:
        print("Skipping other tests due to login failure")
        return
    
    print("\n" + "=" * 60)
    
    # Test 4: Test /me endpoint
    test_me_endpoint(login_token)
    
    print("\n" + "=" * 60)
    
    # Test 5: Test MCP access
    test_mcp_access(login_token)
    
    print("\n" + "=" * 60)
    
    # Test 6: Test unauthorized access
    test_unauthorized_access()
    
    print("\n" + "=" * 60)
    
    # Test 7: Test wrong user access
    test_wrong_user_access(login_token)
    
    print("\n" + "=" * 60)
    print("🎉 Authentication tests completed!")

if __name__ == "__main__":
    main() 