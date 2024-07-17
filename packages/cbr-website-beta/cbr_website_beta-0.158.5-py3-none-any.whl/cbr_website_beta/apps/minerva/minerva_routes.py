from flask import render_template
from cbr_website_beta.apps.minerva import blueprint
from cbr_website_beta.cbr__flask.decorators import allow_annonymous
from cbr_website_beta.cbr__flask.decorators.allow_annonymous import allow_anonymous
EXPECTED_ROUTES__MINERVA = [ '/minerva']


@blueprint.route('')
@allow_anonymous
def minerva_root():
    return render_template('minerva/index.html')

