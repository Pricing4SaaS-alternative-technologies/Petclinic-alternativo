from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.visita import Visita
from app.models.mascota import Mascota
from app.models.clinica import Clinica

visitas_bp = Blueprint('visitas', __name__,
                       url_prefix='/api/clinicas/<int:clinica_id>/mascotas/<int:mascota_id>/visitas')

def get_mascota(clinica_id, mascota_id):
    # Verifica que la clínica y la mascota existan y pertenezcan
    clinica = Clinica.query.get_or_404(clinica_id)
    mascota = Mascota.query.filter_by(id=mascota_id, clinica_id=clinica.id).first_or_404()
    return mascota

@visitas_bp.route('', methods=['GET'])
@jwt_required()
def get_visitas(clinica_id, mascota_id):
    mascota = get_mascota(clinica_id, mascota_id)
    visitas = Visita.query.filter_by(mascota_id=mascota.id).all()
    return jsonify([{
        'id': v.id,
        'date_time': v.date_time.isoformat(),
        'description': v.description
    } for v in visitas]), 200

@visitas_bp.route('', methods=['POST'])
@jwt_required()
def crear_visita(clinica_id, mascota_id):
    mascota = get_mascota(clinica_id, mascota_id)
    data = request.get_json()
    v = Visita(
        date_time=data.get('date_time'),
        description=data.get('description'),
        mascota_id=mascota.id
    )
    db.session.add(v)
    db.session.commit()
    return jsonify({'id': v.id}), 201

@visitas_bp.route('/<int:visita_id>', methods=['PATCH'])
@jwt_required()
def actualizar_visita(clinica_id, mascota_id, visita_id):
    get_mascota(clinica_id, mascota_id)
    v = Visita.query.filter_by(id=visita_id, mascota_id=mascota_id).first_or_404()
    data = request.get_json()
    if 'date_time' in data:    v.date_time = data['date_time']
    if 'description' in data:  v.description = data['description']
    db.session.commit()
    return jsonify({'msg': 'Actualizada'}), 200

@visitas_bp.route('/<int:visita_id>', methods=['DELETE'])
@jwt_required()
def eliminar_visita(clinica_id, mascota_id, visita_id):
    get_mascota(clinica_id, mascota_id)
    v = Visita.query.filter_by(id=visita_id, mascota_id=mascota_id).first_or_404()
    db.session.delete(v)
    db.session.commit()
    return jsonify({'msg': 'Eliminada'}), 200