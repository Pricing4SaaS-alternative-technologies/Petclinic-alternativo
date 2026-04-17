
from flask import Blueprint, request, jsonify, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.clinica import Clinica
from app.models.mascota import Mascota
from app.models.enums import TipoUsuarioEnum
from app.models.habitacion_hotel import Habitacion_hotel
from app.extensions import db
from app.models.enums import TipoMascota
from app.models.reserva import Reserva
from datetime import date, datetime

habitaciones_hotel = Blueprint('habitaciones_hotel', __name__, url_prefix='/api/habitaciones_hotel')

@habitaciones_hotel.route('/listar/admin', methods=['GET'])
@jwt_required()
def listar_habitaciones_admin():

    id_usuario = get_jwt_identity()
    usuario = db.session.get(Usuario, id_usuario)

    if not usuario:
        abort(404)

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

@habitaciones_hotel.route('/listar/prop-clinica/<int:user_id>', methods=['GET'])
@jwt_required()
def listar_habitaciones_prop_clinica(user_id):
    usuario_id = int(get_jwt_identity())
    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        abort(404)

    rol_usuario = usuario.tipo_usuario
    dueñoC_buscado = db.session.get(Usuario, user_id)

    if not dueñoC_buscado:
        abort(404)

    # Roles no autorizados
    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para usar esta operacion'}), 403

    # usuario solo puede ver sus habitaciones de sus clinicas
    if usuario_id != dueñoC_buscado.id and rol_usuario == TipoUsuarioEnum.PROP_CLINICA:
        return jsonify({'message': 'No tienes permiso para ver las habitaciones de otro propietario'}), 403

    # dueño no existe
    if dueñoC_buscado.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA:
        return jsonify({'message': 'El ID proporcionado no corresponde a un propietario de clínica'}), 400

    habitaciones = Habitacion_hotel.query.all()
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
        "propietario_clinica_id": h.clinica.propietario_id,
        "nombre_clinica": h.clinica.nombre
    }
        for h in habitaciones if h.clinica.propietario_id == dueñoC_buscado.id
    ]), 200

@habitaciones_hotel.route('/listar/<int:clinica_id_enviada>', methods=['GET'])
@jwt_required()
def listar_habitaciones_clinica(clinica_id_enviada):
    id_usuario = int(get_jwt_identity())
    usuario = db.session.get(Usuario, id_usuario)

    if not usuario:
        abort(404)

    rol_usuario = usuario.tipo_usuario
    clinica = db.session.get(Clinica, clinica_id_enviada)

    if not clinica:
        abort(404)

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
    usuario = db.session.get(Usuario, id_usuario)

    if not usuario:
        abort(404)

    rol_usuario = usuario.tipo_usuario
    habitacion = db.session.get(Habitacion_hotel, habitacion_id)

    if not habitacion:
        abort(404)

    clinica = db.session.get(Clinica, habitacion.clinica_id)

    if not clinica:
        abort(404)

    # roles no autorizados
    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN: 
        return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación del hotel'}), 403

    # prop clinica solo puede ver las habitaciones de su clinica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación de esta clínica'}), 403

    # prop mascota no puede ver las habitaciones de una clinica que no sea la suya/su mascota
    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA and usuario.clinica_id and usuario.clinica_id != habitacion.clinica_id:
        return jsonify({'message': 'No tienes permiso para ver los detalles de la habitación de esta clínica'}), 403

    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA and habitacion.reservable == False:
        return jsonify({'message': 'No tienes permiso para ver los detalles de una habitación no reservable'}), 403
    
    try:
        habitacion = Habitacion_hotel.query.filter_by(id=habitacion_id).first()
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

@habitaciones_hotel.route('/crear-habitacion', methods=['POST'])
@jwt_required()
def crear_habitacion():
    id_usuario = int(get_jwt_identity())
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        abort(404)

    rol_usuario = usuario.tipo_usuario

    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg': 'No tienes permiso para crear habitaciones del hotel'}), 403

    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '').strip()
    reservable = data.get('reservable', True)
    url_imagen = data.get('url_imagen')
    tamaño = data.get('tamaño')
    tipo = data.get('tipo')
    clinica_id = data.get('clinica_id')

    # Validaciones básicas
    if not nombre:
        return jsonify({'msg': 'Nombre requerido'}), 400
    
    if len(nombre) > 100:
        return jsonify({'msg': 'El nombre no puede tener más de 100 caracteres'}), 400

    # Descripción es opcional según el modelo
    if descripcion and len(descripcion) > 255:
        return jsonify({'msg': 'La descripción no puede tener más de 255 caracteres'}), 400

    if not clinica_id:
        return jsonify({'msg': 'clinica_id requerido'}), 400

    # Verificar que la clínica existe
    clinica = db.session.get(Clinica, clinica_id)
    if not clinica:
        return jsonify({'msg': 'La clínica especificada no existe'}), 404

    # Prop_clinica solo puede crear habitaciones en su propia clínica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para crear habitaciones en esta clínica'}), 403

    if url_imagen and len(url_imagen) > 255:
        return jsonify({'msg': 'La URL de la imagen no puede tener más de 255 caracteres'}), 400

    # Verificar si ya existe una habitación con ese nombre (dado que es único)
    habitacion_existente = Habitacion_hotel.query.filter_by(nombre=nombre).first()
    if habitacion_existente:
        return jsonify({'msg': 'Ya existe una habitación con ese nombre'}), 400

    try:
        habitacion = Habitacion_hotel(
            nombre=nombre,
            reservable=reservable,
            tamaño=tamaño,
            tipo=tipo,
            clinica_id=clinica_id
        )

        if descripcion:
            habitacion.descripcion = descripcion
        if url_imagen:
            habitacion.url_imagen = url_imagen

        habitacion.save()
        space_client = current_app.space_client
        evaluacion = current_app.run_async(space_client.featureEvaluators.evaluate(id_usuario, "petclinic-petHotelManagement", {"petclinic-maxPetHotelRooms": 1}))
        if evaluacion.eval == False:
            habitacion.delete()
            return jsonify({'message': 'No se puede crear más habitaciones con el plan actual. Por favor, actualiza tu plan.'}), 403
        return jsonify({
            'msg': 'Habitación creada con éxito',
            'id': habitacion.id,
            'nombre': habitacion.nombre,
            'clinica_id': habitacion.clinica_id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear la habitación: {str(e)}")
        return jsonify({'msg': f'Error al crear la habitación: {str(e)}'}), 500

@habitaciones_hotel.route('/editar/<int:habitacion_id>', methods=['PUT'])
@jwt_required()
def editar_habitacion(habitacion_id):
    id_usuario = get_jwt_identity()
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        abort(404)

    rol_usuario = usuario.tipo_usuario

    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg': 'No tienes permiso para editar habitaciones del hotel'}), 403

    habitacion = db.session.get(Habitacion_hotel, habitacion_id)
    if not habitacion:
        abort(404)

    clinica = db.session.get(Clinica, habitacion.clinica_id)
    if not clinica:
        abort(404)

    # prop clinica solo puede editar las habitaciones de su clinica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para editar las habitaciones de esta clínica'}), 403

    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '').strip()
    reservable = data.get('reservable')
    print("reservable recibido:", reservable)
    url_imagen = data.get('url_imagen')
    tamaño = data.get('tamaño')
    tipo = data.get('tipo')

    # Validaciones básicas
    if nombre:
        if len(nombre) > 100:
            return jsonify({'msg': 'El nombre no puede tener más de 100 caracteres'}), 400
        habitacion.nombre = nombre

    if descripcion:
        if len(descripcion) > 255:
            return jsonify({'msg': 'La descripción no puede tener más de 255 caracteres'}), 400
        habitacion.descripcion = descripcion

    if url_imagen:
        if len(url_imagen) > 255:
            return jsonify({'msg': 'La URL de la imagen no puede tener más de 255 caracteres'}), 400
        habitacion.url_imagen = url_imagen

    if reservable is not None:
        print("reservable a asignar:", reservable)
        habitacion.reservable = reservable
        print("Habitación reservable ahora es:", habitacion.reservable)

    if tamaño:
        habitacion.tamaño = tamaño

    if tipo is not None:
        if tipo not in [t.value for t in TipoMascota]:
            return jsonify({'msg': 'Tipo de mascota inválido'}), 400
        
        if tipo != habitacion.tipo.value:
            print(f"Intentando cambiar tipo de '{habitacion.tipo.value.lower()}' a '{tipo}'")
            
            if habitacion.reservable == True:
                return jsonify({'msg': 'A una habitación reservable no se le puede editar el tipo'}), 400

            hoy = date.today()
            reservas_futuras = Reserva.query.filter(
                Reserva.habitacion_id == habitacion_id, 
                Reserva.fecha_fin >= hoy
            ).first()

            if reservas_futuras:
                return jsonify({'msg': 'No se puede cambiar el tipo de habitación porque tiene reservas futuras pendientes'}), 400

            habitacion.tipo = tipo
            print(f"Tipo cambiado a: {habitacion.tipo}")
        else:
            print("El tipo no ha cambiado, no se requiere validación")
    else:
        print("No se envió campo 'tipo' en la solicitud")

    try:
        habitacion.save()
        print("Habitación actualizada exitosamente")
        return jsonify({'msg': 'Habitación actualizada con éxito'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar: {str(e)}")
        return jsonify({'msg': f'Error al actualizar la habitación: {str(e)}'}), 500  

@habitaciones_hotel.route('/eliminar/<int:habitacion_id>', methods=['DELETE'])
@jwt_required()
def eliminar_habitacion(habitacion_id):
    id_usuario = get_jwt_identity()
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        abort(404)
    rol_usuario = usuario.tipo_usuario

    if rol_usuario != TipoUsuarioEnum.PROP_CLINICA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg': 'No tienes permiso para eliminar habitaciones del hotel'}), 403
    
    habitacion = db.session.get(Habitacion_hotel, habitacion_id)
    if not habitacion:
        abort(404)

    clinica = db.session.get(Clinica, habitacion.clinica_id)
    if not clinica:
        abort(404)

    # prop clinica solo puede eliminar las habitaciones de su clinica
    if rol_usuario == TipoUsuarioEnum.PROP_CLINICA and usuario.id != clinica.propietario_id:
        return jsonify({'message': 'No tienes permiso para eliminar las habitaciones de esta clínica'}), 403

    hoy = date.today()
    reservas_futuras = Reserva.query.filter(Reserva.habitacion_id == habitacion_id, Reserva.fecha_fin >= hoy).first()

    if reservas_futuras:
        return jsonify({'msg': 'No se puede eliminar la habitación porque tiene reservas futuras pendientes'}), 400

    if habitacion.reservable == True:
        return jsonify({'msg': 'No se puede eliminar una habitación que está marcada como reservable'}), 400

    try:
        habitacion.delete()
        # actualización de los niveles de uso para lso casos donde se elimina la habitación
        space_client = current_app.space_client
        usage_levels = { 
            "petclinic": {
                "maxPetHotelRooms": -1
            }
        }
        current_app.run_async(space_client.contracts.update_usage_levels(id_usuario, usage_levels))
        return jsonify({'msg': 'Habitación eliminada con éxito'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error al eliminar la habitación: {str(e)}'}), 500