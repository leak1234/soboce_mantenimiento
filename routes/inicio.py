from flask import Blueprint, render_template
from db import get_db_connection
from auth import login_requerido

inicio_bp = Blueprint('inicio', __name__)

@inicio_bp.route('/')
@login_requerido
def inicio():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Maquinaria;")
        total_equipos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Mantenimiento WHERE estado = 'Pendiente';")
        mant_pendientes = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Mantenimiento WHERE estado = 'Completado';")
        mant_completados = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Usuario;")
        total_usuarios = cur.fetchone()[0]

        cur.execute("SELECT estado, COUNT(*) FROM Mantenimiento GROUP BY estado;")
        mant_por_estado = cur.fetchall()

        cur.execute("SELECT rol, COUNT(*) FROM Usuario GROUP BY rol;")
        usuarios_por_rol = cur.fetchall()

    conn.close()
    return render_template('inicio.html',
                           total_equipos=total_equipos,
                           mant_pendientes=mant_pendientes,
                           mant_completados=mant_completados,
                           total_usuarios=total_usuarios,
                           mant_por_estado=mant_por_estado,
                           usuarios_por_rol=usuarios_por_rol)
