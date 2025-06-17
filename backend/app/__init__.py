# backend/app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .routes import auth as auth_blueprint
from .routes.clinicas import clinicas_bp
from .routes.mascotas import mascotas_bp
from .routes.visitas import visitas_bp
from .routes.prop_mascotas import props_bp

from .extensions import db

def create_app():
    ## Construir rutas absolutas para el frontend
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..','..'))
    dist_dir = os.path.join(parent_dir, 'frontend', 'dist')
    static_dir = os.path.join(dist_dir, 'static')

    app = Flask(__name__,
                static_folder=static_dir,
                template_folder=dist_dir)

    ## Cargar configuración
    app.config.from_object('app.config.Config')
    
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    
    ## metemos esto siguiendo el tutorial
    jwt = JWTManager(app)

    ## Inicializar la base de datos
    db.init_app(app)

    CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True
    )

    ## Registrar blueprints (rutas)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(clinicas_bp)
    app.register_blueprint(mascotas_bp)
    app.register_blueprint(visitas_bp)
    app.register_blueprint(props_bp)


    ## Para desarrollo: crear tablas si no existen
    with app.app_context():
        from . import models
        from .models import Usuario
        print("Subclases de Usuario registradas:", Usuario.__subclasses__())
        db.create_all()

    return app

