
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.adopcion import Adopcion
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.enums import TipoUsuarioEnum

adopciones_bp = Blueprint('adopciones', __name__, url_prefix='/api/adopciones')

@adopciones_bp.route('/admin/listar', methods=['GET'])
@jwt_required()
def listar_adopciones():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No autorizado'}), 403
    
    adopciones = Adopcion.query.all()
    return jsonify([
        {
            'id': a.id,
            'descripcion': a.descripcion,
            'adopcion_cerrada': a.adopcion_cerrada,
            'fecha_creacion': a.fecha_creacion.isoformat(),
            'mascota_id': a.mascota_id,
            'mascota_nombre': a.mascota.nombre,
            'dueño_anterior_id': a.dueño_anterior_id,
            'dueño_anterior_nombre': a.dueño_anterior.nombre+' '+a.dueño_anterior.apellidos ,
            'dueño_nuevo_id': a.dueño_nuevo_id,
            'dueño_nuevo_nombre': a.dueño_nuevo.nombre+' '+a.dueño_nuevo.apellidos if a.dueño_nuevo else "No tiene dueño adoptivo"
        }
        for a in adopciones
        ]), 200

# Este metodo actua como filtro para el admin o como el listar_todas para el prop_mascota
@adopciones_bp.route('/usuario/<int:user_id>', methods=['GET'])
@jwt_required()
def listar_adopciones_usuario(user_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario_buscado = Usuario.query.get_or_404(user_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario_buscado.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No estas autorizado para ver estas funciones'}), 403
    
    if usuario_buscado.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'El ID proporcionado no corresponde a un propietario de mascota'}), 400
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario_id != user_id:
        return jsonify({'msg':'No puedes listar las adopciones de otro usuario'}), 403
    
    adopciones = Adopcion.query.filter(Adopcion.dueño_anterior_id==user_id).all()
    return jsonify([
        {
            'id': a.id,
            'descripcion': a.descripcion,
            'adopcion_cerrada': a.adopcion_cerrada,
            'fecha_creacion': a.fecha_creacion.isoformat(),
            'mascota_id': a.mascota_id,
            'mascota_nombre': a.mascota.nombre,
            'dueño_anterior_id': a.dueño_anterior_id,
            'dueño_anterior_nombre': a.dueño_anterior.nombre+' '+a.dueño_anterior.apellidos ,
            'dueño_nuevo_id': a.dueño_nuevo_id,
            'dueño_nuevo_nombre': a.dueño_nuevo.nombre+' '+a.dueño_nuevo.apellidos if a.dueño_nuevo else "No tiene dueño adoptivo"
        }
        for a in adopciones
        ]), 200

# Orientado para que los solicitantes puedan ver las adopciones disponibles ne su clinica
@adopciones_bp.route('/clinica/<int:clinica_id>', methods=['GET'])
@jwt_required()
def listar_adopciones_clinica(clinica_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No estas autorizado para ver estas funciones'}), 403
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and usuario.clinica_id != clinica_id:
        return jsonify({'msg':'No puedes listar las adopciones de una clinica a la que no perteneces'}), 403

    adopciones = Adopcion.query.filter(Adopcion.dueño_anterior.clinica_id==clinica_id).all()
    return jsonify([
        {
            'id': a.id,
            'descripcion': a.descripcion,
            'adopcion_cerrada': a.adopcion_cerrada,
            'fecha_creacion': a.fecha_creacion.isoformat(),
            'mascota_id': a.mascota_id,
            'mascota_nombre': a.mascota.nombre,
            'dueño_anterior_id': a.dueño_anterior_id,
            'dueño_anterior_nombre': a.dueño_anterior.nombre+' '+a.dueño_anterior.apellidos ,
            'dueño_nuevo_id': a.dueño_nuevo_id,
            'dueño_nuevo_nombre': a.dueño_nuevo.nombre+' '+a.dueño_nuevo.apellidos if a.dueño_nuevo else "No tiene dueño adoptivo"
        }
        for a in adopciones
        ]), 200

@adopciones_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear_adopcion():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No puedes crear adopciones sin ser un usuario de mascota'}), 403
    
    data = request.get_json()

    desc = data.get('descripcion', '').strip()
    if not desc:
        return jsonify({'msg':'Descripción requerida'}), 400
    if len(desc) > 255:
        return jsonify({'msg':'La descripción no puede tener más de 255 caracteres'}), 400

    mascota_encontrada = Mascota.query.get_or_404(data['mascota_id'])
    if mascota_encontrada.dueño_id != usuario_id:
        return jsonify({'msg':'No puedes poner en adopcion una mascota que no es tuya'}),400
    
    adopcion_crear = Adopcion(
      descripcion=desc,
      mascota_id=mascota_encontrada.id,
    )
    adopcion_crear.dueño_anterior_id = usuario_id

    adopcion_crear.save()
    return jsonify({"id": adopcion_crear.id}), 201


@adopciones_bp.route('/eliminar/<int:adopcion_id>', methods=['DELETE'])
@jwt_required()
def eliminar_adopcion(adopcion_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    adopcion_borrar = Adopcion.query.get_or_404(adopcion_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'msg':'No puedes eliminar adopciones sin ser un usuario de mascota o admin'}), 403

    if adopcion_borrar.dueño_anterior_id != usuario_id:
        return jsonify({'msg':'No puedes eliminar una adopcion de otro dueño!'}), 403

    adopcion_borrar.delete()
    return jsonify({'msg': 'Eliminada'}), 200
