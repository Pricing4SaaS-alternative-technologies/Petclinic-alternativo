from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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
    try:
        plans = current_app.run_async(space_client.service_context.get_pricing(name, version))
    except Exception as e:
        if(e.status == 404):
            contract = ''
        else:
            raise
    return plans