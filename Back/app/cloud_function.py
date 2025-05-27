import os
import json
import base64
from google.cloud import storage
from google.cloud import pubsub_v1
from app import create_app, db
from app.models import Documento
from app.docs import extract_text

app = create_app()

def process_document(event, context):
    """Cloud Function triggered by Pub/Sub message."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message_data = json.loads(pubsub_message)
    
    document_id = message_data.get('document_id')
    filename = message_data.get('filename')
    
    if not document_id or not filename:
        print("Missing required fields in message")
        return
    
    # Initialize Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ.get('BUCKET_NAME'))
    blob = bucket.blob(filename)
    
    # Download file to temporary location
    temp_path = f"/tmp/{filename}"
    blob.download_to_filename(temp_path)
    
    try:
        with app.app_context():
            doc = Documento.query.get(document_id)
            if not doc:
                print(f"Document {document_id} not found")
                return
                
            print(f"📥 Processing document ID={doc.id}, file={doc.filename}")
            text = extract_text(temp_path, doc.filename)
            doc.text = text
            doc.status = "processed"
            db.session.commit()
            
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
            
            print(f"Document ID {doc.id} processed successfully")
            
    except Exception as e:
        print(f"Error processing document ID {document_id}: {str(e)}")
        # Publish error message
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(
            os.environ.get('PROJECT_ID'),
            os.environ.get('ERROR_TOPIC')
        )
        
        error_message = {
            'document_id': document_id,
            'status': 'error',
            'error': str(e)
        }
        
        publisher.publish(
            topic_path,
            json.dumps(error_message).encode('utf-8')
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path) 