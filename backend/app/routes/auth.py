# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, db  # Asegúrate de que la ruta sea correcta

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/register', methods=['POST'])
def register():
    #conseguimos los dato
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Faltan datos'}), 400

    # podriamos hacerlo mas especifico buscando si existe el usernam y dsps si existe el email, devolviendo errores diferentes
    existing_user = User.find_by_username_or_email(username, email)
    if existing_user:
        return jsonify({'message': 'El usuario o email ya está en uso'}), 400

    # Crear un nuevo usuario
    new_user = User(username=username, email=email, password=password)
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

    # usamos la función q hicimos antes
    user = User.find_by_username_or_email(username_or_email, username_or_email)

    if not user or not (password == user.password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Crear el token JWT
    access_token = create_access_token(identity=user.id)

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
    # Ejemplo de ruta protegida con JWT
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'message': f'Bienvenido, {user.username}',
        'user_id': current_user_id
    }), 200
