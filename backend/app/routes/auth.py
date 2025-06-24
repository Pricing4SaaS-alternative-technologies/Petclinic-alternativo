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
    tipo_str = data.get('tipo_usuario')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    usuario = data.get('usuario')
    email = data.get('email')
    contraseña = data.get('contraseña')

    if not tipo_str or not all([nombre, apellidos, usuario, email, contraseña]):
        return jsonify({'message': 'Faltan datos obligatorios'}), 400

    # Validar tipo
    try:
        tipo_enum = TipoUsuarioEnum[tipo_str]
        if tipo_enum == TipoUsuarioEnum.USUARIO:
            return jsonify({'message': 'Tipo de usuario no permitido'}), 400
    except KeyError:
        return jsonify({'message': 'Tipo de usuario inválido'}), 400
    
    # Comprobar si ya existe usuario
    if Usuario.find_by_usuario_or_email(usuario, email):
        return jsonify({'message': 'Usuario o email ya registrado'}), 400

    # Crear instancia según tipo
    user = None

    if tipo_enum == TipoUsuarioEnum.PROP_MASCOTA:
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        clinica = data.get('clinica_id')
        
        if not direccion or not telefono or not clinica:
            return jsonify({'message': 'No estan rellenos los campos obligatorios para dueño de mascota'}), 400
        user = Prop_mascota(nombre, apellidos, usuario, email, contraseña, direccion, telefono, clinica)

    elif tipo_enum == TipoUsuarioEnum.VETERINARIO:
        ciudad = data.get('ciudad')
        especialidades_raw = data.get('especialidades', [])
        valores_validos = [e.value for e in EspecialidadEnum]
        
        if not all(e in valores_validos for e in especialidades_raw):
            return jsonify({'message': 'Algunas especialidades no son válidas'}), 400
        
        clinica = data.get('clinica_id')
        try:
            especialidades_enum = [EspecialidadEnum(e) for e in especialidades_raw]
        except ValueError:
            return jsonify({'message': 'Especialidades inválidas'}), 400
        user = Veterinario(nombre, apellidos, usuario, email, contraseña, especialidades_enum, ciudad, clinica)

    elif tipo_enum == TipoUsuarioEnum.PROP_CLINICA:
        user = Prop_clinica(nombre, apellidos, usuario, email, contraseña)

    if user is None:
        return jsonify({'message': 'Error al crear el usuario'}), 500

    user.save()
    return jsonify({'message': f'{tipo_enum.value.capitalize()} registrado con éxito'}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_o_mail = data.get('usuario_o_email')
    contraseña = data.get('contraseña')

    if not user_o_mail or not contraseña:
        return jsonify({'message': 'Faltan datos'}), 400

    usuario = Usuario.find_by_usuario_or_email(user_o_mail, user_o_mail)

    if not usuario or not usuario.check_password(contraseña):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Incluir tipo en el token
    access_token = create_access_token(identity=str(usuario.id))
    usuario_payload = {
        'id': usuario.id,
        'usuario': usuario.usuario,
        'email': usuario.email,
        'tipo': usuario.tipo_usuario.value
    }
    if usuario.tipo_usuario in (TipoUsuarioEnum.VETERINARIO, TipoUsuarioEnum.PROP_MASCOTA):
        usuario_payload['clinica_id'] = usuario.clinica_id

    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'usuario': usuario_payload
    }), 200


@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    usuario = Usuario.query.get(identity)
    return jsonify({
        'message': f'Bienvenido, {usuario.usuario}',
        'tipo': usuario.tipo_usuario.value,
        'user_id': identity["id"]
    }), 200


@auth.route('/especialidades', methods=['GET'])
def get_especialidades():
    from app.models.enums import EspecialidadEnum
    return jsonify([e.value for e in EspecialidadEnum])