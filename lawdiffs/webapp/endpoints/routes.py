import logging
from flask import (Blueprint, request)

from ...data import jsonify
from ...data.access import laws as data_laws
from ...mine import repos

logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'private_endpoints', __name__, template_folder='templates')


@blueprint.route('/laws/<law_code>/toc')
def fetch_toc(law_code):
    serialized = {}
    if law_code == 'ors':
        serialized['volumes'] = []
        volumes = data_laws.fetch_volumes(law_code)
        for v in volumes:
            chapters = v.fetch_chapters()
            d = v.serialize()
            d['chapters'] = [c.serialize() for c in chapters]
            serialized['volumes'].append(d)

    if not serialized:
        raise Exception('No TOC serialized for code' + str(law_code))
    return jsonify(serialized)


# @blueprint.route('/laws/<law_code>')
# def fetch_laws(law_code):
#     laws = data_laws.fetch_by_code(law_code)
#     return jsonify(laws)


@blueprint.route('/law/<law_code>/<version>/<subsection>')
def fetch_law(law_code, version, subsection):
    law = data_laws.fetch_law(law_code=law_code, subsection=subsection)
    prev, next = data_laws.fetch_previous_and_next_subsections(
        law_code, subsection)
    d = {
        'title': law.title(version),
        'text': law.text(version, formatted=True),
        'versions': law.versions,
        'prev': prev,
        'next': next
    }
    return jsonify(d)


@blueprint.route('/versions/<law_code>/<subsection>')
def fetch_versions(law_code, subsection):
    law = data_laws.fetch_law(law_code=law_code, subsection=subsection)
    d = {
        'versions': law.versions
    }
    return jsonify(d)


@blueprint.route('/diff/<law_code>/<subsection>/<version1>/<version2>')
def fetch_diff(law_code, subsection, version1, version2):
    law = data_laws.fetch_law(law_code=law_code, subsection=subsection)
    diff = repos.get_tag_diff(law, version1, version2)
    prev, next = data_laws.fetch_previous_and_next_subsections(
        law_code, subsection)
    return jsonify({
        'diff': diff,
        'version2_title': law.title(version2),
        'lines': diff.splitlines(),
        'prev': prev,
        'next': next,
        'versions': law.versions
    })
