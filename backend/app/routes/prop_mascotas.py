from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.clinica import Clinica
from app.models.prop_mascota import Usuario, TipoUsuarioEnum, Prop_mascota
from app.models.mascota import Mascota
from app.models.visita import Visita

prop_mascotas_bp = Blueprint('prop_mascotas', __name__,
    url_prefix='/api/clinicas/<int:clinica_id>/props_mascotas'
)

@prop_mascotas_bp.route('', methods=['GET'])
@jwt_required()
def listar_propietarios(clinica_id):
    Clinica.query.get_or_404(clinica_id)
    props = Prop_mascota.query.filter_by(clinica_id=clinica_id).all()
    return jsonify([{'id': p.id, 'usuario': p.usuario} for p in props]), 200

@prop_mascotas_bp.route('/<int:prop_id>/mascotas', methods=['GET'])
@jwt_required()
def listar_mascotas_propietario(clinica_id, prop_id):
    Clinica.query.get_or_404(clinica_id)
    Prop_mascota.query.filter_by(id=prop_id, clinica_id=clinica_id).first_or_404()
    mascotas = Mascota.query.filter_by(dueño_id=prop_id).all()
    return jsonify([{'id': m.id, 'nombre': m.nombre} for m in mascotas]), 200

@prop_mascotas_bp.route('/mine/visitas', methods=['GET'])
@jwt_required()
def listar_visitas_propietario(clinica_id):
    # 1) obtenemos usuario y comprobamos rol
    user_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(user_id)
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg': 'No autorizado'}), 403
    visitas = (
      Visita.query
            .join(Visita.mascota)
            .filter(
              Mascota.dueño_id == user_id,
              Mascota.clinica_id == clinica_id
            )
            .all()
    )
    return jsonify([v.to_dict() for v in visitas]), 200