from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
from auth import login_requerido , roles_requeridos

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
@login_requerido
@roles_requeridos('admin')
def lista_usuarios():
    nombre = request.args.get('nombre', '').strip().lower()
    correo = request.args.get('correo', '').strip().lower()
    rol = request.args.get('rol', '').strip().lower()

    conn = get_db_connection()
    with conn.cursor() as cur:
        query = """
            SELECT usuario_id, nombre, correo, rol, estado
            FROM Usuario
            WHERE 1=1
        """
        params = []

        if nombre:
            query += " AND LOWER(nombre) LIKE %s"
            params.append(f"%{nombre}%")
        if correo:
            query += " AND LOWER(correo) LIKE %s"
            params.append(f"%{correo}%")
        if rol:
            query += " AND LOWER(rol) = %s"
            params.append(rol)

        query += " ORDER BY nombre"
        cur.execute(query, params)
        usuarios = cur.fetchall()
    conn.close()

    return render_template('usuarios/usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']  
        rol = request.form['rol']
        estado = bool(int(request.form['estado']))

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Usuario (nombre, correo, contraseña, rol, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, contraseña, rol, estado))
            conn.commit()
            flash('Usuario registrado exitosamente.', 'success')
        conn.close()
        return redirect(url_for('usuarios.lista_usuarios'))

    return render_template('usuarios/nuevo.html')

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_usuario(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT usuario_id, nombre, correo, contraseña, rol, estado FROM Usuario WHERE usuario_id = %s;", (id,))
        usuario = cur.fetchone()

    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('usuarios.lista_usuarios'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        rol = request.form['rol']
        estado = bool(int(request.form['estado']))

        with conn.cursor() as cur:
            if contraseña:
                # Actualiza con contraseña nueva (sin hash, según tu configuración)
                cur.execute("""
                    UPDATE Usuario 
                    SET nombre=%s, correo=%s, contraseña=%s, rol=%s, estado=%s 
                    WHERE usuario_id=%s
                """, (nombre, correo, contraseña, rol, estado, id))
            else:
                # Actualiza sin cambiar la contraseña
                cur.execute("""
                    UPDATE Usuario 
                    SET nombre=%s, correo=%s, rol=%s, estado=%s 
                    WHERE usuario_id=%s
                """, (nombre, correo, rol, estado, id))
            conn.commit()
            flash('Usuario actualizado correctamente.', 'success')
        conn.close()
        return redirect(url_for('usuarios.lista_usuarios'))

    conn.close()
    return render_template('usuarios/editar.html', usuario=usuario)

@usuarios_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_usuario(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Verificar si hay mantenimientos pendientes para este usuario
        cur.execute("""
            SELECT mantenimiento_id 
            FROM Mantenimiento 
            WHERE usuario_id_responsable = %s AND estado = 'Pendiente'
            LIMIT 1;
        """, (id,))
        pendiente = cur.fetchone()

        if pendiente:
            mantenimiento_id = pendiente[0]
            flash('⚠️ No se puede eliminar el usuario. Tiene mantenimientos pendientes. Por favor, reasígnalos.', 'danger')
            conn.close()
            # Redirige a la vista de edición de mantenimiento
            return redirect(url_for('mantenimientos.editar_mantenimiento', id=mantenimiento_id))

        # Si no hay pendientes, eliminar usuario
        cur.execute("DELETE FROM Usuario WHERE usuario_id = %s;", (id,))
        conn.commit()
        flash('✅ Usuario eliminado correctamente.', 'success')
    conn.close()
    return redirect(url_for('usuarios.lista_usuarios'))

