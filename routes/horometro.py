from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
from auth import login_requerido

horometro_bp = Blueprint('horometro', __name__)

@horometro_bp.route('/horometro/<int:maquinaria_id>', methods=['GET', 'POST'])
@login_requerido
def registrar_horometro(maquinaria_id):
    conn = get_db_connection()

    if request.method == 'POST':
        fecha = request.form['fecha']
        horas = request.form['horas']

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Horometro (maquinaria_id, fecha_registro, horas_acumuladas)
                VALUES (%s, %s, %s)
            """, (maquinaria_id, fecha, horas))
            flash("Registro de horómetro guardado correctamente.", "success")
        conn.commit()
        return redirect(url_for('equipos.detalle_equipo', id=maquinaria_id))

    # Obtener historial de horómetros
    with conn.cursor() as cur:
        cur.execute("""
            SELECT fecha_registro, horas_acumuladas
            FROM Horometro
            WHERE maquinaria_id = %s
            ORDER BY fecha_registro DESC
        """, (maquinaria_id,))
        registros = cur.fetchall()
    conn.close()

    return render_template('horometro/registro.html', registros=registros, maquinaria_id=maquinaria_id)
