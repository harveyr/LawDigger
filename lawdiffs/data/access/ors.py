import logging

from . import laws as da_laws
from .. import law_codes
from .. import models

logger = logging.getLogger(__name__)

law_code = law_codes.OREGON_REVISED_STATUTES


def get_or_create_volume(version, volume_str):
    obj = da_laws.get_or_create_division(
        law_code=law_code, version=version, division=volume_str)
    if obj.leaf is not False:
        obj.leaf = False
        obj.save()

    return obj


def get_or_create_chapter(volume, chapter_str):
    if not isinstance(volume, models.LawDivision):
        raise Exception('I want LawDivision. I got {}'.format(volume))

    obj = da_laws.get_or_create_division(
        parent_id=volume.id, law_code=volume.law_code,
        version=volume.version, division=chapter_str)
    if obj.leaf is not True:
        obj.leaf = True
        obj.save()

    return obj


def create_statute(chapter, subsection, title, text):
    law = da_laws.create_law_in_division(
        division=chapter,
        subsection=subsection,
        title=title,
        text=text)
    logger.info('Created ORS: {}'.format(law))
    return law


def get_toc_map():
    volumes = {
        '1': {
            'title': 'Courts of Record; Court Officers; Juries',
            'chapters': [1, 10]
        },
        '2': {
            'title': 'Procedure in Civil Proceedings',
            'chapters': [12, 25]
        },
        '3': {
            'title': 'Remedies and Special Actions and Proceedings',
            'chapters': [28, 36]
        },
        '4': {
            'title': 'Evidence and Witnesses',
            'chapters': [40, 45]
        },
        '5': {
            'title': 'Small Claims Department of Circuit Court',
            'chapters': [46, 46]
        },
        '6': {
            'title': 'Justice Courts',
            'chapters': [51, 55]
        },
        '7': {
            'title': 'Corporations and Partnerships',
            'chapters': [56, 70]
        },
        '8': {
            'title': 'Commercial Transactions',
            'chapters': [71, 84]
        },
        '9': {
            'title': 'Mortgages and Liens',
            'chapters': [86, 88]
        },
        '10': {
            'title': 'Property Rights and Transactions',
            'chapters': [90, 105]
        },
        '11': {
            'title': 'Domestic Relations',
            'chapters': [106, 110]
        },
        '12': {
            'title': 'Probate Law',
            'chapters': [111, 118]
        },
        '13': {
            'title': 'Protective Proceedings; Powers of Attorney; Trusts',
            'chapters': [124, 130]
        },
        '14': {
            'title': 'Procedure in Criminal Matters Generally',
            'chapters': [131, 153]
        },
        '15': {
            'title': 'Procedure in Criminal Actions in Justice Courts',
            'chapters': [156, 157]
        },
        '16': {
            'title': 'Crimes and Punishments',
            'chapters': [161, 169]
        },
        '17': {
            'title': 'State Legislative Department and Laws',
            'chapters': [171, 174]
        },
        '18': {
            'title': 'Executive Branch; Organization',
            'chapters': [176, 185]
        },
        '19': {
            'title': 'Miscellaneous Matters Related to Government and Public Affairs',
            'chapters': [186, 200]
        },
        '20': {
            'title': 'Counties and County Officers',
            'chapters': [201, 215]
        },
        '21': {
            'title': 'Cities',
            'chapters': [221, 227]
        },
        '22': {
            'title': 'Public Officers and Employees',
            'chapters': [236, 244]
        },
        '23': {
            'title': 'Elections',
            'chapters': [246, 260]
        },
        '24': {
            'title': 'Public Organizations for Community Service',
            'chapters': [261, 268]
        },
        '25': {
            'title': 'Public Lands',
            'chapters': [270, 275]
        },
        '26': {
            'title': 'Public Facilities, Contracting and Insurance',
            'chapters': [276, 283]
        },
        '26': {
            'title': 'Public Facilities, Contracting and Insurance',
            'chapters': [276, 283]
        },
        '26A': {
            'title': 'Economic Development',
            'chapters': [284, 285]
        },
        '27': {
            'title': 'Public Borrowing',
            'chapters': [286, 289]
        },
        '28': {
            'title': 'Public Financial Administration',
            'chapters': [291, 297]
        },
        '29': {
            'title': 'Revenue and Taxation',
            'chapters': [305, 324]
        },
        '30': {
            'title': 'Education and Culture',
            'chapters': [326, 359]
        },
        '31': {
            'title': 'Highways, Roads, Bridges and Ferries',
            'chapters': [366, 391]
        },
        '32': {
            'title': 'Military Affairs; Emergency Services',
            'chapters': [396, 404]
        },
        '33': {
            'title': 'Privileges and Benefits of Veterans and Service Personnel',
            'chapters': [406, 408]
        },
        '34': {
            'title': 'Human Services; Juvenile Code; Corrections',
            'chapters': [409, 423]
        },
        '35': {
            'title': 'Mental Health and Developmental Disabilities; Alcohol and Drug Treatment',
            'chapters': [426, 430]
        },
        '36': {
            'title': 'Public Health and Safety',
            'chapters': [431, 470]
        },
        '37': {
            'title': 'Alcoholic Liquors; Controlled Substances; Drugs',
            'chapters': [471, 475]
        },
        '38': {
            'title': 'Protection From Fire',
            'chapters': [476, 480]
        },
        '41': {
            'title': 'Wildlife',
            'chapters': [496, 501]
        },
        '42': {
            'title': 'Commercial Fishing and Fisheries',
            'chapters': [506, 513]
        },
        '43': {
            'title': 'Mineral Resources',
            'chapters': [516, 523]
        },
        '44': {
            'title': 'Forestry and Forest Products',
            'chapters': [526, 532]
        },
        '45': {
            'title': 'Water Resources: Irrigation, Drainage, Flood Control, Reclamation',
            'chapters': [536, 558]
        },
        '46': {
            'title': 'Agriculture',
            'chapters': [561, 571]
        },
        '47': {
            'title': 'Agricultural Marketing and Warehousing',
            'chapters': [576, 587]
        },
        '48': {
            'title': 'Animals',
            'chapters': [596, 610]
        },
        '49': {
            'title': 'Food and Other Commodities: Purity, Sanitation, Grades, Standards, Labels, Weights and Measures',
            'chapters': [616, 635]
        },
        '50': {
            'title': 'Trade Regulations and Practices',
            'chapters': [645, 650]
        },
        '51': {
            'title': 'Labor and Employment; Unlawful Discrimination',
            'chapters': [651, 663]
        },
        '52': {
            'title': 'Occupations and Professions',
            'chapters': [670, 704]
        },
        '52A': {
            'title': 'Insurance and Finance Administration',
            'chapters': [705, 705]
        },
        '53': {
            'title': 'Financial Institutions',
            'chapters': [706, 717]
        },
        '54': {
            'title': 'Credit Unions, Lending Institutions and Pawnbrokers',
            'chapters': [723, 726]
        },
        '56': {
            'title': 'Insurance',
            'chapters': [731, 752]
        },
        '57': {
            'title': 'Utility Regulation',
            'chapters': [756, 774]
        },
        '58': {
            'title': 'Shipping and Navigation',
            'chapters': [776, 783]
        },
        '59': {
            'title': 'Oregon Vehicle Code',
            'chapters': [801, 826]
        },
        '61': {
            'title': 'Small Watercraft',
            'chapters': [830, 830]
        },
        '62': {
            'title': 'Aviation',
            'chapters': [835, 838]
        }
    }

    titles = {
        1: {
            'title': 'COURTS, ORCP',
            'volumes': [1, 6]
        },
        2: {
            'title': 'BUSINESS ORGANIZATIONS, COMMERCIAL CODE',
            'volumes': [7, 9]
        },
        3: {
            'title': 'LANDLORD-TENANT, DOMESTIC RELATIONS, PROBATE',
            'volumes': [10, 13]
        },
        4: {
            'title': 'CRIMINAL PROCEDURE, CRIMES',
            'volumes': [14, 16]
        },
        5: {
            'title': 'STATE GOVERNMENT, GOVERNMENT PROCEDURES, LAND USE',
            'volumes': [17, 19]
        },
        6: {
            'title': 'LOCAL GOVERNMENT, PUBLIC EMPLOYEES, ELECTIONS',
            'volumes': [20, 23]
        },
        7: {
            'title': 'PUBLIC FACILITIES AND FINANCE',
            'volumes': [24, 28]
        },
        8: {
            'title': 'REVENUE AND TAXATION',
            'volumes': [29, 29]
        },
        9: {
            'title': 'EDUCATION AND CULTURE',
            'volumes': [30, 30]
        },
        10: {
            'title': 'HIGHWAYS, MILITARY, JUVENILE CODE, HUMAN SERVICES',
            'volumes': [31, 35]
        },
        11: {
            'title': 'PUBLIC HEALTH, HOUSING, ENVIRONMENT',
            'volumes': [36, 36]
        }
    }

    return {
        'titles': titles,
        'volumes': volumes
    }
