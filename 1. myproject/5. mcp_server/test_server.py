from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test Server")

@app.get("/")
def read_root():
    return {"message": "Test server is running"}

@app.get("/test")
def test():
    return {"status": "success", "message": "Test endpoint works"}

if __name__ == "__main__":
    print("Starting test server...")
    uvicorn.run(app, host="127.0.0.1", port=8000) 