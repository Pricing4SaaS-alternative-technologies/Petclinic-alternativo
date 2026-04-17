from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from app.extensions import db
from app.models import Usuario, Mascota, Consulta, Respuesta_consulta, Clinica, Prop_mascota, Veterinario
from app.models.enums import TipoUsuarioEnum, EstadoConsulta

consultas = Blueprint('consultas', __name__, url_prefix='/api/consultas')

@consultas.route('/getConsultas/<int:id_usuario>', methods=['GET'])
@jwt_required()
def get_consultas(id_usuario):
    current_id_usuario = get_jwt_identity()

    # Validación de identidad para la ruta
    if str(current_id_usuario) != str(id_usuario):
        return jsonify({'message': 'No tienes permiso para ver las consultas de otro usuario'}), 403

    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    consultas_db = []

    # 1. DUEÑO DE MASCOTA: Solo sus propias consultas
    if usuario.tipo_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        consultas_db = Consulta.query.filter_by(dueño_id=usuario.id).all()

    # 2. VETERINARIO: Consultas de su clínica (específicas para él o genéricas/null)
    elif usuario.tipo_usuario == TipoUsuarioEnum.VETERINARIO:
        # Buscamos a todos los dueños de su misma clínica
        dueños_clinica = Prop_mascota.query.filter_by(clinica_id=usuario.clinica_id).all()
        ids_dueños = [d.id for d in dueños_clinica]
        
        if ids_dueños:
            # Filtramos: consultas de esos dueños Y (que sean para este vet O que sean genéricas/null)
            consultas_db = Consulta.query.filter(
                Consulta.dueño_id.in_(ids_dueños),
                db.or_(Consulta.vet_id == usuario.id, Consulta.vet_id == None)
            ).all()

    elif usuario.tipo_usuario == TipoUsuarioEnum.ADMIN:
        consultas_db = Consulta.query.all()

    return jsonify([{
        "id": c.id,
        "titulo": c.titulo,
        "descripcion": c.descripcion,
        "estado": c.estado_consulta.name if c.estado_consulta else 'PENDIENTE',
        "fecha": c.fecha_creacion.isoformat() if c.fecha_creacion else None,
        "dueño_id": c.dueño_id,
        "mascota_id": c.mascota_id,
        "vet_id": c.vet_id
    } for c in consultas_db]), 200
    
@consultas.route('/get-veterinarios', methods=['GET'])
@jwt_required()
def get_veterinarios_clinica():
    id_usuario = get_jwt_identity()
    
    prop = Prop_mascota.query.get(id_usuario)
    if not prop or not prop.clinica_id:
        return jsonify([]), 200
    
    vets = Veterinario.query.filter_by(clinica_id=prop.clinica_id).all()
    
    return jsonify([
        {
            "id": v.id, 
            "nombre": f"{v.nombre} {v.apellidos}",
            # Añadimos las especialidades aquí para que Vue las reciba
            "especialidades": v.especialidades 
        } for v in vets
    ]), 200
    

@consultas.route('/crear-consulta', methods=['POST'])
@jwt_required()
def crear_consulta():
    data = request.get_json() or {}
    id_usuario = int(get_jwt_identity())
    
    # Validamos que sea un dueño de mascota
    usuario = Usuario.query.get(id_usuario)
    if not usuario or usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA:
        return jsonify({'message': 'No tienes permiso para crear consultas'}), 403

    titulo = data.get('titulo', '').strip()
    descripcion = data.get('descripcion', '').strip()
    mascota_id = data.get('mascota_id')
    vet_id = data.get('vet_id') 

    if not titulo or not descripcion or not mascota_id:
        return jsonify({"msg": "Campos obligatorios faltantes"}), 400
    
    if titulo and len(titulo) > 50:
        return jsonify({"msg": "El título excede los 50 caracteres"}), 400
    
    if descripcion and len(descripcion) > 500:
        return jsonify({"msg": "La descripción excede los 500 caracteres"}), 400

    mascota = Mascota.query.get(mascota_id)
    if not mascota or mascota.dueño_id != id_usuario:
        return jsonify({"msg": "Mascota no válida"}), 404

    try:
        nueva_consulta = Consulta(
            titulo=titulo,
            descripcion=descripcion,
            dueño_id=id_usuario,
            mascota_id=mascota_id,
            vet_id=vet_id
        )
        # Sincronizamos la fecha enviada o usamos la actual
        fecha_str = datetime.now().isoformat()
        nueva_consulta.fecha_creacion = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S.%f')
            
        nueva_consulta.save()
        return jsonify({"id": nueva_consulta.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

@consultas.route('/getRespuestas/<int:consulta_id>', methods=['GET'])
@jwt_required()
def get_respuestas(consulta_id):
    consulta = Consulta.query.get(consulta_id)
    if not consulta:
        return jsonify({"msg": "Consulta no encontrada"}), 404
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.get(user_id)
     
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    es_dueño = (consulta.dueño_id == user_id)
    
    es_vet_autorizado = False
    if usuario.tipo_usuario == TipoUsuarioEnum.VETERINARIO:
        dueño_consulta = Prop_mascota.query.get(consulta.dueño_id)
        if dueño_consulta and dueño_consulta.clinica_id == usuario.clinica_id:
            if consulta.vet_id is None or consulta.vet_id == user_id:
                es_vet_autorizado = True

    es_admin = (usuario.tipo_usuario == TipoUsuarioEnum.ADMIN)

    if not (es_dueño or es_vet_autorizado or es_admin):
        return jsonify({'message': 'No tienes permiso para ver las respuestas de esta consulta'}), 403
    
    respuestas_json = []
    for r in consulta.respuestas:
        # Buscamos al veterinario que hizo esta respuesta
        vet = Veterinario.query.get(r.vet_id) if hasattr(r, 'vet_id') and r.vet_id else None
        
        # Preparamos los datos por si el veterinario ya no existe en la BD
        nombre_vet = f"{vet.nombre} {vet.apellidos}" if vet else "Veterinario Clínico"
        especialidades_vet = vet.especialidades if vet else []

        respuestas_json.append({
            "id": r.id,
            "titulo": r.titulo,
            "descripcion": r.descripcion,
            "fecha": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
            "nombre_vet": nombre_vet,
            "especialidades_vet": especialidades_vet
        })
    
    return jsonify(respuestas_json), 200

@consultas.route('/responder-consulta/<int:consulta_id>', methods=['POST'])
@jwt_required()
def crear_respuesta(consulta_id):
    id_usuario_actual = get_jwt_identity()
    usuario = Usuario.query.get(id_usuario_actual)

    if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.VETERINARIO and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN):
        return jsonify({'message': 'No tienes permiso para responder a esta consulta'}), 403

    consulta_original = Consulta.query.get(consulta_id)
    if not consulta_original:
        return jsonify({"msg": "Consulta no encontrada"}), 404

    data = request.get_json() or {}
    titulo = data.get('titulo', '').strip()
    descripcion = data.get('descripcion', '').strip()

    if not titulo or not descripcion:
        return jsonify({"msg": "El título y la descripción son obligatorios"}), 400

    if len(titulo) > 50:
        return jsonify({"msg": "El título debe tener menos de 50 caracteres"}), 400

    if len(descripcion) > 100:
        return jsonify({"msg": "La descripción debe tener menos de 100 caracteres"}), 400

    try:
        nueva_respuesta = Respuesta_consulta(
            titulo=titulo,
            descripcion=descripcion,
            fecha_creacion=datetime.now(),
            consulta_id=consulta_id
        )
        
        nueva_respuesta.vet_id = usuario.id 
        
        db.session.add(nueva_respuesta)
        db.session.commit()
        
        return jsonify({"msg": "Respuesta enviada correctamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al crear respuesta: {str(e)}"}), 500
    
    
@consultas.route('/cerrar-consulta/<int:consulta_id>', methods=['PUT'])
@jwt_required()
def cerrar_consulta(consulta_id):
    id_usuario_actual = int(get_jwt_identity())
    
    consulta = Consulta.query.get(consulta_id)
    
    if not consulta:
        return jsonify({"msg": "Consulta no encontrada"}), 404
        
    if consulta.dueño_id != id_usuario_actual:
        return jsonify({"msg": "No tienes permiso para cerrar esta consulta"}), 403
    
    user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.PROP_MASCOTA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN):
        return jsonify({'message': 'No tienes permiso para cambiar el estado de esta consulta'}), 403

    try:
        consulta.estado_consulta = EstadoConsulta.RESUELTA
        
        db.session.commit()
        
        return jsonify({"msg": "Consulta marcada como resuelta por el dueño"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al cerrar: {str(e)}"}), 500