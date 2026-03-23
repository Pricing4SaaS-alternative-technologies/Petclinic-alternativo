from flask import Blueprint, request, jsonify, current_app
from app.models.usuario import Usuario
from app.models.veterinario import Veterinario
from app.models.prop_mascota import Prop_mascota
from app.models.prop_clinica import Prop_clinica
from app.models.enums import TipoUsuarioEnum
from flask_jwt_extended import jwt_required, get_jwt_identity

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    user_data = {
        'id': usuario.id,
        'nombre': usuario.nombre,
        'apellidos': usuario.apellidos,
        'usuario': usuario.usuario,
        'email': usuario.email,
        'tipo_usuario': usuario.tipo_usuario.name if usuario.tipo_usuario else None
    }

    if isinstance(usuario, Prop_mascota):
        user_data.update({
            'direccion': usuario.direccion,
            'telefono': usuario.telefono,
            'clinica_id': usuario.clinica_id
        })
        
    elif isinstance(usuario, Prop_clinica):
        user_data.update({
            'telefono': usuario.telefono
        })
        
    elif isinstance(usuario, Veterinario):
        user_data.update({
            'ciudad': usuario.ciudad,
            'especialidades': usuario.especialidades,
            'clinica_id': usuario.clinica_id
        })

    return jsonify({'message': 'Perfil obtenido con éxito', 'datos': user_data}), 200


@usuarios_bp.route('/perfil/editar', methods=['PUT'])
@jwt_required()
def edit_perfil():
    id_usuario = get_jwt_identity()
    data = request.get_json()
    
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    
    if nombre is not None:
        n = nombre.strip()
        if len(n) > 100:
            return jsonify({'message': 'El nombre no puede tener más de 100 caracteres'}), 400
        usuario.nombre = n

    if apellidos is not None:
        a = apellidos.strip()
        if len(a) > 100:
            return jsonify({'message': 'Los apellidos no pueden tener más de 100 caracteres'}), 400
        usuario.apellidos = a

    
    if isinstance(usuario, (Prop_mascota, Prop_clinica)):
        telefono = data.get('telefono')
        if telefono is not None:
            t = telefono.strip()
            if not t.isdigit() or len(t) != 9:
                return jsonify({'message': 'El teléfono debe tener 9 dígitos numéricos'}), 400
            usuario.telefono = t

    if isinstance(usuario, Prop_mascota):
        direccion = data.get('direccion')
        if direccion is not None:
            d = direccion.strip()
            if len(d) > 100:
                return jsonify({'message': 'La dirección no puede tener más de 100 caracteres'}), 400
            usuario.direccion = d

    if isinstance(usuario, Veterinario):
        ciudad = data.get('ciudad')
        if ciudad is not None:
            c = ciudad.strip()
            if len(c) > 40:
                return jsonify({'message': 'La ciudad no puede tener más de 40 caracteres'}), 400
            usuario.ciudad = c
            
        especialidades = data.get('especialidades')
        if especialidades is not None:
            try:
                usuario.set_especialidades(especialidades)
            except Exception as e:
                return jsonify({'message': f'Error al procesar las especialidades: {str(e)}'}), 400

    try:
        usuario.save()
        
        datos_contacto_space = {
            "firstName": usuario.nombre, 
            "lastName": usuario.apellidos,
            "email": usuario.email,
            "username": usuario.usuario
        }

        if isinstance(usuario, (Prop_mascota, Prop_clinica)) and usuario.telefono:
            datos_contacto_space["phone"] = usuario.telefono

        space_client = current_app.space_client
        current_app.run_async(
            space_client.contracts.update_user_contact(str(id_usuario), datos_contacto_space)
        )

        return jsonify({'message': 'Perfil actualizado correctamente en BBDD y SPACE'}), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500