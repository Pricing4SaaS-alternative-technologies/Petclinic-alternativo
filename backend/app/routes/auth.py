# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import Usuario

from app.extensions import db

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/register', methods=['POST'])
def register():
    ## conseguimos los datos
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    ## podriamos hacerlo mas especifico buscando si existe el username y despues si existe el email, devolviendo errores diferentes
    existing_user = Usuario.find_by_username_or_email(username, email)
    if existing_user:
        return jsonify({'message': 'El usuario o email ya está en uso'}), 400

    ## Crear un nuevo usuario
    new_user = Usuario(username=username, email=email, password=password)
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

    ## usamos la función q hicimos antes
    user = Usuario.find_by_username_or_email(username_or_email, username_or_email)
    
    ##TODO: cambiar esto por el check_password
    ## si se mete el check password al final, hay q cambiar aqui el metodo
    if not user or (password != user.password):
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
    ## Ejemplo de ruta protegida con JWT
    current_user_id = get_jwt_identity()
    user = Usuario.query.get(current_user_id)
    return jsonify({
        'message': f'Bienvenido, {user.username}',
        'user_id': current_user_id
    }), 200
