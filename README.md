# Proyecto 1 - Entrega 4

Esta aplicación permite a los usuarios gestionar documentos, generar resúmenes y obtener respuestas a preguntas basadas en su contenido. En lugar de usar un modelo local como Llama o Mistral 7B, ahora utiliza la **API de Gemini** para procesar el texto de forma eficiente. Incluye un backend con Flask, un frontend simple y un sistema de procesamiento en segundo plano con un worker.

---

## Cambios Clave Respecto a la Versión Anterior
- Modelo: Pasamos de usar Mistral 7B a la API de Gemini para resúmenes y respuestas.
- Procesamiento: Antes, el texto se extraía al subir el archivo; ahora se guarda como pending y el worker lo procesa después.
- Rutas: Se añadieron /list y /delete para gestionar mejor los documentos.
- Flexibilidad: Puedes usar un documento_id para trabajar con documentos específicos.
- Texto: Nuevas funciones como clean_text, split_text_into_chunks y truncate_text optimizan el manejo del texto.
---


##  Componentes Principales

### 1. Cloud Run  

### 2. Pub/Sub

### 3. Cloud Functions

### 4. Bucket Cloud Storage

### 5. Cloud SQL (Postgres)  
- Instancia gestionada en us‑central1‑c  
- Guarda usuarios, metadatos de documentos y estados de procesamiento

### 6. Cloud Monitoring  
- Vigila CPU, latencia y tamaño del MIG  
- Dispara escalado y alertas ante fallos

### Documentación de la API
Puedes acceder a la [documentacion](/Documentacion_API.md)

### Video del Proyecto
Puedes acceder al [video](https://youtu.be/YYK1vjMiQvM)



