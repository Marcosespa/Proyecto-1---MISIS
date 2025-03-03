from app import create_app, db
from flask_cors import CORS

app = create_app()
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)


# # back/run.py
# # from flask_cors import CORS
# # back/run.py
# from flask import Flask, send_from_directory
# from app import create_app

# app = Flask(__name__, static_folder='../front')

# @app.route('/')
# @app.route('/login')
# def serve_login():
#     return send_from_directory(app.static_folder, 'login.html')

# @app.route('/registro')
# def serve_registro():
#     return send_from_directory(app.static_folder, 'registro.html')

# @app.route('/index')
# def serve_index():
#     return send_from_directory(app.static_folder, 'index.html')

# @app.route('/app/<path:filename>')
# def serve_js(filename):
#     return send_from_directory(f'{app.static_folder}/app', filename)

# if __name__ == '__main__':
#     create_app()
#     app.run(debug=True, port=8080)