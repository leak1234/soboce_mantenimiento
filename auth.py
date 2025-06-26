from flask import session, redirect, url_for, flash, request, render_template
from functools import wraps
from db import get_db_connection
from flask import Blueprint
import requests

auth_bp = Blueprint('auth', __name__)

# Decorador para verificar login
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión primero.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorada

# Decorador para roles específicos
def roles_requeridos(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            rol_actual = session.get('rol')
            if rol_actual not in roles_permitidos:
                flash('No tienes permiso para acceder a esta sección.', 'error')
                return redirect(url_for('inicio.inicio'))
            return f(*args, **kwargs)
        return funcion_decorada
    return decorador

# Ruta de login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contraseña']
        captcha_token = request.form.get('g-recaptcha-response')

        # Validar CAPTCHA
        secret_key = '6LcktW4rAAAAAC0ceEqPdzb0ijANGQSHH2CpRo90'
        captcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': secret_key,
            'response': captcha_token
        }
        captcha_respuesta = requests.post(captcha_url, data=payload)
        resultado = captcha_respuesta.json()

        if not resultado.get('success'):
            flash('⚠️ Verificación CAPTCHA fallida. Inténtalo de nuevo.', 'danger')
            return redirect(url_for('auth.login'))

        # Validar usuario
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT usuario_id, nombre, contraseña, rol FROM Usuario WHERE correo = %s", (correo,))
            usuario = cur.fetchone()
        conn.close()

        if usuario and usuario[2] == contrasena:
            session['usuario_id'] = usuario[0]
            session['usuario'] = usuario[1]
            session['rol'] = usuario[3]
            flash('✅ Has iniciado sesión exitosamente.', 'success')
            return redirect(url_for('inicio.inicio'))
        else:
            flash('❌ Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')

# Ruta de logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))
