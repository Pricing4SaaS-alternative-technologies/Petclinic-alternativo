
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.reserva import Reserva
from app.models.mascota import Mascota
from app.models.enums import TipoUsuarioEnum
from app.extensions import db
from app.models.habitacion_hotel import Habitacion_hotel

reservas = Blueprint('reservas', __name__, url_prefix='/api/reservas')

@reservas.route('/mis_habs_reservas', methods=['GET'])
@jwt_required()
def listar_mis_habitaciones_reservas():
    id_usuario = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(id_usuario)
    rol_usuario = usuario.tipo_usuario
    
    mascota_id = request.args.get('mascota_id', type=int)

    if rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver tus reservas'}), 403

    # Obtener las mascotas del usuario
    mascotas = Mascota.query.filter_by(dueño_id=id_usuario).all()
    mascota_ids = [mascota.id for mascota in mascotas]
    
    if not mascota_ids:
        return jsonify([]), 200
    
    if mascota_id:
        if mascota_id not in mascota_ids:
            return jsonify({'message': 'Mascota no pertenece al usuario'}), 400
        mascota_ids = [mascota_id]

    # Consulta alternativa: obtener reservas primero y luego las habitaciones
    reservas = Reserva.query.filter(Reserva.mascota_id.in_(mascota_ids)).all()
    habitacion_ids = [reserva.habitacion_id for reserva in reservas]
    
    if not habitacion_ids:
        return jsonify([]), 200
    
    # Obtener las habitaciones a partir de las IDs de las reservas
    habitaciones_reservadas = Habitacion_hotel.query.filter(Habitacion_hotel.id.in_(habitacion_ids)).all()

    return jsonify([
        {
            "id": h.id,
            "nombre": h.nombre,
            "descripcion": h.descripcion,
            "reservable": h.reservable,
            "url_imagen": h.url_imagen,
            "tamaño": h.tamaño.value,
            "tipo": h.tipo.value,
            "clinica_id": h.clinica_id
        }
        for h in habitaciones_reservadas
    ]), 200
    
@reservas.route('/mis_reservas', methods=['GET'])
@jwt_required()
def listar_reservas():
    id_usuario = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(id_usuario)
    rol_usuario = usuario.tipo_usuario
    mascota_id = request.args.get('mascota_id', type=int)

    if rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver tus reservas'}), 403
    

    mascotas = Mascota.query.filter_by(dueño_id=id_usuario).all()
    mascota_ids = [mascota.id for mascota in mascotas]
    
    if not mascota_ids:
        return jsonify([]), 200
    
    if mascota_id:
        if mascota_id not in mascota_ids:
            return jsonify({'message': 'Mascota no pertenece al usuario'}), 400
        mascota_ids = [mascota_id]
    
    
    reservas = Reserva.query.filter(Reserva.mascota.has(dueño_id=id_usuario)).all()
    
    return jsonify([{
        'id': reserva.id,
        'mascota_id': reserva.mascota_id,
        'habitacion_id': reserva.habitacion_id,
        'fecha_inicio': reserva.fecha_inicio.isoformat(),
        'fecha_fin': reserva.fecha_fin.isoformat()
    } for reserva in reservas]), 200
    
@reservas.route('/crear', methods=['POST'])
@jwt_required()
def crear_reserva():
    id_usuario = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(id_usuario)
    rol_usuario = usuario.tipo_usuario

    if rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para crear reservas'}), 403

    data = request.get_json()
    mascota_id = data.get('mascota_id')
    habitacion_hotel_id = data.get('habitacion_hotel_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')

    mascota = Mascota.query.filter_by(id=mascota_id, dueño_id=id_usuario).first()
    if not mascota:
        return jsonify({'message': 'Mascota no encontrada o no te pertenece'}), 404

    habitacion = Habitacion_hotel.query.filter_by(id=habitacion_hotel_id, reservable=True).first()
    if not habitacion:
        return jsonify({'message': 'Habitación no encontrada o no reservable'}), 404
    
    if fecha_inicio >= fecha_fin:
        return jsonify({'message': 'La fecha de fin debe ser posterior a la fecha de inicio'}), 400
    
    if Reserva.query.filter(
        Reserva.habitacion_id == habitacion_hotel_id,
        Reserva.fecha_fin > fecha_inicio,
        Reserva.fecha_inicio < fecha_fin
    ).first():
        return jsonify({'message': 'La habitación ya está reservada en las fechas seleccionadas'}), 400
    id_clinica_mascota = Usuario.query.get_or_404(mascota.dueño_id).clinica_id
    if id_clinica_mascota != habitacion.clinica_id:
        return jsonify({'message': 'La mascota no pertenece a la clínica de la habitación'}), 403

    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        dueño_mascota_id = mascota.dueño_id
        if id_usuario != dueño_mascota_id:
            return jsonify({'message': 'No tienes permiso para reservar con esta mascota'}), 403

    nueva_reserva = Reserva(
        mascota_id=mascota_id,
        habitacion_id=habitacion_hotel_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({'message': 'Reserva creada exitosamente', 'reserva_id': nueva_reserva.id}), 201
