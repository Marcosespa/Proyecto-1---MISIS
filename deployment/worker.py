import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app.models import Documento
from app.docs import extract_text

NFS_PATH = "/mnt/nfs/files"

def process_pending_documents():
    session = db.session
    pendientes = session.query(Documento).filter_by(status="pending").all()
    for doc in pendientes:
        filepath = os.path.join(NFS_PATH, doc.filename)
        if not os.path.exists(filepath):
            continue
        try:
            print(f"Procesando documento ID: {doc.id} ({doc.filename})")
            text = extract_text(filepath, doc.filename)
            doc.text = text
            doc.status = "processed"
            session.commit()
            print(f"Documento ID {doc.id} procesado exitosamente")
        except Exception as e:
            print(f" Error procesando documento ID {doc.id}: {str(e)}")
            session.rollback()

if __name__ == "__main__":
    # print(f" Worker corriendo... observando {NFS_PATH}")
    while True:
        process_pending_documents()
        time.sleep(5)
