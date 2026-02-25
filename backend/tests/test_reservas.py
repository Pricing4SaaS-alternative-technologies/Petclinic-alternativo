import os
import pytest
import time
import tempfile
from types import SimpleNamespace
from datetime import date, timedelta
from app import create_app, db
from app.models.mascota import Mascota
from app.models.prop_mascota import Prop_mascota
from app.models.clinica import Clinica
from app.models.prop_clinica import Prop_clinica
from app.models.reserva import Reserva
from app.models.habitacion_hotel import Habitacion_hotel
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

        # Clinica 2 para pruebas de acceso no autorizado
        prop_clinica_2 = Prop_clinica(first_name='Otro Dueño', last_name='Clinica', username=f'otro_dueño_{unique_id}', email=f'otro_{unique_id}@dueño.com', password='password123', telefono='987654321')
        db.session.add(prop_clinica_2)
        db.session.flush()
        clinica_2 = Clinica(nombre=f'Clínica 2 {unique_id}', direccion='Otra Calle 123', telefono='112233445', propietario_id=prop_clinica_2.id)
        db.session.add(clinica_2)
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

        habitacion = Habitacion_hotel(
            nombre='Habitación de prueba',
            reservable=True,
            tamaño='KING_SIZE',
            tipo='GATO',
            clinica_id=clinica.id
        )
        db.session.add(habitacion)
        habitacion_no_reservable = Habitacion_hotel(nombre='Habitación no reservable', reservable=False, tamaño='KING_SIZE', tipo='GATO', clinica_id=clinica.id)
        db.session.add(habitacion_no_reservable)
        db.session.commit()

        return {
            'prop_mascota_id': prop_mascota.id,
            'prop_clinica_id': prop_clinica.id,
            'prop_clinica_2_id': prop_clinica_2.id,
            'clinica_id': clinica.id,
            'clinica_2_id': clinica_2.id,
            'mascota_id': mascota.id,
            'habitacion_id': habitacion.id,
            'habitacion_no_reservable_id': habitacion_no_reservable.id
        }

@pytest.fixture
def auth_prop_mascota(client, add_data):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_data['prop_mascota_id']))
    return access_token

@pytest.fixture
def auth_prop_clinica(client, add_data):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_data['prop_clinica_id']))
    return access_token

@pytest.fixture
def auth_prop_clinica_2(client, add_data):
    with client.application.app_context():
        access_token = create_access_token(identity=str(add_data['prop_clinica_2_id']))
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

# Tests para Crear Reserva

def test_crear_reserva_ok(client, auth_prop_mascota, add_data):
    data = {
        'mascota_id': add_data['mascota_id'],
        'habitacion_hotel_id': add_data['habitacion_id'],
        'fecha_inicio': (date.today() + timedelta(days=1)).isoformat(),
        'fecha_fin': (date.today() + timedelta(days=3)).isoformat()
    }
    response = client.post('/api/reservas/crear', json=data, headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 201
    assert 'Reserva creada exitosamente' in response.json['message']

def test_crear_reserva_sin_auth(client, add_data):
    data = {'mascota_id': add_data['mascota_id'], 'habitacion_hotel_id': add_data['habitacion_id'], 'fecha_inicio': '2025-01-01', 'fecha_fin': '2025-01-03'}
    response = client.post('/api/reservas/crear', json=data)
    assert response.status_code in [401, 422]

def test_crear_reserva_campos_faltantes(client, auth_prop_mascota, add_data):
    data = {'mascota_id': add_data['mascota_id']}
    response = client.post('/api/reservas/crear', json=data, headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 400

def test_crear_reserva_fecha_invalida(client, auth_prop_mascota, add_data):
    data = {'mascota_id': add_data['mascota_id'], 'habitacion_hotel_id': add_data['habitacion_id'], 'fecha_inicio': 'fecha-invalida', 'fecha_fin': '2025-01-03'}
    response = client.post('/api/reservas/crear', json=data, headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 400

def test_crear_reserva_habitacion_ocupada(client, auth_prop_mascota, add_data):
    reserva_existente = Reserva(mascota_id=add_data['mascota_id'], habitacion_id=add_data['habitacion_id'], fecha_inicio=date.today() + timedelta(days=5), fecha_fin=date.today() + timedelta(days=10))
    with client.application.app_context():
        db.session.add(reserva_existente)
        db.session.commit()

    data = {'mascota_id': add_data['mascota_id'], 'habitacion_hotel_id': add_data['habitacion_id'], 'fecha_inicio': (date.today() + timedelta(days=6)).isoformat(), 'fecha_fin': (date.today() + timedelta(days=8)).isoformat()}
    response = client.post('/api/reservas/crear', json=data, headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 400
    assert 'La habitación ya está reservada' in response.json['message']

# Tests para Listar Mis Reservas

def test_listar_mis_reservas_ok(client, auth_prop_mascota, add_data):
    with client.application.app_context():
        reserva = Reserva(mascota_id=add_data['mascota_id'], habitacion_id=add_data['habitacion_id'], fecha_inicio=date.today() + timedelta(days=1), fecha_fin=date.today() + timedelta(days=3))
        db.session.add(reserva)
        db.session.commit()
    response = client.get('/api/reservas/mis_reservas', headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_listar_mis_reservas_sin_auth(client):
    response = client.get('/api/reservas/mis_reservas')
    assert response.status_code in [401, 422]

# Tests para Listar Reservas por Habitación

def test_listar_reservas_habitacion_ok(client, auth_prop_clinica, add_data):
    with client.application.app_context():
        reserva = Reserva(mascota_id=add_data['mascota_id'], habitacion_id=add_data['habitacion_id'], fecha_inicio=date.today() + timedelta(days=1), fecha_fin=date.today() + timedelta(days=3))
        db.session.add(reserva)
        db.session.commit()
    response = client.get(f"/api/reservas/habitacion/{add_data['habitacion_id']}", headers={'Authorization': f'Bearer {auth_prop_clinica}'})
    assert response.status_code == 200
    assert 'reservas' in response.json
    assert len(response.json['reservas']) > 0

def test_listar_reservas_habitacion_sin_auth(client, add_data):
    response = client.get(f"/api/reservas/habitacion/{add_data['habitacion_id']}")
    assert response.status_code in [401, 422]

# Tests para Listar Mis Habitaciones Reservadas

def test_listar_mis_habitaciones_reservas_ok(client, auth_prop_mascota, add_data):
    with client.application.app_context():
        reserva = Reserva(mascota_id=add_data['mascota_id'], habitacion_id=add_data['habitacion_id'], fecha_inicio=date.today() + timedelta(days=1), fecha_fin=date.today() + timedelta(days=3))
        db.session.add(reserva)
        db.session.commit()
    response = client.get('/api/reservas/mis_habs_reservas', headers={'Authorization': f'Bearer {auth_prop_mascota}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['id'] == add_data['habitacion_id']

def test_listar_mis_habitaciones_reservas_sin_auth(client):
    response = client.get('/api/reservas/mis_habs_reservas')
    assert response.status_code in [401, 422]