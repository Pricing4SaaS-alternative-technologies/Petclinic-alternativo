from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.adopcion import Adopcion
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.peticion_adopcion import Peticion_adopcion
from app.models.enums import TipoUsuarioEnum, EstadoPeticion

peticiones_bp = Blueprint('peticiones_adopcion', __name__, url_prefix='/api/peticiones_adopcion')

@peticiones_bp.route('/admin/listar', methods=['GET'])
@jwt_required()
def listar_peticiones():
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

# orientado para que el dueño de mascota vea las peticiones realizadas a una adopcion suya
@peticiones_bp.route('/adopcion/<int:adopcion_listar_id>', methods=['GET'])
@jwt_required()
def listar_peticiones_adopcion(adopcion_listar_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    adopcion_listar = Adopcion.query.get_or_404(adopcion_listar_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No estas autorizado para ver estas funciones'}), 403
    
    # Posiblemnte eliminable, ya que si no es una peticion creada por ti mismo (dueño_anteriro) no podras verla
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and adopcion_listar.dueño_anterior.clinica_id != usuario.clinica_id:
        return jsonify({'msg':'No puedes ver las peticiones de una adopcion de una clinica a la que no perteneces '}), 403
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and adopcion_listar.dueño_anterior.id != usuario_id:
        return jsonify({'msg':'No puedes ver las peticiones relacionada a una adopción que no has generado tu'}), 403
    
    peticiones = Peticion_adopcion.query.filter_by(adopcion_id=adopcion_listar_id)  # Asumiendo que tienes una relación definida en el modelo Adopcion
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

# Orientado para que los solicitantes vean sus propias peticiones de adopcion
@peticiones_bp.route('/usuario/<int:user_id>', methods=['GET'])
@jwt_required()
def listar_peticiones_usuario(user_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No estas autorizado para ver estas funciones'}), 403
    
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario_id != user_id:
        return jsonify({'msg':'No puedes ver las peticiones de otro usuario'}), 403
    
    peticiones = Peticion_adopcion.query.filter_by(solicitante_id=user_id).all()
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
    
    
@peticiones_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear_peticion():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No puedes crear adopciones sin ser un usuario de mascota'}), 403
    
    data = request.get_json()
    
    adopcion_id = data.get('adopcion_id')
    adopcion = Adopcion.query.get_or_404(adopcion_id)
    
    # No se puede hacer peticion de tu propia adopcion
    if adopcion.dueño_anterior_id == usuario_id:
        return jsonify({'msg':'No puedes solicitar la adopción de tu propia mascota'}), 403
    
    # No puedes hacer peticiones a adopciones que no son de la clinica (l creador dueo anterior debe pertenecer a la mismac linica)
    if usuario.tipo_usuario != TipoUsuarioEnum.ADMIN and adopcion.dueño_anterior.clinica_id != usuario.clinica_id:
        return jsonify({'msg':'No puedes ver las peticiones de una adopcion de una clinica a la que no perteneces '}), 403
    
    razon_adopcion = data.get('razon_adopcion','').strip()
    if not razon_adopcion:
        return jsonify({'msg':'Razón de adopción requerida'}), 400
    if len(razon_adopcion) > 255:
        return jsonify({'msg':'La razón de adopción no puede tener más de 255 caracteres'}), 400

    # vemos que no puedas generar otra petición para la isma adopción
    peticion_existente = Peticion_adopcion.query.filter_by(adopcion_id=adopcion_id, solicitante_id=usuario_id).first()
    if peticion_existente:
        return jsonify({'msg':'Tu petición de adopción ha sido rechazada por el propietario, no puedes hacer otra petición'}), 400
    
    nueva_peticion = Peticion_adopcion(
        razon_adopcion=razon_adopcion,
        adopcion_id=adopcion_id,
        solicitante_id=usuario_id
    )
    
    db.session.add(nueva_peticion)
    db.session.commit()
    
    return jsonify({'id': nueva_peticion.id}), 201

# TODO si durante la imposición del try salta algun error, se tiene que hacer rollback, hay que mirarlo
@peticiones_bp.route('/aceptar/<int:peticion_id>',methods=['PUT'])
@jwt_required()
def aceptar_peticion(peticion_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    peticion = Peticion_adopcion.query.get_or_404(peticion_id)
    adopcion_solicitada = Adopcion.query.get_or_404(peticion.adopcion_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and adopcion_solicitada.dueño_anterior_id != usuario_id:
        return jsonify({'msg':'No puedes aceptar peticiones de una adopcion que no has generado tu'}), 403
    
    if peticion.solicitante.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No puedes aceptar peticiones a un usuario que no es propietario de mascota'}), 403
    
    try: 
        # Actualizamos estado de adopción
        adopcion_solicitada.dueño_nuevo_id = peticion.solicitante_id
        adopcion_solicitada.adopcion_cerrada = True 
        adopcion_solicitada.save()
        
        # Actualizamos la petición y el resto
        peticion.estado_peticion = EstadoPeticion.APROBADA
        peticion.save()
        
        # buscar peticiones diferentes y rechazarlas
        Peticiones_restantes = Peticion_adopcion.query.filter()
        for p in Peticiones_restantes:
            if(p.id != peticion_id and p.adopcion_id == adopcion_solicitada.id ):
                p.estado_peticion = EstadoPeticion.RECHAZADA
                p.save()
        
        #Actualizamos por ultimo la mascota (aquie es donde se introduce la logica de la libreria)
        mascota_adoptada = Mascota.query.get_or_404(adopcion_solicitada.mascota_id)
        mascota_adoptada.dueño_id = peticion.solicitante_id
        mascota_adoptada.save()
        return jsonify({'id':peticion_id}), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500
    

@peticiones_bp.route('/rechazar/<int:peticion_id>', methods=['PUT'])
@jwt_required()
def rechazar_peticion(peticion_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    peticion = Peticion_adopcion.query.get_or_404(peticion_id)
    adopcion_solicitada = Adopcion.query.get_or_404(peticion.adopcion_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and adopcion_solicitada.dueño_anterior_id != usuario_id:
        return jsonify({'msg':'No puedes rechazar peticiones de una adopcion que no has generado tu'}), 403
    
    if peticion.solicitante.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'msg':'No puedes rechazar peticiones a un usuario que no es propietario de mascota'}), 403
    
    # Actualizamos la petición y el resto
    peticion.estado_peticion = EstadoPeticion.RECHAZADA
    peticion.save()
    return jsonify({'id':peticion_id}), 200

@peticiones_bp.route('/eliminar/<peticion_id>', methods=['DELETE'])
@jwt_required
def eliminar_peticion(peticion_id):
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    
    peticion = Peticion_adopcion.query.get_or_404(peticion_id)
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and peticion.solicitante_id != usuario_id:
        return jsonify({'msg':'No puedes eliminar peticiones que no son tuyas'}), 403
    
    peticion.delete()
    return jsonify({'msg': 'Eliminada'}), 200
    
    
    
        
    