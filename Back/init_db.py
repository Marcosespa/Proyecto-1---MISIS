from app import create_app, db
from app.models import Usuario, Documento
import os
from dotenv import load_dotenv

# Cargar variables desde .env.local
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env.local'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), 'Back'))

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_db()
