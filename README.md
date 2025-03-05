# Proyecto-1---MISIS

Esta aplicación permite la gestión, análisis y resumen automatizado de documentos utilizando un modelo LLM local (Llama) para resumir textos, proporcionar explicaciones y responder preguntas.

## Funcionalidades

- Registro e inicio de sesión de usuarios (JWT)
- Carga de documentos en formatos: PDF, TXT, DOCX y Markdown
- Generación de resúmenes y respuestas a preguntas basadas en el contenido del documento utilizando el modelo Mistral 7B Instruct v0.1 - GGUF
- API REST implementada con Flask

## Cómo ejecutar la API

### Usando Docker Compose

1. Clona el repositorio.
2. Dirigite a la carpeta Back, y descarga el modelo `huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.1-GGUF mistral-7b-instruct-v0.1.Q4_K_M.gguf --local-dir . --local-dir-use-symlinks False`
3. Ejecuta el siguiente comando para construir las imágenes y levantar los contenedores:
`docker-compose up --build`
4. Una vez levantados los contenedores, la API estará disponible en: http://localhost:8080

### Documentación de la API
Puedes acceder a la [documentacion](Back/Documentacion_API.md)

### Video del Proyecto
Puedes acceder al [video](https://www.youtube.com/watch?v=Olw-yXb1w0Y)
