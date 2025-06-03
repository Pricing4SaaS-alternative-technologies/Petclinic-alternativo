# backend/app/routes.py

from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.ejemplo import Ejemplo
from ..models.usuario import Usuario

main = Blueprint('main', __name__)

@main.route('/api/v1.0/mensaje', methods=['GET'])
@jwt_required()
def get_message():
    identity = get_jwt_identity()
    user = Usuario.query.get(int(identity))
    
    message = Ejemplo.query.first()
    if message:
        return jsonify(message.text)
    return jsonify({
        'message': f'Bienvenido, {user.usuario}, si estas viendo esto estas loggeado de forma correcta con JWT',
        'tipo': f'Actualmente eres un usuario de tipo {user.tipo_usuario.value}',
        'user_id': int(identity)
    })

