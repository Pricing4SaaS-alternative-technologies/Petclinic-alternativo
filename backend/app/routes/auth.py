# backend/app/routes/auth.py
from .clinicas import get_propietario_clinica
from .contratos import getContratoUsuario
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models import Usuario, Prop_mascota, Veterinario, Prop_clinica
from app.models.enums import TipoUsuarioEnum, EspecialidadEnum

auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("info recopilada", data)
    # datos del usuario basico
    tipo_str = data.get('tipo_usuario')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    usuario = data.get('usuario')
    email = data.get('email')
    contraseña = data.get('contraseña')

    if not tipo_str or not all([nombre, apellidos, usuario, email, contraseña]):
        return jsonify({'message': 'Faltan datos obligatorios'}), 400

    # Validar tipo
    try:
        tipo_enum = TipoUsuarioEnum[tipo_str]
        if tipo_enum == TipoUsuarioEnum.USUARIO:
            return jsonify({'message': 'Tipo de usuario no permitido'}), 400
    except KeyError:
        return jsonify({'message': 'Tipo de usuario inválido'}), 400
    
    # Comprobar si ya existe usuario
    if Usuario.find_by_usuario_or_email(usuario, email):
        return jsonify({'message': 'Usuario o email ya registrado'}), 400

    # Crear instancia según tipo
    user = None

    if tipo_enum == TipoUsuarioEnum.PROP_MASCOTA:
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        clinica = data.get('clinica_id')
        
        if not direccion or not telefono or not clinica:
            return jsonify({'message': 'No estan rellenos los campos obligatorios para dueño de mascota'}), 400
        user = Prop_mascota(nombre, apellidos, usuario, email, contraseña, direccion, telefono, clinica)

    elif tipo_enum == TipoUsuarioEnum.VETERINARIO:
        ciudad = data.get('ciudad')
        especialidades_raw = data.get('especialidades', [])
        valores_validos = [e.value for e in EspecialidadEnum]
        
        if not all(e in valores_validos for e in especialidades_raw):
            return jsonify({'message': 'Algunas especialidades no son válidas'}), 400
        
        clinica = data.get('clinica_id')
        try:
            especialidades_enum = [EspecialidadEnum(e) for e in especialidades_raw]
        except ValueError:
            return jsonify({'message': 'Especialidades inválidas'}), 400
        user = Veterinario(nombre, apellidos, usuario, email, contraseña, especialidades_enum, ciudad, clinica)

    elif tipo_enum == TipoUsuarioEnum.PROP_CLINICA:
        telefono = data.get('telefono')
        if not telefono:
            return jsonify({'message': 'No estan rellenos los campos obligatorios para dueño de mascota'}), 400
        user = Prop_clinica(nombre, apellidos, usuario, email, contraseña, telefono)

    if user is None:
        return jsonify({'message': 'Error al crear el usuario'}), 500


    try:
        user.save()
        space_client = current_app.space_client
        evaluacion = current_app.run_async(space_client.featureEvaluators.evaluate(get_propietario_clinica(user.clinica_id).id, "petclinic-registeredPetOwners", {"petclinic-maxRegisteredPetOwners": 1}))
        if evaluacion.eval == False:
            user.delete()
            return jsonify({'message': 'No se puede crear más usuarios para la clinica actual.'}), 403
    except Exception as e:  
        user.delete()
        return jsonify({'message': str(e)}), 500
    
    if tipo_enum == TipoUsuarioEnum.PROP_CLINICA:
        try:
            contract_data = {
                "userContact": {
                    "userId": str(user.id),
                    "fistName": user.nombre,
                    "lastName": user.apellidos,
                    "email": user.email,
                    "username": user.usuario
                },
                "billingPeriod": {
                    "autoRenew": True,
                    "renewalDays": 30
                },
                "contractedServices": {
                    "PetClinic": "1.0.0"
                },
                "subscriptionPlans": {
                    "PetClinic": "SILVER"
                },
                "subscriptionAddOns": {}
            }
            
            print("Datos del contrato:", contract_data)
            resultado = current_app.run_async(space_client.contracts.add_contract(contract_data))
            print(f"Contrato creado exitosamente: {resultado}")
            
        except Exception as e:
            print(f"Error al crear contrato: {e}")
            return jsonify({
                'message': f'{tipo_enum.value.capitalize()} registrado, pero falló la creación del contrato',
                'error': str(e)
            }), 201
            
    elif tipo_enum == TipoUsuarioEnum.PROP_MASCOTA:
        try:
            contrato_clinic_owner = getContratoUsuario(get_propietario_clinica(user.clinica_id).id)
            print("Contrato del propietario de la clínica obtenido:", contrato_clinic_owner)
            contrato_pet_owner = contrato_clinic_owner.copy()

            contrato_pet_owner["userContact"] = {
            "userId": str(user.id),
            "firstName": user.nombre,
            "lastName": user.apellidos,
            "email": user.email,
            "username": user.usuario
            }
            
            space_client = current_app.space_client
            resultado = current_app.run_async(space_client.contracts.add_contract(contrato_pet_owner))
            print(f"Contrato creado exitosamente para dueño de mascota ID: {user.id}", contrato_pet_owner)
        except Exception as e:
            print(f"Error al crear contrato: {e}")
            return jsonify({
                'message': f'{tipo_enum.value.capitalize()} registrado, pero falló la creación del contrato',
                'error': str(e)
            }), 201
        
    return jsonify({'message': f'{tipo_enum.value.capitalize()} registrado con éxito'}), 201

# meter el plan de precios que tiene contratado en ese momento como respuesta
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_o_mail = data.get('usuario_o_email')
    contraseña = data.get('contraseña')
    contrato = None
    if not user_o_mail or not contraseña:
        return jsonify({'message': 'Faltan datos'}), 400

    usuario = Usuario.find_by_usuario_or_email(user_o_mail, user_o_mail)

    if not usuario or not usuario.check_password(contraseña):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Incluir tipo en el token
    access_token = create_access_token(identity=str(usuario.id))
    usuario_payload = {
        'id': usuario.id,
        'usuario': usuario.usuario,
        'email': usuario.email,
        'tipo': usuario.tipo_usuario.value
    }
    if(usuario.tipo_usuario == TipoUsuarioEnum.PROP_CLINICA):
        contrato = getContratoUsuario(usuario.id)
        
    elif usuario.tipo_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        contrato = getContratoUsuario(usuario.id)
        
        prop_clinica = get_propietario_clinica(usuario.clinica_id)
        usuario_payload['clinica_id'] = usuario.clinica_id
        usuario_payload['prop_clinica_id'] = prop_clinica.id
        
    elif usuario.tipo_usuario == TipoUsuarioEnum.VETERINARIO:
        
        prop_clinica = get_propietario_clinica(usuario.clinica_id)
        contrato = getContratoUsuario(prop_clinica.id)
        
        usuario_payload['clinica_id'] = usuario.clinica_id
        usuario_payload['prop_clinica_id'] = prop_clinica.id

    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'usuario': usuario_payload,
        'contrato': contrato
    }), 200


@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    usuario = Usuario.query.get(identity)
    return jsonify({
        'message': f'Bienvenido, {usuario.usuario}',
        'tipo': usuario.tipo_usuario.value,
        'user_id': identity["id"]
    }), 200



@auth.route('/especialidades', methods=['GET'])
def get_especialidades():
    from app.models.enums import EspecialidadEnum
    return jsonify([e.value for e in EspecialidadEnum])

@auth.route('/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    identity = int(get_jwt_identity())
    usuario_registrado = Usuario.query.get(identity)
    usuario_borrar = Usuario.query.get(user_id)

    if not usuario_borrar:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    if(usuario_registrado.tipo_usuario != TipoUsuarioEnum.ADMIN and usuario_registrado.id != usuario_borrar.id):
        return jsonify({'message': 'No tienes permiso para eliminar este usuario'}), 403
    
    if usuario_borrar.tipo_usuario == TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No se puede eliminar un usuario administrador'}), 403

    space_client = current_app.space_client
    
    if usuario_borrar.tipo_usuario == TipoUsuarioEnum.PROP_MASCOTA:
        if usuario_borrar.clinica_id:
            prop_clinica = get_propietario_clinica(usuario_borrar.clinica_id)
            contrato = getContratoUsuario(prop_clinica.id)
            if contrato:
                usage_levels = { 
                    "petclinic": {
                        "maxRegisteredPetOwners": -1
                    }
                }
                current_app.run_async(space_client.contracts.update_usage_levels(prop_clinica.id, usage_levels))
    
    usuario_borrar.delete()
    return jsonify({'message': 'Usuario eliminado con éxito'}), 200