from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth import login_requerido
from db import get_db_connection
from datetime import date  # Asegúrate de importar date para obtener la fecha actual

mantenimientos_bp = Blueprint('mantenimientos', __name__)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_requerido
from db import get_db_connection

mantenimientos_bp = Blueprint('mantenimientos', __name__)
@mantenimientos_bp.route('/mantenimientos')
@login_requerido
def lista_mantenimientos():
    # Obtener filtros
    filtro_texto = request.args.get('filtro', '').strip().lower()
    tipo = request.args.get('tipo', '').strip()
    estado = request.args.get('estado', '').strip()
    inicio = request.args.get('inicio', '')
    fin = request.args.get('fin', '')

    conn = get_db_connection()
    with conn.cursor() as cur:
        condiciones = []
        valores = []

        if session.get('rol') != 'admin':
            condiciones.append("m.usuario_id_responsable = %s")
            valores.append(session['usuario_id'])

        if filtro_texto:
            condiciones.append("(LOWER(ma.nombre) LIKE %s OR LOWER(m.descripcion) LIKE %s)")
            valores.extend([f"%{filtro_texto}%", f"%{filtro_texto}%"])

        if tipo:
            condiciones.append("m.tipo = %s")
            valores.append(tipo)

        if estado:
            condiciones.append("m.estado = %s")
            valores.append(estado)

        if inicio and fin:
            condiciones.append("m.fecha_programada BETWEEN %s AND %s")
            valores.extend([inicio, fin])

        where_clause = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        query = f"""
            SELECT m.mantenimiento_id, ma.nombre, m.tipo, m.fecha_programada, m.estado
            FROM Mantenimiento m
            JOIN Maquinaria ma ON m.maquinaria_id = ma.maquinaria_id
            {where_clause}
            ORDER BY m.fecha_programada DESC
        """
        cur.execute(query, tuple(valores))
        mantenimientos = cur.fetchall()

    conn.close()

    return render_template('mantenimientos/mantenimientos.html',
                           mantenimientos=mantenimientos,
                           filtro=filtro_texto,
                           tipo=tipo,
                           estado=estado,
                           inicio=inicio,
                           fin=fin)
# Página para crear un nuevo mantenimiento
@mantenimientos_bp.route('/mantenimientos/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_mantenimiento():
    conn = get_db_connection()
    if request.method == 'POST':
        maquinaria_id = request.form['maquinaria_id']
        usuario_id = request.form['usuario_id_responsable']
        frecuencia_id = request.form['frecuencia_id']
        tipo = request.form['tipo']
        fecha_programada = request.form['fecha_programada']
        descripcion = request.form['descripcion']

        with conn.cursor() as cur:
            # Insertar el mantenimiento
            cur.execute("""
                INSERT INTO Mantenimiento 
                (maquinaria_id, usuario_id_responsable, frecuencia_id, tipo, fecha_programada, estado, descripcion)
                VALUES (%s, %s, %s, %s, %s, 'Pendiente', %s)
                RETURNING mantenimiento_id;
            """, (maquinaria_id, usuario_id, frecuencia_id, tipo, fecha_programada, descripcion))
            mantenimiento_id = cur.fetchone()[0]

            # Crear la orden de trabajo automáticamente
            cur.execute("""
                INSERT INTO OrdenTrabajo (mantenimiento_id, fecha_asignacion, estado)
                VALUES (%s, %s, 'pendiente');
            """, (mantenimiento_id, date.today()))  # Asignamos la fecha de hoy

            conn.commit()
            flash('✅ Mantenimiento y orden de trabajo creados exitosamente.', 'success')
        conn.close()
        return redirect(url_for('mantenimientos.lista_mantenimientos'))

    # Obtener maquinaria, usuarios y frecuencias para el formulario
    with conn.cursor() as cur:
        cur.execute("SELECT maquinaria_id, nombre FROM Maquinaria;")
        maquinas = cur.fetchall()
        cur.execute("SELECT usuario_id, nombre FROM Usuario;")
        usuarios = cur.fetchall()
        cur.execute("SELECT frecuencia_id, descripcion FROM FrecuenciaMantenimiento;")
        frecuencias = cur.fetchall()
    conn.close()
    return render_template('mantenimientos/nuevo.html', maquinas=maquinas, usuarios=usuarios, frecuencias=frecuencias)

# Página para editar un mantenimiento existente
@mantenimientos_bp.route('/mantenimientos/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_mantenimiento(id):
    conn = get_db_connection()

    if request.method == 'POST':
        maquinaria_id = request.form['maquinaria_id']
        usuario_id = request.form['usuario_id_responsable']
        frecuencia_id = request.form['frecuencia_id']
        tipo = request.form['tipo']
        fecha_programada = request.form['fecha_programada']
        estado = request.form['estado']
        descripcion = request.form['descripcion']

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Mantenimiento
                SET maquinaria_id=%s,
                    usuario_id_responsable=%s,
                    frecuencia_id=%s,
                    tipo=%s,
                    fecha_programada=%s,
                    estado=%s,
                    descripcion=%s
                WHERE mantenimiento_id=%s
            """, (maquinaria_id, usuario_id, frecuencia_id, tipo, fecha_programada, estado, descripcion, id))
            conn.commit()
            flash('✅ Mantenimiento actualizado correctamente.', 'success')
        conn.close()
        return redirect(url_for('mantenimientos.lista_mantenimientos'))

    # GET - Cargar datos actuales
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Mantenimiento WHERE mantenimiento_id=%s;", (id,))
        mantenimiento = cur.fetchone()

        if mantenimiento is None:
            flash("⚠️ Mantenimiento no encontrado.", "danger")
            conn.close()
            return redirect(url_for('mantenimientos.lista_mantenimientos'))

        cur.execute("SELECT maquinaria_id, nombre FROM Maquinaria;")
        maquinas = cur.fetchall()

        cur.execute("SELECT usuario_id, nombre FROM Usuario;")
        usuarios = cur.fetchall()

        cur.execute("SELECT frecuencia_id, descripcion FROM FrecuenciaMantenimiento;")
        frecuencias = cur.fetchall()

    conn.close()
    return render_template(
        'mantenimientos/editar.html',
        mantenimiento=mantenimiento,
        maquinas=maquinas,
        usuarios=usuarios,
        frecuencias=frecuencias
    )

# Página para ejecutar el mantenimiento y finalizar la orden de trabajo
@mantenimientos_bp.route('/mantenimientos/ejecutar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def ejecutar_mantenimiento(id):
    conn = get_db_connection()
    if request.method == 'POST':
        fecha_realizada = request.form['fecha_realizada']
        estado = request.form['estado']
        descripcion = request.form['descripcion']
        costo_total = request.form['costo_total']

        with conn.cursor() as cur:
            # Actualizar mantenimiento
            cur.execute("""
                UPDATE Mantenimiento
                SET fecha_realizada=%s, estado=%s, descripcion=%s, costo_total=%s
                WHERE mantenimiento_id=%s
            """, (fecha_realizada, estado, descripcion, costo_total, id))

            # Actualizar la orden de trabajo (poner la fecha de finalización)
            cur.execute("""
                UPDATE OrdenTrabajo
                SET estado='finalizado', fecha_finalizacion=%s
                WHERE mantenimiento_id=%s
            """, (fecha_realizada, id))  # La fecha de finalización es la fecha de ejecución

            conn.commit()
            flash('✅ Mantenimiento ejecutado y orden de trabajo finalizada.', 'success')
        conn.close()
        return redirect(url_for('mantenimientos.lista_mantenimientos'))

    # Cargar datos actuales del mantenimiento
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Mantenimiento WHERE mantenimiento_id=%s;", (id,))
        mantenimiento = cur.fetchone()
    conn.close()
    return render_template('mantenimientos/ejecutar.html', mantenimiento=mantenimiento)

# Eliminar mantenimiento
@mantenimientos_bp.route('/mantenimientos/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_mantenimiento(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Mantenimiento WHERE mantenimiento_id=%s;", (id,))
        flash('✅ Mantenimiento eliminado correctamente.', 'success')
    conn.close()
    return redirect(url_for('mantenimientos.lista_mantenimientos'))
