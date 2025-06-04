from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.extensions import db
from datetime import datetime

mascotas_bp = Blueprint('mascotas', __name__, url_prefix='/api/mascotas')

@mascotas_bp.route('/<int:duenio_id>', methods=['GET'])
def get_mascotas_por_duenio(duenio_id):
    mascotas = Mascota.query.filter_by(dueño_id=duenio_id).all()
    return jsonify([
        {
            'id': m.id,
            'nombre': m.nombre,
            'cumpleaños': m.cumpleaños.isoformat(),
            'tipo': m.tipo.value
        } for m in mascotas
    ])

@mascotas_bp.route('', methods=['POST'])
@jwt_required()
def crear_mascota():
    data = request.get_json()

    nombre = data.get('nombre')
    cumpleaños = data.get('cumpleaños')
    tipo = data.get('tipo')

    if not nombre or not cumpleaños or not tipo:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        cumpleaños_dt = datetime.strptime(cumpleaños, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (esperado: yyyy-MM-dd)'}), 400

    user_id = get_jwt_identity()
    dueño = Usuario.query.get(user_id)

    if not dueño:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    nueva_mascota = Mascota(
        nombre=nombre,
        cumpleaños=cumpleaños_dt,
        tipo=tipo,
        dueño_id=user_id
    )

    db.session.add(nueva_mascota)
    db.session.commit()

    return jsonify({'mensaje': 'Mascota creada con éxito'}), 201

@mascotas_bp.route('/<int:mascota_id>', methods=['PATCH'])
@jwt_required()
def editar_nombre_mascota(mascota_id):
    data = request.get_json()
    nuevo_nombre = data.get('nombre')

    if not nuevo_nombre:
        return jsonify({'error': 'Nombre requerido'}), 400

    mascota = Mascota.query.get(mascota_id)
    if not mascota:
        return jsonify({'error': 'Mascota no encontrada'}), 404

    mascota.nombre = nuevo_nombre
    db.session.commit()
    return jsonify({'mensaje': 'Nombre actualizado correctamente'}), 200

@mascotas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_mascota(id):
    mascota = Mascota.query.get(id)
    if not mascota:
        return jsonify({'error': 'Mascota no encontrada'}), 404

    db.session.delete(mascota)
    db.session.commit()
    return jsonify({'mensaje': 'Mascota eliminada correctamente'}), 200
