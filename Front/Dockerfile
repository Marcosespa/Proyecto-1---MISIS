# Usar una imagen base de Nginx
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copiar los archivos del frontend a la carpeta de Nginx
COPY ./frontend/public /usr/share/nginx/html

# Exponer el puerto 80 (puerto predeterminado de Nginx)
EXPOSE 3000

# Nginx se inicia automáticamente, no necesitas un CMD explícito