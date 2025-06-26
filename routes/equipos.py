from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth import login_requerido, roles_requeridos 
from db import get_db_connection

equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos')
@login_requerido
@roles_requeridos('admin','supervisor')
def lista_equipos():
    nombre = request.args.get('nombre', '').strip()
    estado = request.args.get('estado', '').strip()

    conn = get_db_connection()
    with conn.cursor() as cur:
        query = "SELECT maquinaria_id, nombre, descripcion, estado FROM Maquinaria WHERE 1=1"
        params = []

        if nombre:
            query += " AND LOWER(nombre) LIKE %s"
            params.append(f"%{nombre.lower()}%")
        if estado:
            query += " AND estado = %s"
            params.append(estado)

        query += " ORDER BY nombre"
        cur.execute(query, params)
        equipos = cur.fetchall()
    conn.close()
    return render_template('equipos/equipos.html', equipos=equipos)

@equipos_bp.route('/equipos/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_equipo():
    if request.method == 'POST':
        # Capturar datos del formulario
        nombre = request.form.get('nombre', '').strip()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        serie = request.form.get('serie', '').strip()
        ubicacion = request.form.get('ubicacion', '').strip()
        estado = request.form.get('estado', 'Activo').strip()
        fecha_compra = request.form.get('fecha_compra', None)
        descripcion = request.form.get('descripcion', '').strip()

        # Validación básica
        if not nombre:
            flash('El campo Nombre es obligatorio.', 'error')
            return render_template('equipos/nuevo.html')

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Maquinaria
                    (nombre, marca, modelo, serie, ubicacion, estado, fecha_compra, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nombre, marca, modelo, serie, ubicacion, estado, fecha_compra, descripcion))
                conn.commit()
            flash('Equipo registrado exitosamente.', 'success')
            return redirect(url_for('equipos.lista_equipos'))

        except Exception as e:
            flash(f'Error al registrar equipo: {e}', 'error')
            return render_template('equipos/nuevo.html')

        finally:
            conn.close()

    # GET
    return render_template('equipos/nuevo.html')


@equipos_bp.route('/equipos/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_equipo(id):
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form['nombre']
        marca = request.form['marca']
        modelo = request.form['modelo']
        serie = request.form['serie']
        ubicacion = request.form['ubicacion']
        estado = request.form['estado']

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Maquinaria
                SET nombre=%s, marca=%s, modelo=%s, serie=%s, ubicacion=%s, estado=%s
                WHERE maquinaria_id=%s
            """, (nombre, marca, modelo, serie, ubicacion, estado, id))
            flash('Equipo actualizado correctamente.', 'success')
        conn.close()
        return redirect(url_for('equipos.lista_equipos'))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Maquinaria WHERE maquinaria_id = %s;", (id,))
        equipo = cur.fetchone()
    conn.close()
    return render_template('equipos/editar.html', equipo=equipo)

@equipos_bp.route('/equipos/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_equipo(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Maquinaria WHERE maquinaria_id = %s;", (id,))
        flash('Equipo eliminado correctamente.', 'success')
    conn.close()
    return redirect(url_for('equipos.lista_equipos'))

@equipos_bp.route('/equipos/detalle/<int:id>')
@login_requerido
def detalle_equipo(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Maquinaria WHERE maquinaria_id = %s;", (id,))
        equipo = cur.fetchone()
    conn.close()

    if equipo is None:
        flash('Equipo no encontrado.', 'error')
        return redirect(url_for('equipos.lista_equipos'))

    return render_template('equipos/detalle.html', equipo=equipo)
