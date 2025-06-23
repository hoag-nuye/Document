FROM maven:3.8.7-eclipse-temurin-17
ARG BACKEND_PORT
WORKDIR /app

# Copy everything (chỉ để chạy spring-boot:run)
COPY . /app

RUN mvn clean package -DskipTests

# Dùng devtools nếu muốn auto reload
RUN mvn dependency:go-offline

EXPOSE ${BACKEND_PORT}
CMD ["mvn", "spring-boot:run", "-X"]
