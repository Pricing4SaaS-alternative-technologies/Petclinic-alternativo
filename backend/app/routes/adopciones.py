from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.adopcion import Adopcion
from app.models.mascota import Mascota
from app.models.prop_mascota import Prop_mascota
from app.models.enums import EstadoAdopcion

bp = Blueprint('adopciones', __name__, url_prefix='/api/adopciones')

@bp.route('', methods=['GET'])
@jwt_required(optional=True)
def listar_todas():
    return jsonify([a.to_dict() for a in Adopcion.query.all()]), 200

@bp.route('/mine/creadas', methods=['GET'])
@jwt_required()
def listar_creadas():
    user = get_jwt_identity()
    return jsonify([a.to_dict()
      for a in Adopcion.query.filter_by(dueño_nuevo_id=user).all()
    ]), 200

@bp.route('/mine/pendientes', methods=['GET'])
@jwt_required()
def listar_pendientes():
    user = get_jwt_identity()
    propuestas = Adopcion.query.filter(
        Adopcion.dueño_anterior_id == user,
        Adopcion.estado_adopcion == EstadoAdopcion.PENDIENTE,
        Adopcion.dueño_nuevo_id.isnot(None)    # sólo propuestas reales
    ).all()
    return jsonify([a.to_dict() for a in propuestas]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def crear_adopcion():
    user = get_jwt_identity()
    data = request.get_json()
    m = Mascota.query.get_or_404(data['mascota_id'])
    if m.dueño_id == user:
        return jsonify({'msg':'No puedes proponer adopción de tu propia mascota'}),400
    ad = Adopcion(
      descripcion=data.get('descripcion',''),
      mascota_id=m.id,
      dueño_anterior_id=m.dueño_id,
      dueño_nuevo_id=None
    )
    db.session.add(ad); db.session.commit()
    return jsonify(ad.to_dict()), 201

@bp.route('/<int:aid>/aceptar', methods=['PUT'])
@jwt_required()
def aceptar(aid):
    user = get_jwt_identity()
    try:
        user = int(user)
    except (TypeError, ValueError):
        pass
    ad = Adopcion.query.get_or_404(aid)
    if ad.dueño_anterior_id!=user or ad.estado_adopcion!=EstadoAdopcion.PENDIENTE:
        return jsonify({'msg':'No autorizado'}),403
    ad.estado_adopcion = EstadoAdopcion.APROBADA
    ad.mascota.dueño_id = ad.dueño_nuevo_id
    db.session.commit()
    return jsonify(ad.to_dict()),200

@bp.route('/<int:aid>/rechazar', methods=['PUT'])
@jwt_required()
def rechazar(aid):
    user = get_jwt_identity()
    try:
        user = int(user)
    except (TypeError, ValueError):
        pass
    ad = Adopcion.query.get_or_404(aid)
    if ad.dueño_anterior_id!=user or ad.estado_adopcion!=EstadoAdopcion.PENDIENTE:
        return jsonify({'msg':'No autorizado'}),403
    ad.estado_adopcion = EstadoAdopcion.RECHAZADA
    nueva_ad = Adopcion(
        descripcion       = ad.descripcion,
        mascota_id        = ad.mascota_id,
        dueño_anterior_id = ad.dueño_anterior_id,
        dueño_nuevo_id    = None
    )
    db.session.add(nueva_ad)
    db.session.commit()
    return jsonify(nueva_ad.to_dict()), 200

@bp.route('/<int:aid>/solicitar', methods=['PUT'])
@jwt_required()
def solicitar(aid):
    user = get_jwt_identity()
    ad = Adopcion.query.get_or_404(aid)

    if ad.dueño_anterior_id == user:
        return jsonify({'msg':'No puedes solicitar tu propia adopción'}), 403
    if ad.estado_adopcion != EstadoAdopcion.CREADA:
        return jsonify({'msg':'Sólo adopciones en estado CREADA se pueden solicitar'}), 400

    ad.dueño_nuevo_id    = user
    ad.estado_adopcion   = EstadoAdopcion.PENDIENTE
    db.session.commit()
    return jsonify(ad.to_dict()), 200

@bp.route('/<int:aid>', methods=['DELETE'])
@jwt_required()
def eliminar_adopcion(aid):
    user = get_jwt_identity()
    try:
        user = int(user)
    except (TypeError, ValueError):
        pass
    
    ad = Adopcion.query.get_or_404(aid)
    if ad.dueño_anterior_id != user:
        return jsonify({'msg':'No autorizado'}), 403

    db.session.delete(ad)
    db.session.commit()
    return '', 204

@bp.route('/<int:aid>', methods=['PATCH'])
@jwt_required()
def editar_adopcion(aid):
    user = get_jwt_identity()
    try:
        user = int(user)
    except (TypeError, ValueError):
        pass

    ad = Adopcion.query.get_or_404(aid)
    if ad.dueño_anterior_id != user or ad.estado_adopcion != EstadoAdopcion.CREADA:
        return jsonify({'msg':'No autorizado'}), 403

    data = request.get_json() or {}
    desc = data.get('descripcion')
    if not desc:
        return jsonify({'msg':'Descripción requerida'}), 400

    ad.descripcion = desc.strip()
    db.session.commit()
    return jsonify(ad.to_dict()), 200