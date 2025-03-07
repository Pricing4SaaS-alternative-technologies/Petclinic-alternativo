# backend/app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    # Construir rutas absolutas para el frontend
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..','..'))
    dist_dir = os.path.join(parent_dir, 'frontend', 'dist')
    static_dir = os.path.join(dist_dir, 'static')

    app = Flask(__name__,
                static_folder=static_dir,
                template_folder=dist_dir)

    # Cargar configuración
    app.config.from_object('app.config.Config')

    # Inicializar la base de datos
    db.init_app(app)

    # Habilitar CORS para las rutas de la API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar blueprints (rutas)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Para desarrollo: crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app
