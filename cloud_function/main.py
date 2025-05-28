import os
import json
import base64
import logging
from google.cloud import storage
from google.cloud import pubsub_v1
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Documento, Base
from app.docs import extract_text
import functions_framework
#INTENTO
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine and session
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

logger.info(f"Connecting to database with URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def process_document_impl(cloud_event):
    """Implementation of document processing logic."""
    temp_path = None
    session = None
    try:
        # Get PubSub message from CloudEvent
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')
        message_data = json.loads(pubsub_message)
        
        document_id = message_data.get('document_id')
        filename = message_data.get('filename')
        
        if not document_id or not filename:
            logger.error("Missing required fields in message")
            return
        
        # Initialize Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(os.environ.get('BUCKET_NAME'))
        blob = bucket.blob(filename)
        
        # Download file to temporary location
        temp_path = f"/tmp/{filename}"
        logger.info(f"Downloading file {filename} to {temp_path}")
        blob.download_to_filename(temp_path)
        
        session = Session()
        doc = session.query(Documento).get(document_id)
        if not doc:
            logger.error(f"Document {document_id} not found")
            return
            
        logger.info(f"Processing document ID={doc.id}, file={doc.filename}")
        text = extract_text(temp_path, doc.filename)
        doc.text = text
        doc.status = "processed"
        session.commit()
        
        # Publish completion message
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(
            os.environ.get('PROJECT_ID'),
            os.environ.get('COMPLETION_TOPIC')
        )
        
        completion_message = {
            'document_id': document_id,
            'status': 'processed'
        }
        
        publisher.publish(
            topic_path,
            json.dumps(completion_message).encode('utf-8')
        )
        
        logger.info(f"Document ID {doc.id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error in function: {str(e)}")
        if session:
            session.rollback()
        
        # Publish error message
        try:
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(
                os.environ.get('PROJECT_ID'),
                os.environ.get('ERROR_TOPIC')
            )
            
            error_message = {
                'document_id': document_id if 'document_id' in locals() else None,
                'status': 'error',
                'error': str(e)
            }
            
            publisher.publish(
                topic_path,
                json.dumps(error_message).encode('utf-8')
            )
        except Exception as pubsub_error:
            logger.error(f"Error publishing error message: {str(pubsub_error)}")
            
    finally:
        if session:
            session.close()
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")

@functions_framework.cloud_event
def process_document(cloud_event):
    """Cloud Function entry point."""
    try:
        process_document_impl(cloud_event)
        return ('OK', 200)
    except Exception as e:
        logger.error(f"Error in process_document: {str(e)}")
        return (str(e), 500) 