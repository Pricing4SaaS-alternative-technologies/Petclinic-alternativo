from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, datetime
from app.extensions import db
from app.models.visita import Visita
from app.models.mascota import Mascota
from app.models.enums import TipoUsuarioEnum
from app.models.usuario import Usuario


visitas_bp = Blueprint('visitas', __name__,
    url_prefix='/api/visitas'
)
@visitas_bp.route('/listar/admin', methods=['GET'])
@jwt_required()
def listar_visitas():
    usuario_id = get_jwt_identity()
    rol_usuario = Usuario.query.filter_by(id=usuario_id).first().tipo_usuario
    
    if rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver todas las visitas del sistema'}), 403
    
    visitas = Visita.query.all()
    return jsonify([
        {
            'id': v.id,
            'fecha': v.fecha.isoformat(),
            'descripcion': v.descripcion,
            'mascota_id': v.mascota_id,
            'mascota_nombre': v.mascota.nombre,
            'veterinario_id': v.veterinario_id
        }
        for v in visitas
    ]), 200

@visitas_bp.route('/veterinario/<int:vet_id>', methods=['GET'])
@jwt_required()
def listar_visitas_veterinario(vet_id):
    
    usuario_id = int(get_jwt_identity())
    rol_usuario = Usuario.query.filter_by(id=usuario_id).first_or_404().tipo_usuario
    
    vet_buscado = db.get_or_404(Usuario, vet_id)
    # Roles no autorizados
    if rol_usuario != TipoUsuarioEnum.VETERINARIO and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para usar esta operacion'}), 403

    # vet solo peude ver sus visitas
    if usuario_id != vet_buscado.id and rol_usuario == TipoUsuarioEnum.VETERINARIO:
        return jsonify({'message': 'No tienes permiso para ver las visitas de otro veterinario'}), 403
    
    # vet no existe
    if vet_buscado.tipo_usuario != TipoUsuarioEnum.VETERINARIO:
        return jsonify({'message': 'El ID proporcionado no corresponde a un veterinario'}), 400
    
    visitas = Visita.query.filter_by(veterinario_id=vet_id).all()
    return jsonify([
        {
            'id': v.id,
            'fecha': v.fecha.isoformat(),
            'descripcion': v.descripcion,
            'mascota_id': v.mascota_id,
            'mascota_nombre': v.mascota.nombre
        }
        for v in visitas
    ]), 200

@visitas_bp.route('/mascota/<int:mascota_id>', methods=['GET'])
@jwt_required()
def listar_visitas_mascota(mascota_id):
    usuario_id = int(get_jwt_identity())
    rol_usuario = Usuario.query.filter_by(id=usuario_id).first().tipo_usuario
    mascota = db.get_or_404(Mascota, mascota_id)
    
    if rol_usuario != TipoUsuarioEnum.PROP_MASCOTA and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver las visitas'}), 403

    if rol_usuario == TipoUsuarioEnum.PROP_MASCOTA and usuario_id != mascota.dueño_id:
        return jsonify({'message': 'No tienes permiso para ver las visitas de otra mascota'}), 403
    
    visitas = Visita.query.filter_by(mascota_id=mascota_id).all()
    return jsonify([
        {
            'id': v.id,
            'fecha': v.fecha.isoformat(),
            'descripcion': v.descripcion,
            'veterinario_id': v.veterinario_id
        }
        for v in visitas
    ]), 200

@visitas_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear_visita():
    data       = request.get_json() or {}
    mascota_id = data.get('mascota_id')
    fecha_str  = data.get('fecha')
    descripcion= data.get('descripcion','').strip()
    
    veterinario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=veterinario_id).first()
    
    if usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No autorizado'}), 403
    
    dueño_mascota_id= db.get_or_404(Mascota, mascota_id).dueño_id
    dueño_mascota= db.get_or_404(Usuario, dueño_mascota_id)
    
    if dueño_mascota.clinica_id != usuario.clinica_id:
        return jsonify({'msg':'La mascota no pertenece a la clínica del veterinario'}), 403
    
    
    # validación fecha+hora
    if not fecha_str:
        return jsonify({'msg':'Fecha y hora requerida'}), 400
    try:
        fecha_dt = datetime.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({'msg':'Formato de fecha y hora inválido (YYYY-MM-DDThh:mm)'}), 400
    if fecha_dt < datetime.now():
        return jsonify({'msg':'La fecha y hora no puede ser anterior al momento actual'}), 400

    # validación descripción...
    if not descripcion:
        return jsonify({'msg':'Descripción requerida'}), 400
    if len(descripcion) > 255:
        return jsonify({'msg':'La descripción no puede tener más de 255 caracteres'}), 400

    visita = Visita(fecha_dt, descripcion, mascota_id)
    visita.veterinario_id = veterinario_id
    db.session.add(visita)
    db.session.commit()
    return jsonify({'id': visita.id}), 201

@visitas_bp.route('/actualizar/<int:visita_id>', methods=['PATCH'])
@jwt_required()
def actualizar_visita(visita_id):
    
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=usuario_id).first()
    visita_editable= Visita.query.filter_by(id=visita_id).first_or_404()
    data = request.get_json() or {}

    # solo vets y admins pueden editar visitas
    if usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No tienes permiso para actualizar visitas'}), 403
    
    # solo vet que crea visita puede editarla
    if usuario.tipo_usuario == TipoUsuarioEnum.VETERINARIO and visita_editable.veterinario_id != usuario_id:
        return jsonify({'msg':'No tienes permiso para actualizar esta visita'}), 403

    # comprobación de campos recibidos a editar
    
    if 'fecha' in data:
        fecha_str = data.get('fecha')
        if not fecha_str:
            return jsonify({'msg':'Fecha y hora requerida'}), 400
        try:
            fecha_dt = datetime.fromisoformat(fecha_str)
        except ValueError:
            return jsonify({'msg':'Formato de fecha y hora inválido (YYYY-MM-DDThh:mm)'}), 400
        if fecha_dt < datetime.now():
            return jsonify({'msg':'La fecha y hora no puede ser anterior al momento actual'}), 400
        visita_editable.fecha = fecha_dt

    if 'descripcion' in data:
        desc = data.get('descripcion','').strip()
        if not desc:
            return jsonify({'msg':'Descripción requerida'}), 400
        if len(desc) > 255:
            return jsonify({'msg':'La descripción no puede tener más de 255 caracteres'}), 400
        visita_editable.descripcion = desc

    db.session.commit()
    return jsonify({'msg':'Actualizada'}), 200

@visitas_bp.route('/eliminar/<int:visita_id>', methods=['DELETE'])
@jwt_required()
def eliminar_visita(visita_id):
    
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=usuario_id).first()
    visita_eliminable = Visita.query.filter_by(id=visita_id).first_or_404()
    
    if usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No tienes permiso para eliminar visitas'}), 403
    
    if usuario_id != visita_eliminable.veterinario_id and usuario.tipo_usuario == TipoUsuarioEnum.VETERINARIO:
        return jsonify({'msg':'No tienes permiso para eliminar esta visita'}), 403

    db.session.delete(visita_eliminable)
    db.session.commit()
    return jsonify({'msg': 'Eliminada'}), 200