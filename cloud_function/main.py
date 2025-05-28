import base64
import json
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud import storage, pubsub_v1
from pypdf import PdfReader
from docx import Document
import google.cloud.logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar cliente de logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configuración de la base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Documento(Base):
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    text = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def extract_text(file_path):
    """Extrae el texto de un archivo PDF o DOCX."""
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                return text
        elif file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_path}")
    except Exception as e:
        logger.error(f"Error al extraer texto: {str(e)}")
        raise

def process_document(event, context):
    """Función principal que procesa el documento."""
    try:
        # Obtener el mensaje de Pub/Sub
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_data = json.loads(pubsub_message)
        
        document_id = message_data.get('document_id')
        filename = message_data.get('filename')
        
        if not document_id or not filename:
            raise ValueError("document_id y filename son requeridos en el mensaje")
        
        logger.info(f"Procesando documento: {filename} (ID: {document_id})")
        
        # Configurar clientes
        storage_client = storage.Client()
        pubsub_client = pubsub_v1.PublisherClient()
        
        # Obtener el bucket y el blob
        bucket_name = os.environ.get('BUCKET_NAME')
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        
        # Descargar el archivo
        temp_file = f"/tmp/{filename}"
        blob.download_to_filename(temp_file)
        
        # Extraer el texto
        text = extract_text(temp_file)
        
        # Actualizar la base de datos
        db = SessionLocal()
        try:
            documento = db.query(Documento).filter(Documento.id == document_id).first()
            if documento:
                documento.text = text
                documento.status = "processed"
                documento.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Documento {document_id} actualizado exitosamente")
            else:
                logger.error(f"Documento {document_id} no encontrado en la base de datos")
                raise ValueError(f"Documento {document_id} no encontrado")
        finally:
            db.close()
        
        # Publicar mensaje de éxito
        project_id = os.environ.get('PROJECT_ID')
        completion_topic = os.environ.get('COMPLETION_TOPIC')
        topic_path = pubsub_client.topic_path(project_id, completion_topic)
        
        success_message = {
            'document_id': document_id,
            'status': 'success',
            'message': 'Documento procesado exitosamente'
        }
        
        pubsub_client.publish(topic_path, json.dumps(success_message).encode('utf-8'))
        logger.info(f"Mensaje de éxito publicado para documento {document_id}")
        
        # Limpiar archivo temporal
        os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"Error procesando documento: {str(e)}")
        
        # Publicar mensaje de error
        try:
            project_id = os.environ.get('PROJECT_ID')
            error_topic = os.environ.get('ERROR_TOPIC')
            topic_path = pubsub_client.topic_path(project_id, error_topic)
            
            error_message = {
                'document_id': document_id,
                'status': 'error',
                'error': str(e)
            }
            
            pubsub_client.publish(topic_path, json.dumps(error_message).encode('utf-8'))
            logger.info(f"Mensaje de error publicado para documento {document_id}")
        except Exception as pubsub_error:
            logger.error(f"Error publicando mensaje de error: {str(pubsub_error)}")
        
        # Actualizar estado en la base de datos
        try:
            db = SessionLocal()
            documento = db.query(Documento).filter(Documento.id == document_id).first()
            if documento:
                documento.status = "error"
                documento.updated_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Error actualizando estado en la base de datos: {str(db_error)}")
        finally:
            db.close()
        
        # Limpiar archivo temporal si existe
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        
        raise 