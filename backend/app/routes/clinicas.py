from flask import Blueprint, request, jsonify
from app.models.clinica import Clinica
from app.models.usuario import Usuario
from app.models.veterinario import Veterinario
from app.models.prop_mascota import Prop_mascota
from app.models.enums import TipoUsuarioEnum, Plan
from flask_jwt_extended import jwt_required, get_jwt_identity

clinicas_bp = Blueprint('clinicas', __name__, url_prefix='/api/clinicas')

@clinicas_bp.route('/listar-todas', methods=['GET'])
@jwt_required(optional=True)
def get_clinicas():
    
    id_usuario = get_jwt_identity()
    
    clinicas = Clinica.query.all()
    
    if not id_usuario:
        return jsonify([
            {
                'id': c.id,
                'nombre': c.nombre
            }
            for c in clinicas
        ])
    else:
        return jsonify([
            {
                'id': c.id,
                'nombre': c.nombre,
                'direccion': c.direccion,
                'telefono': c.telefono,
                'plan': c.plan.value,
                'propietario': c.propietario
            }
            for c in clinicas
        ])

@clinicas_bp.route('/listar/<int:propietario_id>', methods=['GET'])
@jwt_required()
def get_clinicas_by_propietario(propietario_id):
    id_usuario = get_jwt_identity()
    # rol del usuairo por si es admin
    rol_usuario = Usuario.query.filter_by(id=id_usuario).first().tipo_usuario
    
    if (id_usuario != propietario_id and rol_usuario != TipoUsuarioEnum.PROP_CLINICA) and rol_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver estas clínicas'}), 403
    
    clinicas = Clinica.query.filter_by(propietario_id=propietario_id).all()
    
    return jsonify([
        {
            'id': c.id,
            'nombre': c.nombre,
            'direccion': c.direccion,
            'telefono': c.telefono,
            'plan': c.plan.value
        }
        for c in clinicas
    ]), 200

@clinicas_bp.route('/crear', methods=['POST'])
@jwt_required()
def create_clinica():
    data = request.get_json()
    id_usuario = get_jwt_identity()
    
    # Comprobar si el usuario es propietario de clínica
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN):
        return jsonify({'message': 'No tienes permiso para crear clínicas'}), 403
    
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    telefono = data.get('telefono')
    
    if not all([nombre, direccion, telefono]):
        return jsonify({'message':'Faltan datos obligatorios'}), 400

    # validaciones de longitud y formato
    if len(nombre) > 50:
        return jsonify({'message':'El nombre no puede tener más de 50 caracteres'}), 400
    if len(direccion) > 100:
        return jsonify({'message':'La dirección no puede tener más de 100 caracteres'}), 400
    if not telefono.isdigit() or len(telefono) != 9:
        return jsonify({'message':'El teléfono debe tener 9 dígitos numéricos'}), 400
    
    nueva_clinica = Clinica(nombre=nombre, direccion=direccion, telefono=telefono, propietario_id=id_usuario)
    
    try:
        nueva_clinica.save()
        return jsonify({'message': 'Clínica creada correctamente', 'clinica_id': nueva_clinica.id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@clinicas_bp.route('/editar/<int:clinica_id>', methods=['PUT'])
@jwt_required()
def edit_clinica(clinica_id):
    data = request.get_json()
    id_usuario = get_jwt_identity()
    clinica = Clinica.query.filter_by(id=clinica_id).first()
    
    if clinica is None:
        return jsonify({'message': 'La clínica no existe'}), 404
    else:
        
        usuario = Usuario.query.filter_by(id=id_usuario).first()
        
        if (id_usuario != clinica.propietario_id and usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA) and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
            return jsonify({'message': 'No tienes permiso para editar esta clínica'}), 403
        
        nombre = data.get('nombre')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        
        if nombre is not None:
            n = nombre.strip()
            if len(n) > 50:
                return jsonify({'message':'El nombre no puede tener más de 50 caracteres'}), 400
            clinica.nombre = n

        if direccion is not None:
            d = direccion.strip()
            if len(d) > 100:
                return jsonify({'message':'La dirección no puede tener más de 100 caracteres'}), 400
            clinica.direccion = d

        if telefono is not None:
            t = telefono.strip()
            if not t.isdigit() or len(t) != 9:
                return jsonify({'message':'El teléfono debe tener 9 dígitos numéricos'}), 400
            clinica.telefono = t

        try:
            clinica.save()
            return jsonify({'message': 'Clínica actualizada correctamente'}), 201
        except Exception as e:
            return jsonify({'message': str(e)}), 500      


@clinicas_bp.route('/cambiar-plan/<int:clinica_id>', methods=['POST'])
@jwt_required()
def cambiar_plan(clinica_id):
    data = request.get_json()
    id_usuario = get_jwt_identity()
    clinica = Clinica.query.filter_by(id=clinica_id).first()
    
    if clinica is None:
        return jsonify({'message': 'La clínica no existe'}), 404
    else:
        
        usuario = Usuario.query.filter_by(id=id_usuario).first()
        
        if not usuario or (usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN) or id_usuario != clinica.propietario_id:
            return jsonify({'message': 'No tienes permiso para actualizar el plan de esta clínica'}), 403
        
        plan = data.get('plan')
        if plan is None or plan not in [p.value for p in Plan]:
            return jsonify({'message': 'Plan inválido'}), 400
        
        clinica.plan = plan
        try:
            clinica.save()
            return jsonify({'message': 'Plan de la clinica actualizado'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500  


@clinicas_bp.route('/eliminar/<int:clinica_id>', methods=['DELETE'])
@jwt_required()
def delete_clinica(clinica_id):
    id_usuario = get_jwt_identity()
    clinica = Clinica.query.filter_by(id=clinica_id).first()
    
    if clinica is None:
        return jsonify({'message': 'La clínica no existe'}), 404
    
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if (id_usuario != clinica.propietario_id and usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA) and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para eliminar esta clínica'}), 403
    
    try:
        # nos cargamos primero a todos los usuarios base ligados a la clinica a borrar
        for propietario in Prop_mascota.query.filter_by(clinica_id=clinica.id).all():
            propietario.delete()
        for veterinario in Veterinario.query.filter_by(clinica_id=clinica.id).all():
            veterinario.delete()
        # Ahora sí, borra la clínica
        clinica.delete()
        return jsonify({'message': 'Clínica eliminada correctamente'}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500