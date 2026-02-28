import os
import pytest
import time
import tempfile
from types import SimpleNamespace
from datetime import date, datetime, timedelta
from app import create_app, db
from app.models.mascota import Mascota
from app.models.enums import EspecialidadEnum
from app.models.prop_mascota import Prop_mascota
from app.models.clinica import Clinica
from app.models.prop_clinica import Prop_clinica
from app.models.veterinario import Veterinario
from app.models.visita import Visita
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
def add_data(client):
    with client.application.app_context():
        unique_id = str(int(time.time() * 100) % 1000000)
        
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
        
        clinica = Clinica(
            nombre=f'Clínica Test {unique_id}',
            direccion=f'Calle Test {unique_id}',
            telefono=f'{int(unique_id):09d}'[:9],
            propietario_id=prop_clinica.id
        )
        db.session.add(clinica)
        db.session.flush()

        prop_mascota = Prop_mascota(
            first_name='Test',
            last_name='User',
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='password123',
            direccion=f'Calle Test {unique_id}',
            telefono='555555555',
            clinica_id=clinica.id
        )
        db.session.add(prop_mascota)
        db.session.flush()

        mascota = Mascota(
            nombre='Mascota de prueba',
            cumpleaños=date(2022, 1, 1),
            tipo='GATO',
            dueño_id=prop_mascota.id
        )
        db.session.add(mascota)
        db.session.flush()

        veterinario = Veterinario(
            first_name='Veterinario',
            last_name='Test',
            username=f'vet_{unique_id}',
            email=f'vet_{unique_id}@example.com',
            password='password123',
            especialidades=[EspecialidadEnum.CIRUGIA, EspecialidadEnum.DERMATOLOGIA],
            ciudad='Test City',
            clinica_id=clinica.id
        )
        db.session.add(veterinario)
        db.session.commit()

        return {
            'prop_mascota_id': prop_mascota.id,
            'prop_clinica_id': prop_clinica.id,
            'clinica_id': clinica.id,
            'mascota_id': mascota.id,
            'veterinario_id': veterinario.id
        }

@pytest.fixture
def auth_prop_mascota(client, add_data):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_data['prop_mascota_id']))
    return access_token

@pytest.fixture
def auth_veterinario(client, add_data):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_data['veterinario_id']))
    return access_token

@pytest.fixture(autouse=True)
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

# Tests para Crear Visita
def test_crear_visita_ok(client, auth_veterinario, add_data):
    data = {
        'mascota_id': add_data['mascota_id'],
        'fecha': (datetime.now() + timedelta(days=1)).isoformat(),
        'descripcion': 'Visita de prueba'
    }
    response = client.post('/api/visitas/crear', json=data, headers={'Authorization': f'Bearer {auth_veterinario}'})
    assert response.status_code == 201
    assert 'id' in response.json

def test_crear_visita_sin_auth(client, add_data):
    data = {'mascota_id': add_data['mascota_id'], 'fecha': (datetime.now() + timedelta(days=1)).isoformat(), 'descripcion': 'Visita de prueba'}
    response = client.post('/api/visitas/crear', json=data)
    assert response.status_code in [401, 422]

def test_crear_visita_campos_faltantes(client, auth_veterinario, add_data):
    data = {'mascota_id': add_data['mascota_id']}
    response = client.post('/api/visitas/crear', json=data, headers={'Authorization': f'Bearer {auth_veterinario}'})
    assert response.status_code == 400

# Tests para Listar Visitas
def test_listar_visitas_mascota_ok(client, auth_prop_mascota, add_data):
    response = client.get(f"/api/visitas/mascota/{add_data['mascota_id']}", headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_listar_visitas_mascota_sin_auth(client, auth_prop_mascota, add_data):
    response = client.get(f"/api/visitas/mascota/{add_data['mascota_id']}")
    assert response.status_code == 401

def test_listar_visitas_veterinario_ok(client, auth_veterinario, add_data):
    response = client.get(f"/api/visitas/veterinario/{add_data['veterinario_id']}", headers={'Authorization': f'Bearer {auth_veterinario}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_listar_visitas_veterinario_sin_auth(client, auth_veterinario, add_data):
    response = client.get(f"/api/visitas/veterinario/{add_data['veterinario_id']}")
    assert response.status_code == 401

# Tests para Actualizar Visita
def test_actualizar_visita_ok(client, auth_veterinario, add_data):
    # Primero, crea una visita para actualizar
    with client.application.app_context():
        visita = Visita(fecha=(datetime.now() + timedelta(days=1)), descripcion='Visita original', mascota_id=add_data['mascota_id'])
        visita.veterinario_id=add_data['veterinario_id']
        db.session.add(visita)
        db.session.commit()
        visita_id = visita.id

    data = {
        'fecha': (datetime.now() + timedelta(days=2)).isoformat(),
        'descripcion': 'Visita actualizada'
    }
    response = client.patch(f'/api/visitas/actualizar/{visita_id}', json=data, headers={'Authorization': f'Bearer {auth_veterinario}'})
    assert response.status_code == 200
    assert 'Actualizada' in response.json['msg']

def test_actualizar_visita_sin_auth(client, auth_veterinario, add_data):
    # Primero, crea una visita para actualizar
    with client.application.app_context():
        visita = Visita(fecha=(datetime.now() + timedelta(days=1)), descripcion='Visita original', mascota_id=add_data['mascota_id'])
        visita.veterinario_id=add_data['veterinario_id']
        db.session.add(visita)
        db.session.commit()
        visita_id = visita.id

    data = {
        'fecha': (datetime.now() + timedelta(days=2)).isoformat(),
        'descripcion': 'Visita actualizada'
    }
    response = client.patch(f'/api/visitas/actualizar/{visita_id}', json=data)
    assert response.status_code == 401

# Tests para Eliminar Visita
def test_eliminar_visita_ok(client, auth_veterinario, add_data):
    # Primero, crea una visita para eliminar
    with client.application.app_context():
        visita = Visita(fecha=(datetime.now() + timedelta(days=1)), descripcion='Visita a eliminar', mascota_id=add_data['mascota_id'])
        visita.veterinario_id=add_data['veterinario_id']
        db.session.add(visita)
        db.session.commit()
        visita_id = visita.id

    response = client.delete(f'/api/visitas/eliminar/{visita_id}', headers={'Authorization': f'Bearer {auth_veterinario}'})
    assert response.status_code == 200
    assert 'Eliminada' in response.json['msg']

def test_eliminar_visita_sin_auth(client, auth_veterinario, add_data):
    # Primero, crea una visita para eliminar
    with client.application.app_context():
        visita = Visita(fecha=(datetime.now() + timedelta(days=1)), descripcion='Visita a eliminar', mascota_id=add_data['mascota_id'])
        visita.veterinario_id=add_data['veterinario_id']
        db.session.add(visita)
        db.session.commit()
        visita_id = visita.id

    response = client.delete(f'/api/visitas/eliminar/{visita_id}')
    assert response.status_code == 401