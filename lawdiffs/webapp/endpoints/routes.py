import logging
from flask import (Blueprint, request)

from ...data import jsonify
from ...data.access import laws as data_laws

logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'private_endpoints', __name__, template_folder='templates')


@blueprint.route('/laws/<state_code>')
def index_route(state_code):
    laws = data_laws.fetch_laws_by_state_code(state_code)
    return jsonify(laws)
