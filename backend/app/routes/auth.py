# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import Usuario
from app.extensions import db

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/register', methods=['POST'])
def register():
    ## Conseguir los datos del request
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    ## Comprobar si ya existe el usuario o email
    existing_user = Usuario.find_by_username_or_email(username, email)
    if existing_user:
        return jsonify({'message': 'El usuario o email ya está en uso'}), 400

    ## Crear un nuevo usuario
    new_user = Usuario(username=username, email=email, password=password)
    ## Hashear la contraseña antes de guardar
    new_user.hash_password()

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    ## Buscar usuario por username o email
    user = Usuario.find_by_username_or_email(username_or_email, username_or_email)
    
    ## Usar check_password para validar la contraseña
    if not user or not user.check_password(password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    ## Crear el token JWT
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = Usuario.query.get(current_user_id)
    return jsonify({
        'message': f'Bienvenido, {user.username}',
        'user_id': current_user_id
    }), 200
