import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  // 2. Cho dev-server tự động mở đúng file
  server: {
    host: '0.0.0.0', //  lắng nghe mọi IP trên máy
    // open: '/index.html',  // lúc chạy `npm run dev` sẽ auto mở http://localhost:3000/index.html
    port: Number(process.env.VITE_FRONTEND_PORT),
    watch: {
        usePolling: true,
        interval: 100,
      },
  }
})
