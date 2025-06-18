from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.visita import Visita

prop_clinicas_bp = Blueprint('prop_clinicas', __name__, url_prefix='/api/visitas')

@prop_clinicas_bp.route('/mine', methods=['GET'])
@jwt_required()
def listar_visitas_mias():
    vet_id = get_jwt_identity()
    visitas = Visita.query.filter_by(veterinario_id=vet_id).all()
    result = [
      {
        'id': v.id,
        'date_time': v.date_time.isoformat(),
        'description': v.description,
        'mascota_id': v.mascota_id,
        'clinica_id':  v.clinica_id,             
        'dueno_id':    v.mascota.dueño.id,
        'dueno': v.mascota.dueño.usuario,
        'mascota': v.mascota.nombre
      }
      for v in visitas
    ]
    return jsonify(result), 200