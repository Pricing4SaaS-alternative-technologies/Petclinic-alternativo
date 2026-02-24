# backend/app/__init__.py
import os
import threading
import asyncio
import atexit
from app.config import Config
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app_SpacePyCl.routes.config import SpaceClient

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

# 1. Creamos el loop global permanente
_global_async_loop = asyncio.new_event_loop()

# 2. Definimos la función que mantendrá el loop vivo en un hilo secundario
def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# 3. Arrancamos el hilo secundario (daemon=True hace que se cierre solo al apagar Flask)
_loop_thread = threading.Thread(target=_start_background_loop, args=(_global_async_loop,), daemon=True)
_loop_thread.start()

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
    app.register_blueprint(prop_mascotas_bp)
    app.register_blueprint(veterinario_bp)
    app.register_blueprint(adopciones_bp)
    app.register_blueprint(contratos_bp)
    app.register_blueprint(habitaciones_hotel)
    app.register_blueprint(reservas)
    app.register_blueprint(peticiones_bp)

    ## Para desarrollo: crear tablas si no existen
    with app.app_context():
        from . import models
        from .models import Usuario
        print("Subclases de Usuario registradas:", Usuario.__subclasses__())
        db.create_all()
    
    # 4. Helper mágico: Envía las corrutinas al hilo secundario de forma segura
    def run_async(coro):
        future = asyncio.run_coroutine_threadsafe(coro, _global_async_loop)
        return future.result()

    app.run_async = run_async
    
    # 5. Inicializamos el SpaceClient DENTRO del loop del hilo secundario
    # Así su sesión HTTP "nace" atada al loop correcto que nunca se cierra
    async def init_client():
        return SpaceClient(url="http://localhost:5403", api_key=Config.SPACE_API_KEY)
        
    app.space_client = run_async(init_client())
    
    # 6. Función de cierre
    def shutdown_space_client():
        print("Cerrando SpaceClient...")
        try:
            run_async(app.space_client.close())
        except Exception as e:
            print(f"Error al cerrar SpaceClient: {e}")

    app.shutdown_space_client = shutdown_space_client

    # Se llamará automáticamente cuando el proceso termine
    atexit.register(shutdown_space_client)

    return app