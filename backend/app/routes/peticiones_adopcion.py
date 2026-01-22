from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.adopcion import Adopcion
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.peticion_adopcion import Peticion_adopcion
from app.models.enums import TipoUsuarioEnum

bp = Blueprint('peticiones_adopcion', __name__, url_prefix='/api/peticiones_adopcion')

@bp.route('/admin/listar', methods=['GET'])
@jwt_required()
def listar_todas_peticiones_adopcion():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No estas autorizado para usar esta funcion'}), 403
    
    peticiones = Peticion_adopcion.query.all()
    return jsonify([
        {
            'id': p.id,
            'razon_adopcion': p.razon_adopcion,
            'fecha_solicitud': p.fecha_solicitud.isoformat(),
            'estado_peticion': p.estado_peticion.value,
            'adopcion_id': p.adopcion_id,
            'adopcion_mascota_nombre': p.adopcion.mascota.nombre,
            'solicitante_id': p.solicitante_id,
            'solicitante_nombre': p.solicitante.nombre + ' ' + p.solicitante.apellidos
        }
        for p in peticiones
    ]), 200

@bp.route('/adopcion/<int:adopcion_id>', methods=['GET'])
@jwt_required()
def listar_peticiones_adopcion(adopcion_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    adopcion_listar = Adopcion.query.get_or_404(adopcion_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No estas autorizado para ver estas funciones'}), 403
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and adopcion_listar.dueño_anterior.clinica_id != usuario.clinica_id:
        return jsonify({'msg':'No puedes ver las peticiones de una adopcion de una clinica a la que no perteneces '}), 403
    
    peticiones = adopcion_listar.peticiones_adopcion  # Asumiendo que tienes una relación definida en el modelo Adopcion
    return jsonify([
        {
            'id': p.id,
            'razon_adopcion': p.razon_adopcion,
            'fecha_solicitud': p.fecha_solicitud.isoformat(),
            'estado_peticion': p.estado_peticion.value,
            'adopcion_id': p.adopcion_id,
            'adopcion_mascota_nombre': p.adopcion.mascota.nombre,
            'solicitante_id': p.solicitante_id,
            'solicitante_nombre': p.solicitante.nombre + ' ' + p.solicitante.apellidos
        }
        for p in peticiones
    ]), 200
    
