from flask import Blueprint, jsonify
from app.models.clinica import Clinica

clinicas_bp = Blueprint('clinicas', __name__, url_prefix='/api/clinicas')

@clinicas_bp.route('', methods=['GET'])
def get_clinicas():
    clinicas = Clinica.query.all()
    return jsonify([
        {
            'id': c.id,
            'nombre': c.name
        }
        for c in clinicas
    ])
