import sys
import os
from dotenv import load_dotenv

# Cargar variables desde .env.local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env.local'))

sys.path.append(os.path.join(os.path.dirname(__file__), 'Back'))

from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas exitosamente.")
