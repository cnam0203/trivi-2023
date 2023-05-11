# Build docker image.
# Sử dung node
FROM node:12 as node

# Khai báo tham số
ARG workdir=.
LABEL description="deploy react app"

# Khái báo workdir trong node.
WORKDIR /app

# Copy project vào trong workdir của node.
COPY ${workdir}/ /app/

ENV BE_SERVER=localhost:8000
# Cài đặt các thư viện node liên quan.
RUN npm install --legacy-peer-deps

# Chạy lệnh build.
# RUN npm run build

# RUN npm install -g pm2

# # Sử dụng nginx
# FROM nginx:1.12
# # Copy folder đã được build vào folder chạy của nginx.
# COPY --from=node /app/build/ /var/www/dist/

# # Copy file cấu hình chạy cho nginx (file nginx.conf sẽ tạo ở bước tiếp theo)
# COPY --from=node /app/nginx.conf /etc/nginx/nginx.conf

# Cài đặt curl cho câu lệnh check HEALTH
# RUN apt-get update && apt-get install -y curl

# Kiểm tra trạng thái của container sau khi chạy
HEALTHCHECK --interval=1m --timeout=3s \
  CMD curl -f http://localhost || exit 1

# CMD ["nginx", "-g", "daemon off;"]