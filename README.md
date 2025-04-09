#  Proyecto 1 - Entrega 2 

Esta aplicación permite a los usuarios gestionar documentos, generar resúmenes y obtener respuestas a preguntas basadas en su contenido. En lugar de usar un modelo local como Llama o Mistral 7B, ahora utiliza la **API de Gemini** para procesar el texto de forma eficiente. Incluye un backend con Flask, un frontend simple y un sistema de procesamiento en segundo plano con un worker.

---

## Cambios Clave Respecto a la Versión Anterior
- Modelo: Pasamos de usar Mistral 7B a la API de Gemini para resúmenes y respuestas.
- Procesamiento: Antes, el texto se extraía al subir el archivo; ahora se guarda como pending y el worker lo procesa después.
- Rutas: Se añadieron /list y /delete para gestionar mejor los documentos.
- Flexibilidad: Puedes usar un documento_id para trabajar con documentos específicos.
- Texto: Nuevas funciones como clean_text, split_text_into_chunks y truncate_text optimizan el manejo del texto.
---
##  `web-server-vm` — **Servidor Principal (Frontend + Backend)**

###   Funcionalidades:

- Corre el **backend Flask** (`web-app`) en el puerto **5000**.
- Corre el **frontend HTML/JS** (`front-app`) en el puerto **80**.
- Ambos acceden a la carpeta compartida `/mnt/nfs/files` montada desde un servidor NFS.
- Permite:
  - Registro e inicio de sesión de usuarios (usando JWT).
  - Carga de documentos en formatos como PDF, TXT, DOCX y Markdown.
  - Generación de resúmenes y respuestas a preguntas usando la API de Gemini.
- Nuevas rutas:
  - `/list`: Muestra todos los documentos del usuario con resumen y vista previa.
  - `/delete/<int:document_id>`: Elimina un documento específico (con verificación de propiedad).
- Soporte para documentos específicos mediante `documento_id` en rutas como `/ask` y `/summarize`.


##  worker-vm — Procesamiento en Segundo Plano
###   Funcionalidades:
- Corre worker.py dentro de un contenedor Docker.
- Lee archivos desde /mnt/nfs/files.
- Procesa documentos con status = "pending" en la base de datos.
- Extrae el texto de los archivos y lo guarda, marcando el documento como processed.
- Usa funciones como:
- clean_text: Normaliza el texto eliminando espacios excesivos.
- split_text_into_chunks: Divide textos largos en fragmentos con solapamiento.
- truncate_text: Limita el texto a 2000 caracteres para la API.

##  nfs-vm — Servidor de Archivos Compartido
###   Funcionalidades:
- Exporta la carpeta /mnt/nfs/files vía NFS a las otras dos VMs (web-server-vm y worker-vm).
- Permite que el backend almacene archivos subidos y que el worker los procese desde un lugar centralizado.
