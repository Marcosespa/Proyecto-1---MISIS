import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://misis_user:contrasena@34.170.253.253/misis_db'
os.environ['SECRET_KEY'] = 'dev-secret-key'
os.environ['JWT_SECRET_KEY'] = 'jwt-secret-key'

import sys
from app import create_app, db
from app.models import Usuario, Documento
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
        print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()


# # NUEVO 
# from dotenv import load_dotenv
# import os

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# # Importa sólo lo necesario para la base de datos
# from app import create_app, db

# def init_db():
#     app = create_app(with_docs=False)  # si adaptas create_app para no cargar docs
#     with app.app_context():
#         db.create_all()
#         print("Base de datos inicializada correctamente.")

# if __name__ == "__main__":
#     init_db()
