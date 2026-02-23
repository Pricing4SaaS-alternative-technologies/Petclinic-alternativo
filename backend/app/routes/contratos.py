from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .clinicas import get_propietario_clinica

from app.models import Usuario, Prop_mascota, Veterinario, Prop_clinica
from app.models.enums import TipoUsuarioEnum, EspecialidadEnum

contratos = Blueprint('contratos', __name__, url_prefix='/api/contratos')

@contratos.route('/getContract/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
# TODO revisar jwtRequired para esta ruta, se usa en el login y no tenemos info ahora mismo en esa variable
def getContratoUsuario(user_id):
    space_client = current_app.space_client
    try:
        contract = current_app.run_async(space_client.contracts.get_user_id_contract(user_id))
    except Exception as e:
        if(e.status == 404):
            contract = None
        else:
            raise
    return contract

@contratos.route('/createContract', methods=['POST'])
@jwt_required()
# TODO Revisar posible incorporación del createContract en el auth_service eliminando la ruta y el jwt_required (conversion a auxiliar)
def createContrato(data):
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA:
        return jsonify({'message': 'Solo los dueños de clinicas pueden contrtar un plan de precios'}), 403
    
    data = request.get_json()
    space_client = current_app.space_client
    contract = current_app.run_async(space_client.contracts.add_contract(data))
    #Una vez con el contrato, le generamos el token de los pricings
    #current_app.run_async(space_client.featureEvaluators.generate_user_pricing_token(id_usuario))
    return contract


@contratos.route('services/<name>/pricing/<version>', methods=['GET'])
@jwt_required()
def getPlans(name, version):
    space_client = current_app.space_client
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    if usuario.tipo_usuario != TipoUsuarioEnum.PROP_CLINICA and usuario.tipo_usuario != TipoUsuarioEnum.ADMIN:
        return jsonify({'message': 'No tienes permiso para ver los planes'}), 403

    try:
        plans = current_app.run_async(space_client.service_context.get_pricing(name, version))
    except Exception as e:
        if(e.status == 404):
            contract = ''
        else:
            raise
    return plans

@contratos.route('/update/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def updateContratoUsuario(id_usuario):
    
    # Obtener datos del cuerpo de la petición
    data = request.get_json()
    
    # Obtener el nuevo plan del body
    nombre_plan = data.get('newPlan')
    
    dato_contrato = {
                "contractedServices": {
                    "PetClinic": "1.0.2"
                },
                "subscriptionPlans": {
                    "PetClinic": nombre_plan
                },
                "subscriptionAddOns": {}
            }
    print("Datos del contrato:", dato_contrato)
    space_client = current_app.space_client
    try:
        contrato = current_app.run_async(space_client.contracts.update_contract_subscription(str(id_usuario), dato_contrato))
        print(f"Contrato actualizado exitosamente: {contrato}")
        return jsonify(contrato), 200
        
    except Exception as e:
        print(f"Error al editar contrato: {e}")
        if hasattr(e, 'status') and e.status == 404:
            return jsonify({"error": "Contrato no encontrado"}), 404
    return contrato


@contratos.route('/generate-token/<int:id_usuario>', methods=['POST'])
@jwt_required()
def generate_user_pricing_token(id_usuario):
    
    usuario_loggeado_id = int(get_jwt_identity())
 
    if usuario_loggeado_id != id_usuario:
        return jsonify({'message': 'No tienes permiso para generar un token para este usuario'}), 403

    space_client = current_app.space_client
    try:
        token = current_app.run_async(space_client.featureEvaluators.generate_user_pricing_token(id_usuario))
        print(f"Token generado exitosamente para usuario ID: {id_usuario}", token)
        return jsonify({"token": token}), 200
    except Exception as e:
        print(f"Error al generar token: {e}")
        return jsonify({"error": "Error al generar token"}), 500


'''
@contratos.route('/crear-contrato-dueño-mascota/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def crear_contrato_dueño_mascota():
    id_usuario = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    
    if(usuario.tipo_usuario == TipoUsuarioEnum.PROP_CLINICA):
        contrato = getContratoUsuario(usuario.id)
        
    elif usuario.tipo_usuario in (TipoUsuarioEnum.VETERINARIO, TipoUsuarioEnum.PROP_MASCOTA):
        
        prop_clinica = get_propietario_clinica(usuario.clinica_id)
        contrato = getContratoUsuario(prop_clinica.id)
        
    try:
        contract_data = {
                "userContact": {
                    "userId": str(usuario.id),
                    "fistName": usuario.nombre,
                    "lastName": usuario.apellidos,
                    "email": usuario.email,
                    "username": usuario.usuario
                }
            }
        contrato.add(contract_data)
        createContrato(contrato)
    except Exception as e:
        print(f"Error al crear contrato: {e}")
        
    return jsonify({'message': 'Contrato creado con éxito'}), 201
'''

@contratos.route('/contractAddon/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def contratarAddon(id_usuario):
    # 1. Identificación del usuario y obtención del contrato actual
    id_usuario_jwt = int(get_jwt_identity())
    usuario = Usuario.query.get(id_usuario_jwt)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    contrato_actual = getContratoUsuario(usuario.id)
    
    # 2. Obtener el addon desde el cuerpo de la petición
    data = request.get_json()
    addon_key = data.get('addons') # Ej: "extraClinics"

    # 3. Mapeo: Nombre del Addon -> Feature de límite en el YAML
    addon_to_feature = {
        "extraPetOwners": "maxRegisteredPetOwners",
        "extraClinics": "maxRegisteredClinics",
        "extraPetHotelRooms": "maxPetHotelRooms",
        "extraPet": "maxRegisteredPets"
    }

    feature_name = addon_to_feature.get(addon_key)
    if not feature_name:
        return jsonify({"error": f"El addon '{addon_key}' no está mapeado a ninguna feature"}), 400

    full_feature_id = f"petclinic-{feature_name}"
    space_client = current_app.space_client
    
    # 4. Evaluación preventiva: ¿Podemos añadir una unidad más?
    try:
        evaluacion = current_app.run_async(
            space_client.featureEvaluators.evaluate(
                str(id_usuario_jwt), 
                full_feature_id, 
                {full_feature_id: 1}
            )
        )
        if not evaluacion.eval:
            return jsonify({
                "message": f"Límite de {addon_key} alcanzado según la política del plan.",
                "details": evaluacion.description
            }), 403
    except Exception as e:
        print(f"Advertencia en evaluación: {e}")

    # 5. PASO 1: Actualizar la suscripción (Sumar +1)
    plan_actual = contrato_actual.get('subscriptionPlans', {}).get('PetClinic', 'GOLD')
    addons_existentes = contrato_actual.get('subscriptionAddOns', {})
    
    # Extraer cantidad actual de forma segura (manejando si es int o dict)
    valor_previo = addons_existentes.get(addon_key, 0)
    if isinstance(valor_previo, dict):
        cantidad_actual = valor_previo.get('quantity', 0)
    else:
        cantidad_actual = valor_previo
        
    nueva_cantidad = cantidad_actual + 1
    
    # Preparamos el nuevo diccionario de addons manteniendo los demás
    nuevos_addons = dict(addons_existentes)
    nuevos_addons[addon_key] = {"quantity": nueva_cantidad}

    dato_contrato = {
        "contractedServices": {"PetClinic": "1.0.2"},
        "subscriptionPlans": {"PetClinic": plan_actual},
        "subscriptionAddOns": nuevos_addons
    }
    
    try:
        # Ejecutamos la actualización del contrato en el servicio de contratos
        contrato_actualizado = current_app.run_async(
            space_client.contracts.update_contract_subscription(str(id_usuario_jwt), dato_contrato)
        )

        # 6. PASO 2: Sincronizar Usage Levels (Vital para que el límite suba en Postman)
        # Esto envía los niveles actualizados al evaluador de features
        usage_levels_actualizados = contrato_actualizado.get('usageLevels', {})
        
        current_app.run_async(
            space_client.contracts.update_usage_levels(
                str(id_usuario_jwt), 
                usage_levels_actualizados
            )
        )
        
        print(f"Éxito: Addon {addon_key} actualizado a {nueva_cantidad} para usuario {id_usuario_jwt}")
        return jsonify(contrato_actualizado), 200
        
    except Exception as e:
        print(f"Error crítico en el proceso de suscripción: {e}")
        return jsonify({"error": str(e)}), 500