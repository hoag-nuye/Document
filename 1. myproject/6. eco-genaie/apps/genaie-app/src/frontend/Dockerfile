FROM node:18

# Lấy biến môi trường từ docker-compose.yml
ARG FRONTEND_PORT

# Tạo thư mục làm việc bên trong container
WORKDIR /app

# Copy file cấu hình trước để cache npm/yarn install
COPY package.json package-lock.json ./

# Cài thư viện một lần
RUN npm install

# Copy toàn bộ source code
COPY . .

# Set biến môi trường cho container.
ENV FRONTEND_PORT=${FRONTEND_PORT}
# Mô tả cổng sẽ mở trong container.
EXPOSE ${FRONTEND_PORT}

# Dev command (sẽ override bằng docker-compose nên không quan trọng lắm)
CMD ["npm", "run", "dev"]
