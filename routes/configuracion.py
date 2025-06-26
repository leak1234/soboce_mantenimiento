from flask import Blueprint, render_template
from auth import login_requerido

configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/configuracion')

@configuracion_bp.route('/')
@login_requerido
def configuracion():
    return render_template('configuracion.html')
