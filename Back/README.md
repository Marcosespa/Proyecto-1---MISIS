# Proyecto-1---MISIS

Esta aplicación permite la gestión, análisis y resumen automatizado de documentos utilizando un modelo LLM local (Llama) para resumir textos, proporcionar explicaciones y responder preguntas.

## Funcionalidades

- Registro e inicio de sesión de usuarios (JWT)
- Carga de documentos en formatos: PDF, TXT, DOCX y Markdown
- Generación de resúmenes y respuestas a preguntas basadas en el contenido del documento utilizando el modelo Llama (llama_cpp)
- API REST implementada con FastAPI

## Cómo ejecutar la aplicación

### Usando Docker Compose

1. Clona el repositorio.
2. Ejecuta: `docker-compose up --build`

3. La aplicación estará disponible en `http://localhost:8000`

### Ejecución local sin Docker

1. Instala las dependencias: `pip install -r requirements.txt`
2. Ejecuta la aplicación: `uvicorn app.main:app --reload`
3. Accede a la documentación interactiva en `http://localhost:8000/docs`