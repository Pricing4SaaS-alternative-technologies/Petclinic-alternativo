
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.clinica import Clinica
from app.models.mascota import Mascota
from app.models.enums import TipoUsuarioEnum
from app.models.habitacion_hotel import Habitacion_hotel

habitaciones_hotel = Blueprint('habitaciones_hotel', __name__, url_prefix='/api/habitaciones_hotel')

@habitaciones_hotel.route('/listar/admin', methods=['GET'])
@jwt_required()
def listar_habitaciones_admin():
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver las habitaciones del hotel'}), 403
    
    return jsonify([
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
        for h in Habitacion_hotel.query.all()]), 200

@habitaciones_hotel.route('/listar/<int:clinica_id_enviada>', methods=['GET'])
@jwt_required()
def listar_habitaciones_clinica(clinica_id_enviada):
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.get_or_404(id_usuario)
    rol_usuario = Usuario.query.filter_by(id=id_usuario).first_or_404().tipo_usuario
    clinica = Clinica.query.get_or_404(clinica_id_enviada)
    id_clinica_usuario = usuario.clinica_id
    
    # roles no autorizados
    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN: 
        return jsonify({'message': 'No tienes permiso para ver las habitaciones del hotel'}), 403
    
    # prop clinica solo puede ver las habitaciones de su clinica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para ver las habitaciones de esta clínica'}), 403
    
    # prop mascota no puede ver las habitaciones de una clinica que no sea la suya/su mascota
    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        # mascota = Mascota.query.filter_by(id_usuario=id_usuario).first()
        if id_clinica_usuario != clinica_id_enviada:
            return jsonify({'message': 'No tienes permiso para ver las habitaciones de esta clínica'}), 403

    try:
        habitaciones = Habitacion_hotel.query.filter_by(reservable=True, clinica_id=clinica_id_enviada).all()
        
        resultado = []
        for h in habitaciones:
            resultado.append({
                "id": h.id,
                "nombre": h.nombre,
                "descripcion": h.descripcion,
                "reservable": h.reservable,
                "url_imagen": h.url_imagen,
                "tamaño": h.tamaño.value if h.tamaño else None,
                "tipo": h.tipo.value if h.tipo else None,
                "clinica_id": h.clinica_id,
                "propietario_clinica_id": h.clinica.propietario_id if h.clinica else None
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@habitaciones_hotel.route('/detalles/<int:habitacion_id>', methods=['GET'])
@jwt_required()
def detalles_habitacion(habitacion_id):
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.get_or_404(id_usuario)
    rol_usuario = Usuario.query.filter_by(id=id_usuario).first_or_404().tipo_usuario
    habitacion = Habitacion_hotel.query.get_or_404(habitacion_id)
    clinica = Clinica.query.get_or_404(habitacion.clinica_id)
    id_clinica_usuario = usuario.clinica_id
    
    # roles no autorizados
    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN: 
        return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación del hotel'}), 403
    
    # prop clinica solo puede ver las habitaciones de su clinica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación de esta clínica'}), 403
    
    # prop mascota no puede ver las habitaciones de una clinica que no sea la suya/su mascota
    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        if id_clinica_usuario != habitacion.clinica_id:
            return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación de esta clínica'}), 403

    try:
        habitacion = Habitacion_hotel.query.filter_by(reservable=True, id=habitacion_id).first()
        
        if not habitacion:
            return jsonify({'message': 'Habitación no encontrada'}), 404

        resultado = {
            "id": habitacion.id,
                "nombre": habitacion.nombre,
                "descripcion": habitacion.descripcion,
                "reservable": habitacion.reservable,
                "url_imagen": habitacion.url_imagen,
                "tamaño": habitacion.tamaño.value if habitacion.tamaño else None,
                "tipo": habitacion.tipo.value if habitacion.tipo else None,
                "clinica_id": habitacion.clinica_id,
                "propietario_clinica_id": habitacion.clinica.propietario_id if habitacion.clinica else None
            }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    