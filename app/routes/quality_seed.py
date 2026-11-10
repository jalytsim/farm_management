# app/routes/quality_seed.py
# =============================================================================
#  Paramètres de qualité, grades et règles de classement « standards » pour
#  les marchandises de Nkusu / 2tume, d'après les normes officielles :
#    · Café Robusta et Arabica : UCDA (EAS 130), normes nationales ougandaises
#    · Cacao                  : ISO 2451
#    · Soja                   : EAS 762:2011
#
#  Usage (local d'abord, puis production) :
#      flask quality seed --dry-run     # montre ce qui serait créé, n'écrit rien
#      flask quality seed               # crée ce qui manque
#
#  · Ne crée QUE ce qui manque : un paramètre, un grade ou une règle qui existe
#    déjà (même nom, même marchandise) n'est ni modifié ni dupliqué.
#  · Tout reste modifiable ensuite dans le Quality Manager.
#  · Les limites de chaque PARAMÈTRE (min / max) sont les limites d'acceptation :
#    au-delà, la livraison est refusée. Ce sont celles du grade le plus bas.
# =============================================================================

from decimal import Decimal

import click
from flask import Blueprint

from app import db
from app.models import Crop, QualityParameter, Grade, GradeRule

bp = Blueprint('quality_seed', __name__, cli_group='quality')

D = lambda v: None if v is None else Decimal(str(v))  # noqa: E731

# ── Référentiel ──────────────────────────────────────────────────────────────
#  parameters : (nom, unité, min accepté, max accepté, obligatoire)
#  grades     : (grade, description, [(paramètre, opérateur, min, max), ...])
#               dans l'ordre, du meilleur au moins bon (sort_order 1, 2, 3…)
STANDARDS = {
    'Coffee Robusta': {
        'source': 'UCDA national standards (EAS 130): moisture 12.5 %, extraneous matter 2 %',
        'parameters': [
            ('Moisture',                         '%', None, 12.5, True),
            ('Total defects',                    '%', None, 15,   True),
            ('Foreign matter',                   '%', None, 2,    True),
            ('Retained on screen 18',            '%', 0,    100,  True),
            ('Retained on screen 15 and above',  '%', 0,    100,  True),
            ('Retained on screen 12 and above',  '%', 0,    100,  True),
            ('Black beans',                      '%', None, None, False),
        ],
        'grades': [
            ('Screen 18', 'UCDA: 92 % retained on screen 18, total defects 7 %', [
                ('Retained on screen 18', 'gte', 92, None),
                ('Total defects', 'lte', None, 7)]),
            ('Screen 15', 'UCDA: 90 % retained on screen 15, total defects 12 %', [
                ('Retained on screen 15 and above', 'gte', 90, None),
                ('Total defects', 'lte', None, 12)]),
            ('Screen 12', 'UCDA: 85 % retained on screen 12, total defects 15 %', [
                ('Retained on screen 12 and above', 'gte', 85, None),
                ('Total defects', 'lte', None, 15)]),
        ],
    },
    'Coffee Arabica': {
        'source': 'UCDA national standards (EAS 130): moisture 12 %',
        'parameters': [
            ('Moisture',                         '%',   None, 12,   True),
            ('Total defects',                    '%',   None, 10,   True),
            ('Retained on screen 17',            '%',   0,    100,  True),
            ('Retained on screen 16 and above',  '%',   0,    100,  True),
            ('Retained on screen 15 and above',  '%',   0,    100,  True),
            ('Cup score (SCA)',                  '/100', 0,   100,  False),
        ],
        'grades': [
            ('AA', 'UCDA: 90 % retained on screen 17, total defects 5 %', [
                ('Retained on screen 17', 'gte', 90, None),
                ('Total defects', 'lte', None, 5)]),
            ('A', 'UCDA: 90 % retained on screen 16, total defects 7 %', [
                ('Retained on screen 16 and above', 'gte', 90, None),
                ('Total defects', 'lte', None, 7)]),
            ('B', 'UCDA: 90 % retained on screen 15, total defects 10 %', [
                ('Retained on screen 15 and above', 'gte', 90, None),
                ('Total defects', 'lte', None, 10)]),
        ],
    },
    'Cocoa': {
        'source': 'ISO 2451: moisture 7.5 %, cut test on beans',
        'parameters': [
            ('Moisture',                           '%',             None, 7.5, True),
            ('Mouldy beans',                       '%',             None, 4,   True),
            ('Slaty beans',                        '%',             None, 8,   True),
            ('Insect damaged, germinated or flat', '%',             None, 6,   True),
            ('Bean count',                         'beans / 100 g', None, None, False),
        ],
        'grades': [
            ('Grade I', 'ISO 2451: mouldy 3 %, slaty 3 %, insect damaged / germinated / flat 3 %', [
                ('Mouldy beans', 'lte', None, 3),
                ('Slaty beans', 'lte', None, 3),
                ('Insect damaged, germinated or flat', 'lte', None, 3)]),
            ('Grade II', 'ISO 2451: mouldy 4 %, slaty 8 %, insect damaged / germinated / flat 6 %', [
                ('Mouldy beans', 'lte', None, 4),
                ('Slaty beans', 'lte', None, 8),
                ('Insect damaged, germinated or flat', 'lte', None, 6)]),
        ],
    },
    'Soya Bean': {
        'source': 'EAS 762:2011 Dry soybeans: moisture 13 %, aflatoxin 10 ppb',
        'parameters': [
            ('Moisture',              '%',   None, 13,  True),
            ('Foreign matter',        '%',   None, 3,   True),
            ('Broken / split grains', '%',   None, 5,   True),
            ('Pest damaged grains',   '%',   None, 1.5, True),
            ('Total defects',         '%',   None, 5,   True),
            ('Total aflatoxin',       'ppb', None, 10,  False),
        ],
        'grades': [
            ('Grade 1', 'EAS 762', [
                ('Foreign matter', 'lte', None, 1),
                ('Broken / split grains', 'lte', None, 1),
                ('Pest damaged grains', 'lte', None, 0.3),
                ('Total defects', 'lte', None, 2)]),
            ('Grade 2', 'EAS 762', [
                ('Foreign matter', 'lte', None, 2),
                ('Broken / split grains', 'lte', None, 2.5),
                ('Pest damaged grains', 'lte', None, 0.8),
                ('Total defects', 'lte', None, 3)]),
            ('Grade 3', 'EAS 762', [
                ('Foreign matter', 'lte', None, 3),
                ('Broken / split grains', 'lte', None, 5),
                ('Pest damaged grains', 'lte', None, 1.5),
                ('Total defects', 'lte', None, 5)]),
        ],
    },
}


def _find_crop(name):
    return Crop.query.filter(db.func.lower(Crop.name) == name.lower()).first()


def seed_quality(dry_run=False):
    """Crée les paramètres, grades et règles manquants. Retourne un rapport."""
    report = {'parameters': 0, 'grades': 0, 'rules': 0, 'missing_crops': []}

    for crop_name, spec in STANDARDS.items():
        crop = _find_crop(crop_name)
        if not crop:
            report['missing_crops'].append(crop_name)
            continue
        click.echo(f"\n== {crop.name} (id {crop.id}) — {spec['source']}")

        # 1. Paramètres
        params = {}
        for position, (name, unit, lo, hi, required) in enumerate(spec['parameters'], start=1):
            param = QualityParameter.query.filter_by(crop_id=crop.id, variety_id=None, name=name).first()
            if param:
                click.echo(f"   = parameter '{name}' already exists, kept as is")
            else:
                param = QualityParameter(
                    crop_id=crop.id, variety_id=None, name=name, unit=unit,
                    value_type='number', options=[], min_value=D(lo), max_value=D(hi),
                    is_required=required, is_active=True, position=position,
                )
                db.session.add(param)
                report['parameters'] += 1
                click.echo(f"   + parameter '{name}' ({unit}) accepted "
                           f"{'≥ ' + str(lo) if lo is not None else ''}"
                           f"{' ≤ ' + str(hi) if hi is not None else ''}")
            params[name] = param
        db.session.flush()

        # 2. Grades et 3. règles
        for sort_order, (grade_value, description, rules) in enumerate(spec['grades'], start=1):
            grade = Grade.query.filter_by(crop_id=crop.id, variety_id=None, grade_value=grade_value).first()
            if grade:
                click.echo(f"   = grade '{grade_value}' already exists, kept as is")
            else:
                grade = Grade(crop_id=crop.id, variety_id=None, grade_value=grade_value,
                              description=description, sort_order=sort_order)
                db.session.add(grade)
                db.session.flush()
                report['grades'] += 1
                click.echo(f"   + grade '{grade_value}' (order {sort_order})")

            for param_name, operator, lo, hi in rules:
                param = params[param_name]
                exists = GradeRule.query.filter_by(grade_id=grade.id, parameter_id=param.id).first()
                if exists:
                    continue
                db.session.add(GradeRule(grade_id=grade.id, parameter_id=param.id,
                                         operator=operator, min_value=D(lo), max_value=D(hi)))
                report['rules'] += 1
                click.echo(f"     + rule {param_name} {operator} {lo if lo is not None else hi}")

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()
    return report


@bp.cli.command('seed')
@click.option('--dry-run', is_flag=True, help="Show what would be created without writing anything.")
def seed_command(dry_run):
    """flask quality seed — standard quality parameters, grades and rules."""
    report = seed_quality(dry_run=dry_run)
    click.echo(f"\n{'[DRY RUN] would create' if dry_run else 'Created'}: "
               f"{report['parameters']} parameters, {report['grades']} grades, {report['rules']} rules.")
    if report['missing_crops']:
        click.echo(f"Commodities not found in the crop table (skipped): {', '.join(report['missing_crops'])}")