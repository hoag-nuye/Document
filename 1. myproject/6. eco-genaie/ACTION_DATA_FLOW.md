
## Thực hiện hành động chat với GeNaie
```css
User gõ https://app.example.com/chat
    ↓
[ Nginx / CDN ]  
    • Trả về index.html + JS bundle của web-app  
    ↓
[ web-app (React) ]  
    • React Router match path "/chat" → ChatPage component  
    • ChatPage thực hiện fetch:
        POST https://api.example.com/ai-agent/ask
        Body: { prompt: "Xin chào", server: "mcp" }
    ↓
[ ai-agent-service ]  
    • Controller nhận `/ask` → gọi Service layer  
    • Service layer dùng ai-client-sdk invoke MCP  
    
[ mcp-service ]  
    • Controller nhận RPC `/rpc/mcp` → thực thi logic → trả về JSON  
    ↓
[ ai-agent-service ]  
    • Nhận kết quả MCP → compose response → trả JSON cho web-app  
    ↓
[ web-app ]  
    • Nhận JSON kết quả → render lên UI  
    ↓
User nhìn thấy câu trả lời trên trang ChatPage  

```
## Khi nhập lệnh docker-compose up genaie_app_frontend trong Shell
```css
┌────────────────────────────────────────────────────────────────┐
│ [1] Shell (cmd/PowerShell/Bash)                                │
│   └─ Bạn gõ: docker-compose up genaie_app_frontend             │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [2] Docker Compose                                             │
│   • Đọc file: docker‑compose.yml                               │
│   • Tìm service: genaie_app_frontend                           │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [3] Build setup                                                │
│   • build.context = ./apps/genaie-app/src/frontend             │
│   • Truyền args/ENV vào Dockerfile                             │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [4] Docker Build                                               │
│   • Tạo image của service frontend                             │
│   • (Quá trình build, cài đặt node_modules,…)                  │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [5] Docker Run                                                 │
│   • Khởi container                                             │
│   • Thực thi CMD ["npm","run","dev"]                           │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [6] npm CLI                                                    │
│   • npm đọc package.json                                       │
│   • Tìm "scripts.dev" → "vite"                                 │
│   • Thiết lập PATH tới node_modules/.bin                       │
│   • Gọi child_process.spawn("vite", stdio…)                    │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [7] Vite CLI                                                   │
│   • Chạy file: node_modules/.bin/vite                          │
│   • Phân tích args (không có --config → dùng mặc định)         │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [8] Vite tìm config                                            │
│   Kiểm tra lần lượt ở project root:                            │
│     • vite.config.js                                           │
│     • vite.config.ts                                           │
│     • vite.config.mjs                                          │
│     • vite.config.cjs                                          │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [9] Load config                                                │
│   • Nếu .ts → transpile TS→JS (esbuild)                        │
│   • Nạp plugin & thiết lập server.open, port,…                 │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [10] Dev‑Server                                                │
│   • Khởi vite dev‑server với port = ${PORT_FRONTEND}           │
│   • server.open = '/index.html'                                │
└────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ [11] Kết quả                                                   │
│   • Mở trình duyệt tại                                         │
│     http://localhost:${PORT_FRONTEND}/index.html               │
│   • Hoặc dừng chờ bạn mở tay                                   │
└────────────────────────────────────────────────────────────────┘
```