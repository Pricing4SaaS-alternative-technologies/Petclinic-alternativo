# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models import Usuario, Prop_mascota, Veterinario, Prop_clinica
from app.models.enums import TipoUsuarioEnum, EspecialidadEnum

auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # print(data)
    # datos del usuario basico
    tipo_str = data.get('type')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not tipo_str or not all([first_name, last_name, username, email, password]):
        return jsonify({'message': 'Faltan datos obligatorios'}), 400

    # Validar tipo
    try:
        tipo_enum = TipoUsuarioEnum[tipo_str]
        if tipo_enum == TipoUsuarioEnum.USUARIO:
            return jsonify({'message': 'Tipo de usuario no permitido'}), 400
    except KeyError:
        return jsonify({'message': 'Tipo de usuario inválido'}), 400
    
    # Comprobar si ya existe usuario
    if Usuario.find_by_username_or_email(username, email):
        return jsonify({'message': 'Usuario o email ya registrado'}), 400

    # Crear instancia según tipo
    user = None

    if tipo_enum == TipoUsuarioEnum.PROP_MASCOTA:
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        if not direccion or not telefono:
            return jsonify({'message': 'No estan rellenos los campos obligatorios para dueño de mascota'}), 400
        user = Prop_mascota(first_name, last_name, username, email, password, direccion, telefono)

    elif tipo_enum == TipoUsuarioEnum.VETERINARIO:
        ciudad = data.get('ciudad')
        especialidades_raw = data.get('especialidades', [])
        try:
            especialidades_enum = [EspecialidadEnum(e.strip()) for e in especialidades_raw.split(",")]
            print("enum de especialidades",especialidades_enum)
        except ValueError:
            return jsonify({'message': 'Especialidades inválidas'}), 400
        user = Veterinario(first_name, last_name, username, email, password, especialidades_enum, ciudad)

    elif tipo_enum == TipoUsuarioEnum.PROP_CLINICA:
        user = Prop_clinica(first_name, last_name, username, email, password)

    if user is None:
        return jsonify({'message': 'Error al crear el usuario'}), 500

    user.save()
    return jsonify({'message': f'{tipo_enum.value.capitalize()} registrado con éxito'}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    user = Usuario.find_by_username_or_email(username_or_email, username_or_email)

    if not user or not user.check_password(password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Incluir tipo en el token
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'tipo': user.type.value
        }
    }), 200


@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    user = Usuario.query.get(identity)
    return jsonify({
        'message': f'Bienvenido, {user.username}',
        'tipo': user.type.value,
        'user_id': identity["id"]
    }), 200
