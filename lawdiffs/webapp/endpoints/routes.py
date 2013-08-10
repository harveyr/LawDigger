import logging
from flask import (Blueprint, request)

from ...data import jsonify
from ...data.access import laws as da_laws
from ...mine import repos

logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'private_endpoints', __name__, template_folder='templates')


@blueprint.route('/laws/<law_code>/toc')
def fetch_toc(law_code):
    serialized = {}
    if law_code == 'ors':
        serialized['volumes'] = []
        volumes = da_laws.fetch_volumes(law_code)
        for v in volumes:
            chapters = v.fetch_chapters()
            d = v.serialize()
            d['chapters'] = [c.serialize() for c in chapters]
            serialized['volumes'].append(d)

            if not 'versions' in serialized:
                serialized['versions'] = chapters[0].title_versions()

    if not serialized:
        raise Exception('No TOC serialized for code' + str(law_code))
    return jsonify(serialized)


@blueprint.route('/laws/<law_code>/division/<division>')
def fetch_division(law_code, division):
    data = {}
    if law_code == 'ors':
        chapter, statutes = da_laws.fetch_ors_by_chapter(division)
        data['chapter'] = chapter
        data['statutes'] = statutes
    if not data:
        raise Exception('No data found for code' + str(law_code))
    return jsonify(data)


# @blueprint.route('/laws/<law_code>')
# def fetch_laws(law_code):
#     laws = da_laws.fetch_by_code(law_code)
#     return jsonify(laws)


@blueprint.route('/law/<law_code>/<version>/<subsection>')
def fetch_law(law_code, version, subsection):
    logger.setLevel(logging.DEBUG)

    law = da_laws.fetch_law(law_code=law_code, subsection=subsection)
    prev, next = da_laws.fetch_previous_and_next_subsections(
        law_code, subsection)
    source = law.fetch_source(version)
    logger.debug('source: {v}'.format(v=source))

    d = {
        'title': law.title(version),
        'text': law.text(version, formatted=True),
        'versions': law.versions,
        'source': source,
        'prev': prev,
        'next': next
    }
    return jsonify(d)


@blueprint.route('/versions/<law_code>/<subsection>')
def fetch_versions(law_code, subsection):
    law = da_laws.fetch_law(law_code=law_code, subsection=subsection)
    d = {
        'versions': law.versions
    }
    return jsonify(d)


@blueprint.route('/diff/<law_code>/<subsection>/<version1>/<version2>')
def fetch_diff(law_code, subsection, version1, version2):
    law = da_laws.fetch_law(law_code=law_code, subsection=subsection)
    diff = repos.get_tag_diff(law, version1, version2)
    prev, next = da_laws.fetch_previous_and_next_subsections(
        law_code, subsection)
    return jsonify({
        'diff': diff,
        'version2_title': law.title(version2),
        'lines': diff.splitlines(),
        'prev': prev,
        'next': next,
        'versions': law.versions
    })
