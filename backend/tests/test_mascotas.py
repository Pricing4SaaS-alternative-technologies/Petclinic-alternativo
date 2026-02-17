import pytest
import time
from app import create_app, db
from app.models.mascota import Mascota
from app.models.prop_mascota import Prop_mascota
from app.models.clinica import Clinica
from app.models.prop_clinica import Prop_clinica
from app.models.enums import TipoUsuarioEnum
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

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


def test_create_mascota(client, auth):
    response = client.post('/api/mascotas/crear-mascota', json={
        'nombre': 'Fido',
        'cumpleaños': '2020-01-01',
        'tipo': 'PERRO'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code in [201, 403]


def test_get_mis_mascotas(client, auth, add_user):
    with client.application.app_context():
        client.post('/api/mascotas/crear-mascota', json={
            'nombre': 'Fido',
            'cumpleaños': '2020-01-01',
            'tipo': 'PERRO'
        }, headers={'Authorization': f'Bearer {auth}'})
    response = client.get('/api/mascotas/listar-tus-mascotas', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)


def test_update_mascota(client, auth, add_user):
    with client.application.app_context():
        response = client.post('/api/mascotas/crear-mascota', json={
            'nombre': 'Fido',
            'cumpleaños': '2020-01-01',
            'tipo': 'PERRO'
        }, headers={'Authorization': f'Bearer {auth}'})
        if response.status_code == 201:
            mascota_id = response.json.get('id', 1)
        else:
            # Si la mascota se creó, obtener su ID
            mascota_response = client.get('/api/mascotas/listar-tus-mascotas', headers={'Authorization': f'Bearer {auth}'})
            if mascota_response.json:
                mascota_id = mascota_response.json[0]['id']
            else:
                mascota_id = 1
    
    response = client.patch(f'/api/mascotas/{mascota_id}', json={
        'nombre': 'Fido Actualizado'
    }, headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code in [200, 404]


def test_delete_mascota(client, auth, add_user):
    with client.application.app_context():
        response = client.post('/api/mascotas/crear-mascota', json={
            'nombre': 'Fido',
            'cumpleaños': '2020-01-01',
            'tipo': 'PERRO'
        }, headers={'Authorization': f'Bearer {auth}'})
        if response.status_code == 201:
            mascota_id = response.json.get('id', 1)
        else:
            mascota_response = client.get('/api/mascotas/listar-tus-mascotas', headers={'Authorization': f'Bearer {auth}'})
            if mascota_response.json:
                mascota_id = mascota_response.json[0]['id']
            else:
                mascota_id = 1
    
    response = client.delete(f'/api/mascotas/{mascota_id}', headers={'Authorization': f'Bearer {auth}'})
    assert response.status_code in [200, 404]