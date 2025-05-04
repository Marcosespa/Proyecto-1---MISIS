
# Documentación de la API de Procesamiento de Documentos

Esta API permite a los usuarios autenticados cargar documentos, resumir su contenido y realizar preguntas sobre ellos utilizando la API de Gemini.

## Autenticación
Todas las rutas requieren autenticación JWT. Incluya el token en el encabezado `Authorization` como:

```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. `POST /upload`
**Descripción:** Carga un archivo al servidor y lo registra como documento pendiente de procesamiento.

**Parámetros:**
- `file` (form-data): Archivo a cargar (`.txt`, `.pdf`, `.docx`, `.md`)

**Respuesta exitosa:**
```json
{
  "message": "Archivo cargado y procesado correctamente",
  "filename": "documento.pdf",
  "documento_id": 1
}
```

**Errores comunes:**
- `400`: No se proporcionó un archivo o tipo de archivo no permitido
- `500`: Error interno del servidor

---

### 2. `POST /summarize`
**Descripción:** Resume el contenido del documento del usuario usando la API de Gemini.

**Parámetros (JSON):**
- `documento_id` (opcional): ID del documento. Si no se especifica, se usa el primer documento del usuario.

**Respuesta exitosa:**
```json
{
  "summary": "Resumen generado por Gemini."
}
```

**Errores comunes:**
- `400`: Documento no encontrado
- `500`: Error al generar el resumen

---

### 3. `POST /ask`
**Descripción:** Realiza una pregunta sobre el contenido del documento cargado.

**Parámetros (JSON):**
- `question`: Pregunta a realizar
- `documento_id` (opcional): ID del documento a consultar

**Respuesta exitosa:**
```json
{
  "answer": "Respuesta generada por Gemini."
}
```

**Errores comunes:**
- `400`: No se proporcionó pregunta o no se encontró el documento
- `500`: Error al generar la respuesta

---

### 4. `GET /list`
**Descripción:** Lista todos los documentos cargados por el usuario.

**Respuesta exitosa:**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "documento.pdf",
      "summary": null,
      "preview": "Primeras palabras del documento..."
    }
  ]
}
```

---

### 5. `DELETE /<document_id>`
**Descripción:** Elimina un documento específico del usuario.

**Respuesta exitosa:**
```json
{
  "Exitoso": "Docuemnto eliminado"
}
```

**Errores comunes:**
- `404`: Documento no encontrado
- `500`: Error al eliminar

---

## Procesamiento Interno

### Extracción de texto
Los formatos soportados son:
- `.txt`, `.md`: Lectura directa
- `.pdf`: Uso de `pypdf`
- `.docx`: Uso de `python-docx`

### Fragmentación de texto
Se divide el texto en fragmentos de 500 palabras con solapamiento de 50, para facilitar el análisis posterior.

### API de Gemini
- Se usa para generar resúmenes y responder preguntas
- Se limita el contexto a 2000 caracteres para no exceder límites de la API

**Modelo usado:** `gemini-1.5-pro-latest`

---

## Variables de Entorno Necesarias
- `GEMINI_API_KEY`: Clave de la API de Gemini

---

## Dependencias
- Flask
- Flask-JWT-Extended
- pypdf
- python-docx
- requests
- dotenv
- SQLAlchemy (db)

---

## Notas Finales
- Se almacena la información del documento en una base de datos, incluyendo estado, texto y resumen.
- El texto completo del documento no se expone directamente vía API (solo un preview).
- El sistema está diseñado para ejecutarse en entornos con almacenamiento compartido (`/mnt/nfs/files`).
