from datetime import datetime, date
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.enums import TipoMascota
from app.models.enums import TipoUsuarioEnum
from app.extensions import db
from datetime import datetime

mascotas_bp = Blueprint('mascotas', __name__, url_prefix='/api/mascotas')

@mascotas_bp.route('/listar-tus-mascotas', methods=['GET'])
@jwt_required()
def get_mis_mascotas():
    user_id = get_jwt_identity()
    rol_usuario = Usuario.query.filter_by(id=user_id).first().tipo_usuario
    
    if (rol_usuario != TipoUsuarioEnum.PROP_MASCOTA) and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver estas mascotas'}), 403
    
    mascotas = Mascota.query.filter_by(dueño_id=user_id).all()
    if not mascotas:
        return jsonify([]), 200

    return jsonify([
        {
            'id': m.id,
            'nombre': m.nombre,
            'cumpleaños': m.cumpleaños.isoformat(),
            'tipo': m.tipo.value
        } for m in mascotas
    ]), 200


@mascotas_bp.route('/dueno-mascota/<int:dueno_id>', methods=['GET'])
@jwt_required()
def get_mascotas_by_dueño(dueno_id):
    user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=user_id).first()

    dueño = Usuario.query.get_or_404(dueno_id)
    if (usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO and dueño.clinica_id != usuario.clinica_id) and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver las mascotas de este dueño'}), 403

    mascotas = Mascota.query.filter_by(dueño_id=dueno_id).all()
    if not mascotas:
        return jsonify([]), 200

    return jsonify([
        {
            'id': m.id,
            'nombre': m.nombre,
            'cumpleaños': m.cumpleaños.isoformat(),
            'tipo': m.tipo.value
        } for m in mascotas
    ]), 200

@mascotas_bp.route('/crear-mascota', methods=['POST'])
@jwt_required()
def crear_mascota():
    data = request.get_json()
    id_usuario = int(get_jwt_identity())

    nombre = data.get('nombre')
    cumpleaños = data.get('cumpleaños')
    tipo = data.get('tipo')

    if not nombre or not cumpleaños or not tipo:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        cumpleaños_dt = datetime.strptime(cumpleaños, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (esperado: yyyy-MM-dd)'}), 400

    if cumpleaños_dt > date.today():
        return jsonify({'error': 'La fecha de cumpleaños no puede ser futura'}), 400
    
    if cumpleaños_dt < date(1800, 1, 1):
        return jsonify({'error': 'La fecha de cumpleaños no puede ser anterior al 1 de enero de 1800'}), 400

    user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not user_id:
        return jsonify({'error': 'Identidad del token inválida'}), 401
    
    if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN):
        return jsonify({'message': 'No tienes permiso para crear mascotas'}), 403

    nueva_mascota = Mascota(
        nombre=nombre,
        cumpleaños=cumpleaños_dt,
        tipo=tipo,
        dueño_id=user_id
    )
    try:
        db.session.add(nueva_mascota)
        db.session.commit()
        
        space_client = current_app.space_client
        evaluacion = current_app.run_async(space_client.featureEvaluators.evaluate(id_usuario, "petclinic-registeredPets", {"petclinic-maxRegisteredPets": 1}))
        if evaluacion.eval == False:
            nueva_mascota.delete()
            return jsonify({'message': 'No se puede crear más mascotas con el plan actual. El dueño de la clínica debe actualizar su plan.'}), 403
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la mascota'}), 500

    return jsonify({'mensaje': 'Mascota creada con éxito'}), 201

@mascotas_bp.route('/<int:mascota_id>', methods=['PATCH'])
@jwt_required()
def editar_nombre_mascota(mascota_id):
    data = request.get_json()
    nuevo_nombre = data.get('nombre')

    if not nuevo_nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    
    if len(nuevo_nombre) > 50:
        return jsonify({'error': 'El nombre no puede tener más de 50 caracteres'}), 400

    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=user_id).first()
    except Exception:
        return jsonify({'error': 'Identidad del token inválida'}), 401

    mascota = db.session.get(Mascota, mascota_id)
    
    if not mascota:
        return jsonify({'error': 'Mascota no encontrada'}), 404

    if (user_id != mascota.dueño_id and usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA) and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para editar esta mascota'}), 403

    mascota.nombre = nuevo_nombre
    db.session.commit()
    return jsonify({'mensaje': 'Nombre actualizado correctamente'}), 200

@mascotas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_mascota(id):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN):
        return jsonify({'message': 'No tienes permiso para eliminar mascotas'}), 403
    
    mascota = db.session.get(Mascota, id)
    if not mascota:
        return jsonify({'error': 'Mascota no encontrada'}), 404

    db.session.delete(mascota)
    space_client = current_app.space_client
    usage_levels = { 
        "petclinic": {
            "maxRegisteredPets": -1
        }
    }
    current_app.run_async(space_client.contracts.update_usage_levels(user_id, usage_levels))
    db.session.commit()
    return jsonify({'mensaje': 'Mascota eliminada correctamente'}), 200