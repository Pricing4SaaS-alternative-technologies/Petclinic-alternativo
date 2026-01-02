from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.enums import TipoUsuarioEnum
from app.extensions import db
from app.models.visita import Visita

veterinario_bp = Blueprint('vet_visitas', __name__, url_prefix='/api/visitas')

@veterinario_bp.route('/mine', methods=['GET'])
@jwt_required()
def listar_visitas_mias():
    vet_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(vet_id)
    if usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO:
        return jsonify({'msg': 'No autorizado'}), 403
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