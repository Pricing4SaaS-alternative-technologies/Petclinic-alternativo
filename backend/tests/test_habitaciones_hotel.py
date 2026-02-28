import os
import pytest
import time
import tempfile
import json
from app import create_app, db
from app.models.habitacion_hotel import Habitacion_hotel
from app.models.clinica import Clinica
from app.models.prop_clinica import Prop_clinica
from flask_jwt_extended import create_access_token
from types import SimpleNamespace

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
def add_prop_clinica_and_clinica(client):
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

        clinica = Clinica(
            nombre=f'Clinica Test {unique_id}',
            direccion='Calle Falsa 123',
            telefono='987654321',
            propietario_id=prop_clinica.id
        )
        db.session.add(clinica)
        db.session.commit()
        return {'prop_clinica_id': prop_clinica.id, 'clinica_id': clinica.id}

@pytest.fixture
def auth(client, add_prop_clinica_and_clinica):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_prop_clinica_and_clinica['prop_clinica_id']))
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

@pytest.fixture
def crear_habitacion(client, auth, add_prop_clinica_and_clinica):
    def _crear(**kwargs):
        clinica_id = add_prop_clinica_and_clinica['clinica_id']
        data = {
            'nombre': 'Habitacion Canina 1',
            'reservable': True,
            'tamaño': 'KING_SIZE',
            'tipo': 'PERRO',
            'clinica_id': clinica_id,
            **kwargs
        }
        return client.post('/api/habitaciones_hotel/crear-habitacion', json=data, headers={'Authorization': f'Bearer {auth}'})
    return _crear

def test_create_habitacion_ok(crear_habitacion):
    response = crear_habitacion()
    assert response.status_code == 201
    assert response.json['nombre'] == 'Habitacion Canina 1'

def test_create_habitacion_missing_fields(client, auth, add_prop_clinica_and_clinica):
    clinica_id = add_prop_clinica_and_clinica['clinica_id']
    data = {
        # 'nombre' is missing
        'reservable': True,
        'tamaño': 'KING_SIZE',
        'tipo': 'PERRO',
        'clinica_id': clinica_id
    }
    response = client.post('/api/habitaciones_hotel/crear-habitacion', json=data, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400
    assert 'Nombre requerido' in response.json['msg']

def test_create_habitacion_sin_auth(client, add_prop_clinica_and_clinica):
    clinica_id = add_prop_clinica_and_clinica['clinica_id']
    data = {
        'nombre': 'Habitacion Sin Auth',
        'reservable': True,
        'tamaño': 'KING_SIZE',
        'tipo': 'PERRO',
        'clinica_id': clinica_id
    }
    response = client.post('/api/habitaciones_hotel/crear-habitacion', json=data)
    assert response.status_code in [401, 422]

def test_get_habitaciones_by_prop_clinica(client, auth, add_prop_clinica_and_clinica, crear_habitacion):
    crear_habitacion()
    prop_clinica_id = add_prop_clinica_and_clinica['prop_clinica_id']
    response = client.get(f'/api/habitaciones_hotel/listar/prop-clinica/{prop_clinica_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_get_habitacion_details_ok(client, auth, crear_habitacion):
    response = crear_habitacion(nombre='Habitacion Felina 1', tamaño='ACOGEDOR', tipo='GATO')
    assert response.status_code == 201
    habitacion_id = response.json['id']

    response = client.get(f'/api/habitaciones_hotel/detalles/{habitacion_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert response.json['nombre'] == 'Habitacion Felina 1'

def test_get_habitacion_details_not_found(client, auth):
    response = client.get('/api/habitaciones_hotel/detalles/999999', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_update_habitacion_ok(client, auth, crear_habitacion):
    response = crear_habitacion(nombre='Habitacion para Actualizar')
    assert response.status_code == 201
    habitacion_id = response.json['id']

    update_data = {'nombre': 'Habitacion Actualizada'}
    response = client.put(f'/api/habitaciones_hotel/editar/{habitacion_id}', json=update_data, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert response.json['msg'] == 'Habitación actualizada con éxito'

    # Verify the update
    response = client.get(f'/api/habitaciones_hotel/detalles/{habitacion_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert response.json['nombre'] == 'Habitacion Actualizada'

def test_update_habitacion_not_found(client, auth):
    update_data = {'nombre': 'Habitacion Inexistente'}
    response = client.put('/api/habitaciones_hotel/editar/999999', json=update_data, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_delete_habitacion_fail_if_reservable(client, auth, crear_habitacion):
    response = crear_habitacion(nombre='Habitacion a Borrar (Reservable)', reservable=True)
    assert response.status_code == 201
    habitacion_id = response.json['id']

    response = client.delete(f'/api/habitaciones_hotel/eliminar/{habitacion_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 400
    assert 'No se puede eliminar una habitación que está marcada como reservable' in response.json['msg']

def test_delete_habitacion_ok(client, auth, crear_habitacion):
    response = crear_habitacion(nombre='Habitacion a Borrar (No Reservable)', reservable=False)
    assert response.status_code == 201
    habitacion_id = response.json['id']

    response = client.delete(f'/api/habitaciones_hotel/eliminar/{habitacion_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    assert response.json['msg'] == 'Habitación eliminada con éxito'

    # Verify it's deleted
    response = client.get(f'/api/habitaciones_hotel/detalles/{habitacion_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_delete_habitacion_not_found(client, auth):
    response = client.delete('/api/habitaciones_hotel/eliminar/999999', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 404

def test_delete_habitacion_sin_auth(client, crear_habitacion):
    response = crear_habitacion(nombre='Habitacion a Borrar Sin Auth', reservable=False)
    assert response.status_code == 201
    habitacion_id = response.json['id']
    
    response = client.delete(f'/api/habitaciones_hotel/eliminar/{habitacion_id}')
    assert response.status_code in [401, 422]
