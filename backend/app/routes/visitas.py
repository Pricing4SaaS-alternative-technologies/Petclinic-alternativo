from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.visita import Visita
from app.models.mascota import Mascota
from app.models.prop_mascota import Prop_mascota
from app.models.clinica import Clinica

visitas_bp = Blueprint('visitas', __name__,
    url_prefix='/api/clinicas/<int:clinica_id>/props_mascotas/<int:usuario_id>/mascotas/<int:mascota_id>/visitas'
)

def get_mascota(clinica_id, usuario_id, mascota_id):
    # 1) Comprueba que la clínica existe
    Clinica.query.get_or_404(clinica_id)
    # 2) Comprueba que el propietario de mascota está en esa clínica
    Prop_mascota.query.filter_by(id=usuario_id, clinica_id=clinica_id).first_or_404()
    # 3) Recupera la mascota sólo si pertenece a ese dueño
    return Mascota.query.filter_by(id=mascota_id, dueño_id=usuario_id).first_or_404()

@visitas_bp.route('', methods=['GET'])
@jwt_required()
def get_visitas(clinica_id, usuario_id, mascota_id):
    mascota = get_mascota(clinica_id, usuario_id, mascota_id)
    data = [
        {'id': v.id, 'date_time': v.date_time.isoformat(), 'description': v.description}
        for v in Visita.query.filter_by(mascota_id=mascota.id)
    ]
    return jsonify(data), 200

@visitas_bp.route('', methods=['POST'])
@jwt_required()
def crear_visita(clinica_id, usuario_id, mascota_id):
    get_mascota(clinica_id, usuario_id, mascota_id)
    json = request.get_json()
    v = Visita(
        date_time=json.get('date_time'),
        description=json.get('description'),
        mascota_id=mascota_id
    )
    db.session.add(v)
    db.session.commit()
    return jsonify({'id': v.id}), 201

@visitas_bp.route('/<int:visita_id>', methods=['PATCH'])
@jwt_required()
def actualizar_visita(clinica_id, usuario_id, mascota_id, visita_id):
    get_mascota(clinica_id, usuario_id, mascota_id)
    v = Visita.query.filter_by(id=visita_id, mascota_id=mascota_id).first_or_404()
    json = request.get_json()
    if 'date_time' in json:    v.date_time = json['date_time']
    if 'description' in json:   v.description = json['description']
    db.session.commit()
    return jsonify({'msg': 'Actualizada'}), 200

@visitas_bp.route('/<int:visita_id>', methods=['DELETE'])
@jwt_required()
def eliminar_visita(clinica_id, usuario_id, mascota_id, visita_id):
    get_mascota(clinica_id, usuario_id, mascota_id)
    v = Visita.query.filter_by(id=visita_id, mascota_id=mascota_id).first_or_404()
    db.session.delete(v)
    db.session.commit()
    return jsonify({'msg': 'Eliminada'}), 200

@visitas_bp.route('/props_mascotas', methods=['GET'])
@jwt_required()
def listar_propietarios(clinica_id, usuario_id, mascota_id=None):
    Clinica.query.get_or_404(clinica_id)
    return jsonify([
        {'id': p.id, 'usuario': p.usuario}
        for p in Prop_mascota.query.filter_by(clinica_id=clinica_id).all()
    ]), 200

# lista de mascotas de un propietario dentro de la clínica
@visitas_bp.route('/props_mascotas/<int:prop_id>/mascotas', methods=['GET'])
@jwt_required()
def listar_mascotas_propietario(clinica_id, usuario_id, prop_id):
    get_mascota(clinica_id, usuario_id, None)  # valida existencia de clínica y prop
    return jsonify([
        {'id': m.id, 'nombre': m.nombre}
        for m in Mascota.query.filter_by(dueño_id=prop_id).all()
    ]), 200