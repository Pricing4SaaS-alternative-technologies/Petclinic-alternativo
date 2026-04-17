from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .clinicas import get_propietario_clinica

from app.models import Usuario, Prop_mascota, Veterinario, Prop_clinica, Clinica
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
        pricing_data = current_app.run_async(space_client.service_context.get_pricing(name, version))
    except Exception as e:
        if hasattr(e, 'status') and e.status == 404:
            return jsonify({'message': 'Catálogo de precios no encontrado'}), 404
        else:
            raise

    planes = pricing_data.get('plans', {})
    limites_uso = pricing_data.get('usageLimits', {})
    addons = pricing_data.get('addOns', {})

    for nombre_plan, info_plan in planes.items():
        limites_del_plan = info_plan.get('usageLimits')
        features_del_plan = info_plan.get('features', {})

        if isinstance(limites_del_plan, dict):
            limites_a_borrar = []
            
            for limite_key in limites_del_plan.keys():
                info_limite_global = limites_uso.get(limite_key, {})
                linked_features = info_limite_global.get('linkedFeatures', [])
                
                if linked_features:
                    feature_vinculada = linked_features[0]
                    feature_data = features_del_plan.get(feature_vinculada)
                    
                    is_active = (feature_data is True) or (isinstance(feature_data, dict) and feature_data.get('value') is True)
                    
                    if not is_active:
                        limites_a_borrar.append(limite_key)
            
            for k in limites_a_borrar:
                del limites_del_plan[k]

    for addon_key, addon_info in addons.items():
        extensiones = addon_info.get('usageLimitsExtensions', {})
        if not extensiones:
            continue
        
        limite_key = list(extensiones.keys())[0]

        info_limite = limites_uso.get(limite_key, {})
        linked_features = info_limite.get('linkedFeatures', [])
        
        if not linked_features:
            continue
            
        feature_vinculada = linked_features[0]

        planes_originales = addon_info.get('availableFor', [])
        planes_compatibles = []
        
        for nombre_plan in planes_originales:
            info_plan = planes.get(nombre_plan, {})
            features_del_plan = info_plan.get('features', {})
            
            feature_data = features_del_plan.get(feature_vinculada)
            is_active = (feature_data is True) or (isinstance(feature_data, dict) and feature_data.get('value') is True)
            
            if is_active:
                planes_compatibles.append(nombre_plan)
                
        addon_info['availableFor'] = planes_compatibles

    return jsonify(pricing_data)

@contratos.route('/update/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def updateContratoUsuario(id_usuario):
    data = request.get_json()
    nombre_plan = data.get('newPlan')
    space_client = current_app.space_client

    try:
        contrato_actual = getContratoUsuario(id_usuario)
        if not contrato_actual:
            return jsonify({"error": "No se encontró el contrato del usuario"}), 404
    except Exception as e:
        print(f"Error al obtener contrato actual: {e}")
        return jsonify({"error": "No se pudo obtener el contrato actual"}), 404

    todas_las_suscripciones_addons = contrato_actual.get('subscriptionAddOns', {})
    addons_del_servicio = todas_las_suscripciones_addons.get("PetClinic", {})

    try:
        pricing_data = current_app.run_async(space_client.service_context.get_pricing("PetClinic", "1.0.3"))
    except Exception as e:
        print(f"Error al obtener el pricing: {e}")
        return jsonify({"error": "No se pudo obtener el catálogo de precios"}), 500

    planes = pricing_data.get('plans', {})
    limites_uso = pricing_data.get('usageLimits', {})
    catalogo_addons = pricing_data.get('addOns', {})

    info_nuevo_plan = planes.get(nombre_plan, {})
    features_nuevo_plan = info_nuevo_plan.get('features', {})

    addons_compatibles = {}

    for addon_key, addon_data in addons_del_servicio.items():
        info_addon = catalogo_addons.get(addon_key)
        
        if not info_addon:
            continue

        es_compatible = True
        extensiones = info_addon.get('usageLimitsExtensions', {})
        
        if extensiones:
            limite_key = list(extensiones.keys())[0]
            info_limite = limites_uso.get(limite_key, {})
            linked_features = info_limite.get('linkedFeatures', [])
            
            if linked_features:
                feature_vinculada = linked_features[0]
                
                feature_config = features_nuevo_plan.get(feature_vinculada, {})
                if isinstance(feature_config, dict):
                    esta_activa = feature_config.get('value', False)
                else:
                    esta_activa = bool(feature_config)
                    
                if not esta_activa:
                    es_compatible = False

        if es_compatible:
            addons_compatibles[addon_key] = addon_data

    todas_las_suscripciones_addons["PetClinic"] = addons_compatibles

    dato_contrato = {
        "contractedServices": {
            "PetClinic": "1.0.3"
        },
        "subscriptionPlans": {
            "PetClinic": nombre_plan
        },
        "subscriptionAddOns": todas_las_suscripciones_addons
    }
    
    print("Datos del contrato a guardar:", dato_contrato)

    try:
        contrato = current_app.run_async(space_client.contracts.update_contract_subscription(str(id_usuario), dato_contrato))
        print(f"Contrato actualizado exitosamente para propietario {id_usuario}")
        
        clinica = Clinica.query.filter_by(propietario_id=id_usuario).first()
        
        if clinica:
            clientes = Prop_mascota.query.filter_by(clinica_id=clinica.id).all()
            veterinarios = Veterinario.query.filter_by(clinica_id=clinica.id).all()
            
            usuarios_asociados = clientes + veterinarios
            
            for usuario_asoc in usuarios_asociados:
                if usuario_asoc.id != id_usuario:
                    try:
                        current_app.run_async(
                            space_client.contracts.update_contract_subscription(str(usuario_asoc.id), dato_contrato)
                        )
                    except Exception as e:
                        print(f"Error replicando nuevo plan para usuario asoc. {usuario_asoc.id}: {e}")

        return jsonify(contrato), 200
        
    except Exception as e:
        print(f"Error al editar contrato: {e}")
        if hasattr(e, 'status') and e.status == 404:
            return jsonify({"error": "Contrato no encontrado"}), 404
        return jsonify({"error": str(e)}), 500


@contratos.route('/generate-token/<int:id_usuario>', methods=['POST'])
@jwt_required()
def generate_user_pricing_token(id_usuario):
    
    usuario_loggeado_id = int(get_jwt_identity())
 
    if usuario_loggeado_id != id_usuario:
        return jsonify({'message': 'No tienes permiso para generar un token para este usuario'}), 403

    space_client = current_app.space_client
    try:
        token = current_app.run_async(space_client.featureEvaluators.generate_user_pricing_token(str(id_usuario)))
        
        if not token:
            print(f"⚠️ ERROR CRÍTICO: El SDK de Space devolvió None para el usuario {id_usuario}.")
            return jsonify({"error": "El servidor de Space falló al generar el token. Revisa los logs de Space"}), 500

        print(f"Token generado exitosamente para usuario ID: {id_usuario}")
        return jsonify({"token": token}), 200
        
    except Exception as e:
        print(f"Error al generar token: {e}")
        return jsonify({"error": str(e)}), 500


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
    id_usuario_jwt = int(get_jwt_identity())
    usuario = Usuario.query.get(id_usuario_jwt)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    contrato_actual = getContratoUsuario(usuario.id)
    
    data = request.get_json()
    addon_key = data.get('addons')

    space_client = current_app.space_client

    servicios_contratados = contrato_actual.get('contractedServices', {})
    service_name = "PetClinic"
    service_version = servicios_contratados.get(service_name, "1.0.3")

    try:
        pricing_data = current_app.run_async(
            space_client.service_context.get_pricing(service_name, service_version)
        )
    except Exception as e:
        print(f"Error al obtener el pricing: {e}")
        return jsonify({"error": "No se pudo obtener el catálogo de addons"}), 500

    feature_name = None
    catalogo_addons = pricing_data.get('addOns', {}) 
    
    if addon_key in catalogo_addons:
        addon_info = catalogo_addons[addon_key]
        extensiones = addon_info.get('usageLimitsExtensions', {})
        if extensiones:
            feature_name = list(extensiones.keys())[0]

    if not feature_name:
        return jsonify({"error": f"El addon '{addon_key}' no está mapeado a ninguna feature en el catálogo actual"}), 400

    plan_actual = contrato_actual.get('subscriptionPlans', {}).get(service_name, 'GOLD')
    
    todas_las_suscripciones_addons = contrato_actual.get('subscriptionAddOns', {})
    addons_del_servicio = todas_las_suscripciones_addons.get(service_name, {})
    
    valor_previo = addons_del_servicio.get(addon_key, 0)
    if isinstance(valor_previo, dict):
        cantidad_actual = valor_previo.get('quantity', 0)
    else:
        cantidad_actual = valor_previo
        
    nueva_cantidad = cantidad_actual + 1
    
    addons_del_servicio[addon_key] = nueva_cantidad
    todas_las_suscripciones_addons[service_name] = addons_del_servicio

    dato_contrato = {
        "contractedServices": {service_name: service_version},
        "subscriptionPlans": {service_name: plan_actual},
        "subscriptionAddOns": todas_las_suscripciones_addons
    }
    
    try:
        contrato_actualizado = current_app.run_async(
            space_client.contracts.update_contract_subscription(str(id_usuario_jwt), dato_contrato)
        )
        
        clinica = Clinica.query.filter_by(propietario_id=id_usuario_jwt).first()
        
        if clinica:
            clientes = Prop_mascota.query.filter_by(clinica_id=clinica.id).all()
            veterinarios = Veterinario.query.filter_by(clinica_id=clinica.id).all()
            
            usuarios_asociados = clientes + veterinarios
            
            for usuario_asoc in usuarios_asociados:
                try:
                    current_app.run_async(
                        space_client.contracts.update_contract_subscription(str(usuario_asoc.id), dato_contrato)
                    )
                except Exception as e:
                    print(f"Error replicando contrato para usuario asoc. {usuario_asoc.id}: {e}")

        print(f"Éxito: Addon {addon_key} subió a {nueva_cantidad} para propietario {id_usuario_jwt} y sus clientes.")
        return jsonify(contrato_actualizado), 200
        
    except Exception as e:
        print(f"Error crítico en el proceso de suscripción: {e}")
        return jsonify({"error": str(e)}), 500