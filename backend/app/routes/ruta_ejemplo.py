# backend/app/routes.py
from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required

from ..models.ejemplo import Ejemplo

main = Blueprint('main', __name__)

@main.route('/api/v1.0/mensaje', methods=['GET'])
@jwt_required()
def get_message():
    message = Ejemplo.query.first()
    if message:
        return jsonify(message.text)
    return jsonify("Estas loggueado y por eso ves este mensaje")

@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def render_vue(path):
    return render_template("index.html")
