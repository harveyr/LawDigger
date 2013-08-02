import logging
from flask import (Blueprint, request)

from ...data import models, jsonify

logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'private_endpoints', __name__, template_folder='templates')


@blueprint.route('/laws/<state_code>')
def index_route(state_code):
    logger.debug('state_code: {v}'.format(v=state_code))
    laws = models.Law.fetch_by_state_code(state_code)
    return jsonify(laws)
