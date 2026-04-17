import os
import pytest
import time
import tempfile
from app import create_app, db
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
def add_prop_clinica(client):
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
        db.session.commit()
        return prop_clinica.id

@pytest.fixture
def auth(client, add_prop_clinica):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_prop_clinica))
    return access_token

from types import SimpleNamespace
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

@pytest.fixture
def crear_clinica(client, auth):
    def _crear(**kwargs):
        data = {
            'nombre': 'Clinica Test',
            'direccion': 'Calle Falsa 123',
            'telefono': '123456789',
            **kwargs
        }
        return client.post('/api/clinicas/crear', json=data, headers={'Authorization': f'Bearer {auth}'})
    return _crear

def test_create_clinica_ok(client, auth, crear_clinica):
    response = crear_clinica()
    assert response.status_code == 201

def test_create_clinica_faltan_campos(client, auth):
    response = client.post('/api/clinicas/crear', json={
        'nombre': 'Clinica Test',
        'telefono': '123456789'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400

def test_create_clinica_telefono_invalido(client, auth):
    response = client.post('/api/clinicas/crear', json={
        'nombre': 'Clinica Test',
        'direccion': 'Calle Falsa 123',
        'telefono': 'abc123456'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400

def test_create_clinica_sin_auth(client):
    response = client.post('/api/clinicas/crear', json={
        'nombre': 'Clinica Test',
        'direccion': 'Calle Falsa 123',
        'telefono': '123456789'
    })
    assert response.status_code in [401, 422]

def test_get_clinica_ok(client, auth, crear_clinica):
    crear_clinica(nombre='Clinica Test 1', direccion='Calle Uno', telefono='123456789')
    response = client.get('/api/clinicas/listar-todas', headers={'Authorization': f'Bearer {auth}'} )
    assert response.status_code == 200
    clinicas = response.json
    assert isinstance(clinicas, list)
    assert len(clinicas) > 0

def test_get_clinicas_sin_auth(client):
    response = client.get('/api/clinicas/listar-todas')
    assert response.status_code == 200 # Es necesario permitir el acceso sin autenticación para listar las clínicas
    assert isinstance(response.json, list)

def test_update_clinica_ok(client, auth, crear_clinica):
    response = crear_clinica()
    assert response.status_code == 201, f"La clínica no se creó correctamente: {response.json}"
    clinica_id = response.json.get('clinica_id')
    assert clinica_id is not None, "No se devolvió el ID de la clínica creada"
    response = client.put(f'/api/clinicas/editar/{clinica_id}', json={
        'nombre': 'Clinica Actualizada'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 201, f"La clínica no se actualizó correctamente: {response.json}"

def test_update_clinica_no_encontrada(client, auth):
    response = client.put('/api/clinicas/editar/999999', json={
        'nombre': 'Clinica Actualizada'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_update_clinica_telefono_invalido(client, auth, crear_clinica):
    response = crear_clinica()
    assert response.status_code == 201, f"La clínica no se creó correctamente: {response.json}"
    clinica_id = response.json.get('clinica_id')
    assert clinica_id is not None, "No se devolvió el ID de la clínica creada"
    response = client.put(f'/api/clinicas/editar/{clinica_id}', json={
        'telefono': 'abc123456'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400, f"La clínica aceptó un teléfono inválido: {response.json}"

def test_delete_clinica_ok(client, auth, crear_clinica):
    response = crear_clinica()
    assert response.status_code == 201, f"La clínica no se creó correctamente: {response.json}"
    clinica_id = response.json.get('clinica_id')
    assert clinica_id is not None, "No se devolvió el ID de la clínica creada"
    response = client.delete(f'/api/clinicas/eliminar/{clinica_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200, f"La clínica no se eliminó correctamente: {response.json}"

def test_delete_clinica_no_encontrada(client, auth):
    response = client.delete('/api/clinicas/eliminar/999999', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404
