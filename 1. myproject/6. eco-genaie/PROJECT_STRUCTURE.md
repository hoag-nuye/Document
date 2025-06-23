```sh
.
├── apps
│   ├── genaie-app/                                         # Ứng dụng chính
│   │   ├── public/                                         # File tĩnh cho frontend
│   │   ├── src/
│   │   │   ├── backend/                                    # Backend (Java/Spring Boot)
│   │   │   │   ├── main/
│   │   │   │   │   ├── java/com/yourorg/
│   │   │   │   │   │   ├── auth/                       # Logic đăng nhập
│   │   │   │   │   │   │   ├── controller/
│   │   │   │   │   │   │   │   └── AuthController.java
│   │   │   │   │   │   │   ├── service/
│   │   │   │   │   │   │   │   └── AuthService.java
│   │   │   │   │   │   │   ├── repository/
│   │   │   │   │   │   │   │   └── UserRepository.java
│   │   │   │   │   │   │   ├── model/
│   │   │   │   │   │   │   │   └── UserModel.java
│   │   │   │   │   │   │   └── middleware/
│   │   │   │   │   │   │       └── AuthMiddleware.java
│   │   │   │   │   │   ├── playground/                 # Thêm: Logic playground
│   │   │   │   │   │   │   ├── controller/
│   │   │   │   │   │   │   │   └── PlaygroundController.java  # API cho chat và tool
│   │   │   │   │   │   │   ├── service/
│   │   │   │   │   │   │   │   └── PlaygroundService.java    # Xử lý chat và thêm tool
│   │   │   │   │   │   │   └── model/
│   │   │   │   │   │   │       └── ToolModel.java            # Model cho công cụ
│   │   │   │   │   │   ├── config/
│   │   │   │   │   │   │   └── DatabaseConfig.java
│   │   │   │   │   │   └── routes/
│   │   │   │   │   │       ├── AuthRoutes.java
│   │   │   │   │   │       └── PlaygroundRoutes.java         # Thêm: Route cho playground
│   │   │   ├── frontend/                                   # Frontend (React)
│   │   │   │   ├── features/
│   │   │   │   │   ├── auth/                           # Đăng nhập/đăng ký
│   │   │   │   │   │   ├── components/
│   │   │   │   │   │   │   ├── LoginForm.tsx
│   │   │   │   │   │   │   ├── RegisterForm.tsx
│   │   │   │   │   │   │   └── Profile.tsx
│   │   │   │   │   │   ├── hooks/
│   │   │   │   │   │   │   └── useAuth.tsx
│   │   │   │   │   │   └── services/
│   │   │   │   │   │       └── authService.ts
│   │   │   │   │   └── playground/                     # Thêm: Chức năng playground
│   │   │   │   │       ├── components/
│   │   │   │   │       │   ├── ChatWithGeNaie.tsx      # Chat với trợ lý
│   │   │   │   │       │   └── AddToolForm.tsx         # Thêm: Form thêm tool
│   │   │   │   │       ├── hooks/
│   │   │   │   │       │   └── usePlayground.tsx       # Thêm: Quản lý state playground
│   │   │   │   │       └── services/
│   │   │   │   │           └── playgroundService.ts    # Thêm: Gọi API cho playground
│   │   │   │   ├── App.tsx                              # Điểm vào frontend
│   │   │   │   └── main.tsx
│   │   ├── .env                                         # Biến môi trường
│   │   ├── package.json                                 # Dependencies
│   │   ├── tsconfig.json                                # Config TypeScript
│   │   └── README.md
├── services
│   ├── mcp-server-service/                              # MCP Server
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/com/yourorg/mcp/
│   │   │   │   │   └── mysql-server/
│   │   │   │   │       ├── controller/
│   │   │   │   │       ├── service/
│   │   │   │   │       ├── model/
│   │   │   │   │       ├── repository/
│   │   │   │   │       └── routes/
│   │   │   │   └── resources/
│   │   │   │       └── application.yml
│   │   │   └── test/
│   │   ├── Dockerfile
│   │   └── pom.xml
│   ├── mcp-client-sdk/                                  # MCP Client SDK
│   │   ├── python/
│   │   ├── java/
│   │   └── README.md
│   ├── ai-agent-mcp-service/                            # Dịch vụ AI Agent
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/com/yourorg/agent/
│   │   │   │   │   └── chats-genaie-agent/
│   │   │   │   │       ├── controller/
│   │   │   │   │       │   └── ChatsGeNaieController.java
│   │   │   │   │       ├── service/
│   │   │   │   │       │   └── ChatsGeNaieService.java
│   │   │   │   │       ├── model/
│   │   │   │   │       │   ├── ChatsGeNaieModel.java
│   │   │   │   │       │   └── ToolModel.java          # Thêm: Model cho tool
│   │   │   │   │       ├── client/
│   │   │   │   │       └── routes/
│   │   │   │   └── resources/
│   │   │   │       └── application.yml
│   │   │   └── test/
│   │   ├── Dockerfile
│   │   └── pom.xml
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yaml
```

