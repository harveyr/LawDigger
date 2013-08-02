import logging
from flask import (Blueprint, request)

from ...data import jsonify, htmlify
from ...data.access import laws as data_laws

logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'private_endpoints', __name__, template_folder='templates')


@blueprint.route('/laws/<state_code>')
def fetch_laws(state_code):
    laws = data_laws.fetch_by_state(state_code)
    return jsonify(laws)


@blueprint.route('/law/<state_code>/<law_id>/<version>')
def fetch_law(state_code, law_id, version):
    law = data_laws.fetch_law(state_code=state_code, id_=law_id)
    data = law.serialize()
    data['html'] = law.get_version_html(version)
    return jsonify(data)
