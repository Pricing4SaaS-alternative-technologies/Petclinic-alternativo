from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models import Usuario, Prop_mascota, Veterinario, Prop_clinica
from app.models.enums import TipoUsuarioEnum, EspecialidadEnum

contratos = Blueprint('contratos', __name__, url_prefix='/api/contratos')

@contratos.route('/getContract/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def getContratoUsuario(user_id):
    space_client = current_app.space_client
    service = current_app.run_async(space_client.contracts.get_user_id_contract(user_id))
    return service
