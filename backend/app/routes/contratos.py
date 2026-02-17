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