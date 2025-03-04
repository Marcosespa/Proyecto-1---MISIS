# Documentación de la API REST

Esta API permite la autenticación de usuarios y la gestión de documentos para generar resúmenes y responder preguntas usando un modelo LLM mistral-7b-instruct-v0.1.Q4_K_M.gguf.


## Base URL

La API se sirve en:
```
http://<host>:<port>/
http://localhost:8080
```

Las rutas se agrupan en dos prefijos principales:  
- **/auth** para autenticación y gestión de usuarios.  
- **/docs** para operaciones con documentos.


## Autenticación

### 1. Registro de Usuario
- **Endpoint:** `POST /auth/registro`
- **Descripción:** Registra un nuevo usuario.
- **Request Body (JSON):**

    ```
    {
      "nombre_usuario": "usuario_ejemplo",
      "contrasena": "contraseña_segura",
      "imagen_perfil": "url_imagen_o_null"
    }
    ```
 
- **Respuestas:**  
  - **201 Created:** 

    ```json
    { "mensaje": "Usuario registrado" }
    ```
 
  - **400 Bad Request:** 

    ```json
    { "mensaje": "Usuario ya registrado" }
    ```


---


### 2. Inicio de Sesión (Login) 
 
- **Endpoint:**  `POST /auth/login`
 
- **Descripción:**  Autentica al usuario y retorna un token JWT.
 
- **Request Body (JSON):** 

  ```json
  {
    "nombre_usuario": "usuario_ejemplo",
    "contrasena": "contraseña_segura"
  }
  ```
 
- **Respuestas:**  
  - **200 OK:** 
    ```json
    { "access_token": "<JWT_TOKEN>" }
    ```
 
  - **401 Unauthorized:** 
    ```json
    { "mensaje": "Credenciales inválidas" }
    ```


---


### 3. Obtener Usuario Actual 
 
- **Endpoint:**  `GET /auth/usuarios/me`
 
- **Descripción:**  Retorna la información del usuario autenticado.
 
- **Headers:** 
`Authorization: Bearer <JWT_TOKEN>`
 
- **Respuestas:**  
  - **200 OK:** 

    ```json
    {
      "id": 1,
      "nombre_usuario": "usuario_ejemplo",
      "imagen_perfil": "url_imagen_o_null"
    }
    ```
 
  - **404 Not Found:** 

    ```json
    { "mensaje": "Usuario no encontrado" }
    ```


---


### 4. Cerrar Sesión 
 
- **Endpoint:**  `POST /auth/logout`
 
- **Descripción:**  Cierra la sesión del usuario autenticado.
 
- **Headers:** 
`Authorization: Bearer <JWT_TOKEN>`
 
- **Respuesta:**  
  - **200 OK:** 

    ```json
    { "mensaje": "Sesión cerrada" }
    ```


---


## Manejo de Documentos 

### 1. Subir Documento 
 
- **Endpoint:**  `POST /docs/upload`
 
- **Descripción:**  Permite al usuario subir un documento para ser procesado.
 
- **Headers:** 
`Authorization: Bearer <JWT_TOKEN>`
 
- **Request:** 
Tipo: `multipart/form-data` con el campo `file`.
 
- **Formatos Permitidos:** 
`txt`, `pdf`, `docx`, `md`
 
- **Respuestas:**  
  - **200 OK:** 

    ```json
    {
      "message": "Archivo cargado y procesado correctamente",
      "filename": "nombre_del_archivo.md"
    }
    ```
 
  - **400 Bad Request:** 
Posibles errores:

    ```json
    { "error": "No file part in the request" }
    { "error": "No file selected" }
    { "error": "Tipo de archivo no permitido" }
    ```


---


### 2. Generar Resumen del Documento 
 
- **Endpoint:**  `POST /docs/summarize`
 
- **Descripción:**  Genera y almacena un resumen del documento subido.
 
- **Headers:** 
`Authorization: Bearer <JWT_TOKEN>`
 
- **Respuestas:**  
  - **200 OK:** 

    ```json
    { "summary": "<resumen_generado>" }
    ```
 
  - **400 Bad Request:** 

    ```json
    { "error": "No se encontró documento cargado para este usuario" }
    ```


---


### 3. Preguntar sobre el Documento 
 
- **Endpoint:**  `POST /docs/ask`
 
- **Descripción:**  Responde preguntas basadas en el contenido del documento.
 
- **Headers:** 
`Authorization: Bearer <JWT_TOKEN>`
 
- **Request Body (JSON):** 

    ```json
    { "question": "¿De qué trata el documento?" }
    ```
 
- **Respuestas:**  
  - **200 OK:** 

    ```json
    { "answer": "<respuesta_generada>" }
    ```
 
  - **400 Bad Request:** Posibles errores:

      ```json
      { "error": "No se proporcionó la pregunta" }
      { "error": "No se encontró documento cargado para este usuario" }
      ```


---


## Configuración Adicional 
 
- **JWT Secret:** Configura `super-secret-key` con un valor secreto y seguro.
 
- **Base de Datos:**  Configurada con SQLAlchemy (por defecto `sqlite:///./test.db`).
 
- **Carpeta de Subida:**  `uploads`
 
- **CORS:** 
Configurado para permitir todos los orígenes:

    ```python
    CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"]}})
    ```
