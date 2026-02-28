# backend/app/__init__.py
import os
from app.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import asyncio
from app_SpacePyCl.routes.config import SpaceClient
import atexit

from .routes import auth as auth_blueprint
from .routes.clinicas import clinicas_bp
from .routes.mascotas import mascotas_bp
from .routes.visitas import visitas_bp
from .routes.prop_mascotas import prop_mascotas_bp
from .routes.veterinario import veterinario_bp
from .routes.adopciones import adopciones_bp
from .routes.contratos import contratos as contratos_bp
from .routes.habitaciones_hotel import habitaciones_hotel as habitaciones_hotel
from .routes.reservas import reservas as reservas
from .routes.peticiones_adopcion import peticiones_bp

from .extensions import db

def create_app(test_config=None):
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
    if test_config:
        app.config.update(test_config)
    
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
    app.register_blueprint(prop_mascotas_bp)
    app.register_blueprint(veterinario_bp)
    app.register_blueprint(adopciones_bp)
    app.register_blueprint(contratos_bp)
    app.register_blueprint(habitaciones_hotel)
    app.register_blueprint(reservas)

    app.register_blueprint(peticiones_bp)

    ## Para desarrollo: crear tablas si no existen
    if not app.config.get("TESTING"):
        with app.app_context():
            from . import models
            from .models import Usuario
            print("Subclases de Usuario registradas:", Usuario.__subclasses__())
            db.create_all()
    
    
    ## EVENT LOOP + CLIENTE GLOBAL POR APP
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.async_loop = loop

    # Crea el cliente y servicios que lo usan
    app.space_client = SpaceClient(url="http://localhost:5403", api_key= Config.SPACE_API_KEY)
    #meter prueba y señalar si esta correcto
    
    # helper para usar funciones async desde las rutas sync
    def run_async(coro):
        #try:
        return app.async_loop.run_until_complete(coro)
        #except Exception as e:
        #    print("error:",str(e))
        #    return {'error': str(e)}, 500
            

    app.run_async = run_async
    
        # Función de cierre
    def shutdown_space_client():
        print("Cerrando SpaceClient...")
        try:
            app.run_async(app.space_client.close())
        finally:
            app.async_loop.close()

    app.shutdown_space_client = shutdown_space_client

    # Se llamará automáticamente cuando el proceso termine (excepto en tests)
    if not app.config.get("TESTING") and not os.environ.get("PYTEST_CURRENT_TEST"):
        atexit.register(shutdown_space_client)

    return app

