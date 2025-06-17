from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.clinica import Clinica
from app.models.prop_mascota import Prop_mascota
from app.models.mascota import Mascota

props_bp = Blueprint('props', __name__,
    url_prefix='/api/clinicas/<int:clinica_id>/props_mascotas'
)

@props_bp.route('', methods=['GET'])
@jwt_required()
def listar_propietarios(clinica_id):
    Clinica.query.get_or_404(clinica_id)
    props = Prop_mascota.query.filter_by(clinica_id=clinica_id).all()
    return jsonify([{'id': p.id, 'usuario': p.usuario} for p in props]), 200

@props_bp.route('/<int:prop_id>/mascotas', methods=['GET'])
@jwt_required()
def listar_mascotas_propietario(clinica_id, prop_id):
    Clinica.query.get_or_404(clinica_id)
    Prop_mascota.query.filter_by(id=prop_id, clinica_id=clinica_id).first_or_404()
    mascotas = Mascota.query.filter_by(dueño_id=prop_id).all()
    return jsonify([{'id': m.id, 'nombre': m.nombre} for m in mascotas]), 200