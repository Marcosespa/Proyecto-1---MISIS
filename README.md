# Proyecto 1 - Entrega 3

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

### 1. Load Balancer  
- **first‑balancer**: External HTTP(S) Load Balancer global  
- Distribuye tráfico a las réplicas del Web Tier  

### 2. Web Tier – Managed Instance Group (`instance-group-1`)  
- **Instancias**: f1‑micro (1–3 réplicas) en us‑central1‑a, ‑b y ‑c  
- **Contenedores**:
  - **Front**: HTML/CSS/JS servido en el puerto 80  
  - **Back**: Flask API en el puerto 5000  
  - Llamadas a la API de Gemini para IA  
- **Autoscaling**: CPU ≥ 60 % → escala; Auto‑healing via `/healthz`

### 3. NFS‑VM  
- VM e2‑medium en us‑central1‑a  
- Exporta `/mnt/nfs/files` vía NFS  
- Montada por todas las réplicas web y por Worker‑VM

### 4. Worker‑VM  
- VM f1‑micro en us‑central1‑a  
- Contenedor que:
  1. Consulta Cloud SQL por documentos `pending`
  2. Lee archivos de NFS
  3. Procesa texto y genera resumen/QA con Gemini API
  4. Guarda resultado en NFS y marca `processed`

### 5. Cloud SQL (Postgres)  
- Instancia gestionada en us‑central1‑c  
- Guarda usuarios, metadatos de documentos y estados de procesamiento

### 6. Cloud Monitoring  
- Vigila CPU, latencia y tamaño del MIG  
- Dispara escalado y alertas ante fallos

### Documentación de la API
Puedes acceder a la [documentacion](/Documentacion_API.md)

### Video del Proyecto
Puedes acceder al [video](https://youtu.be/yIA_pL5DmYQ)



