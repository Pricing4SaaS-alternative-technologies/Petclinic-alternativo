import os
import pytest
import time
import tempfile
from types import SimpleNamespace
from app import create_app, db
from app.models.mascota import Mascota
from app.models.prop_mascota import Prop_mascota
from app.models.clinica import Clinica
from app.models.prop_clinica import Prop_clinica
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    try:
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
            yield client
            with app.app_context():
                db.drop_all()
    finally:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture
def add_user(client):
    with client.application.app_context():
        # Generar IDs únicos basados en timestamp (limitados para que no superen restricciones)
        unique_id = str(int(time.time() * 100) % 1000000)
        
        # Crear propietario de clínica primero
        prop_clinica = Prop_clinica(
            first_name='Owner',
            last_name='Clinic',
            username=f'owner_clinic_{unique_id}',
            email=f'owner_{unique_id}@clinic.com',
            password='password123',
            telefono='123456789'
        )
        db.session.add(prop_clinica)
        db.session.flush()
        
        # Crear clínica
        clinica = Clinica(
            nombre=f'Clínica Test {unique_id}',
            direccion=f'Calle Test {unique_id}',
            telefono=f'{int(unique_id):09d}'[:9],
            propietario_id=prop_clinica.id
        )
        db.session.add(clinica)
        db.session.flush()
        
        # Crear usuario propietario de mascota
        user = Prop_mascota(
            first_name='Test',
            last_name='User',
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='password123',
            direccion=f'Calle Test {unique_id}',
            telefono='555555555',
            clinica_id=clinica.id
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id

@pytest.fixture
def auth(client, add_user):
    with client.application.app_context():
        # Asegurar que user_id es string para JWT
        access_token = create_access_token(identity=str(add_user))
    return access_token


@pytest.fixture
def space_client_allow(client):
    class FeatureEvaluators:
        @staticmethod
        def evaluate(*args, **kwargs):
            return SimpleNamespace(eval=True)

    class Contracts:
        @staticmethod
        def update_usage_levels(*args, **kwargs):
            return SimpleNamespace(ok=True)

    class SpaceClient:
        def __init__(self):
            self.featureEvaluators = FeatureEvaluators()
            self.contracts = Contracts()

        @staticmethod
        def close():
            return SimpleNamespace(ok=True)

    client.application.space_client = SpaceClient()
    client.application.run_async = lambda coro: coro
    return client


@pytest.fixture
def crear_mascota(client, auth):
    """Fixture para crear una mascota de prueba."""
    def _crear(**kwargs):
        data = {
            'nombre': 'Fido',
            'cumpleaños': '2020-01-01',
            'tipo': 'PERRO',
            **kwargs
        }
        return client.post('/api/mascotas/crear-mascota', json=data, 
                          headers={'Authorization': f'Bearer {auth}'})
    return _crear


@pytest.fixture
def mascota_id(client, auth, add_user, crear_mascota):
    """Fixture para obtener el ID de una mascota creada."""
    crear_mascota()
    with client.application.app_context():
        mascota = Mascota.query.filter_by(dueño_id=add_user).first()
        return mascota.id if mascota else None


def test_create_mascota_ok(client, auth, space_client_allow, crear_mascota):
    response = crear_mascota()
    assert response.status_code == 201


def test_create_mascota_faltan_campos(client, auth, space_client_allow):
    response = client.post('/api/mascotas/crear-mascota', json={
        'cumpleaños': '2020-01-01',
        'tipo': 'PERRO'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400

def test_create_mascota_sin_auth(client, space_client_allow):
    response = client.post('/api/mascotas/crear-mascota', json={
        'nombre': 'Fido',
        'cumpleaños': '2020-01-01',
        'tipo': 'PERRO'
    })
    assert response.status_code in [401, 422]


def test_get_mis_mascotas_ok(client, auth, space_client_allow, crear_mascota):
    crear_mascota()
    response = client.get('/api/mascotas/listar-tus-mascotas', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_mis_mascotas_sin_auth(client):
    response = client.get('/api/mascotas/listar-tus-mascotas')
    assert response.status_code in [401, 422]


def test_update_mascota_ok(client, auth, space_client_allow, mascota_id):
    response = client.patch(f'/api/mascotas/{mascota_id}', json={
        'nombre': 'Fido Actualizado'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200


def test_update_mascota_nombre_requerido(client, auth, space_client_allow, mascota_id):
    response = client.patch(f'/api/mascotas/{mascota_id}', json={}, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400

def test_update_mascota_sin_auth(client, space_client_allow, mascota_id):
    response = client.patch(f'/api/mascotas/{mascota_id}', json={
        'nombre': 'Fido Actualizado'
    })
    assert response.status_code in [401, 422]


def test_delete_mascota_ok(client, auth, space_client_allow, mascota_id):
    response = client.delete(f'/api/mascotas/{mascota_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200


def test_delete_mascota_no_encontrada(client, auth, space_client_allow):
    response = client.delete('/api/mascotas/999999', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_delete_mascota_sin_auth(client, space_client_allow, mascota_id):
    response = client.delete(f'/api/mascotas/{mascota_id}')
    assert response.status_code in [401, 422]
