
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.enums import TipoUsuarioEnum
from backend.app.models.habitacion_hotel import Habitacion_hotel

habitaciones_hotel = Blueprint('habitaciones_hotel', __name__, prefix='/api/habitaciones_hotel')

@habitaciones_hotel.route('/listar/admin', methods=['GET'])
@jwt_required()
def listar_habitaciones():
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver las habitaciones del hotel'}), 403
    
    return jsonify(
        {
        "id": h.id,
        "nombre": h.nombre,
        "descripcion": h.descripcion,
        "reservable": h.reservable,
        "url_imagen": h.url_imagen,
        "tamaño": h.tamaño.value,
        "tipo": h.tipo.value,
        "clinica_id": h.clinica_id,
        "propietario_clinica_id": h.clinica.propietario_id  
    }
        for h in Habitacion_hotel.query.all())
