from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth import login_requerido, roles_requeridos
from db import get_db_connection

frecuencias_bp = Blueprint('frecuencias', __name__, url_prefix='/frecuencias')

@frecuencias_bp.route('/')
@login_requerido
@roles_requeridos('admin', 'supervisor')
def lista_frecuencias():
    descripcion = request.args.get('descripcion', '').strip().lower()
    tipo = request.args.get('tipo', '').strip().lower()

    conn = get_db_connection()
    with conn.cursor() as cur:
        query = """
            SELECT frecuencia_id, descripcion, tipo, valor
            FROM FrecuenciaMantenimiento
            WHERE 1=1
        """
        params = []

        if descripcion:
            query += " AND LOWER(descripcion) LIKE %s"
            params.append(f"%{descripcion}%")
        if tipo:
            query += " AND LOWER(tipo) = %s"
            params.append(tipo)

        query += " ORDER BY frecuencia_id"
        cur.execute(query, params)
        frecuencias = cur.fetchall()
    conn.close()
    return render_template('frecuencias/index.html', frecuencias=frecuencias)


@frecuencias_bp.route('/crear', methods=['GET', 'POST'])
@login_requerido
def crear():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        valor = request.form['valor']

        if not descripcion or not tipo or not valor:
            flash('Completa todos los campos')
            return redirect(url_for('frecuencias.crear'))

        try:
            valor_int = int(valor)
        except ValueError:
            flash('El valor debe ser un número entero')
            return redirect(url_for('frecuencias.crear'))

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO FrecuenciaMantenimiento (descripcion, tipo, valor)
                VALUES (%s, %s, %s)
            """, (descripcion, tipo, valor_int))
            conn.commit()
        conn.close()
        flash('Frecuencia creada con éxito')
        return redirect(url_for('frecuencias.lista_frecuencias'))

    return render_template('frecuencias/crear.html')

@frecuencias_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM FrecuenciaMantenimiento WHERE frecuencia_id = %s", (id,))
        frecuencia = cur.fetchone()

    if not frecuencia:
        flash('Frecuencia no encontrada')
        return redirect(url_for('frecuencias.lista_frecuencias'))

    if request.method == 'POST':
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        valor = request.form['valor']

        if not descripcion or not tipo or not valor:
            flash('Completa todos los campos')
            return redirect(url_for('frecuencias.editar', id=id))

        try:
            valor_int = int(valor)
        except ValueError:
            flash('El valor debe ser un número entero')
            return redirect(url_for('frecuencias.editar', id=id))

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE FrecuenciaMantenimiento
                SET descripcion = %s, tipo = %s, valor = %s
                WHERE frecuencia_id = %s
            """, (descripcion, tipo, valor_int, id))
            conn.commit()
        conn.close()
        flash('Frecuencia actualizada con éxito')
        return redirect(url_for('frecuencias.lista_frecuencias'))

    conn.close()
    return render_template('frecuencias/editar.html', frecuencia=frecuencia)

@frecuencias_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM FrecuenciaMantenimiento WHERE frecuencia_id = %s", (id,))
        conn.commit()
    conn.close()
    flash('Frecuencia eliminada con éxito')
    return redirect(url_for('frecuencias.lista_frecuencias'))
