from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth import login_requerido
from db import get_db_connection

inventario_bp = Blueprint('inventario', __name__)

# 📦 Lista de repuestos con filtros
@inventario_bp.route('/inventario/repuestos')
@login_requerido
def lista_repuestos():
    nombre = request.args.get('nombre', '').strip().lower()
    proveedor = request.args.get('proveedor', '').strip().lower()
    stock_min = request.args.get('stock', '').strip()

    conn = get_db_connection()
    with conn.cursor() as cur:
        query = """
            SELECT r.repuesto_id, r.nombre, r.descripcion, r.stock, r.unidad_medida,
                   r.precio_unitario, p.nombre AS proveedor
            FROM Repuesto r
            JOIN Proveedor p ON r.proveedor_id = p.proveedor_id
            WHERE 1=1
        """
        params = []

        if nombre:
            query += " AND LOWER(r.nombre) LIKE %s"
            params.append(f"%{nombre}%")
        if proveedor:
            query += " AND LOWER(p.nombre) LIKE %s"
            params.append(f"%{proveedor}%")
        if stock_min:
            query += " AND r.stock >= %s"
            params.append(stock_min)

        query += " ORDER BY r.nombre"
        cur.execute(query, params)
        repuestos = cur.fetchall()
    conn.close()

    return render_template('inventario/repuestos.html', repuestos=repuestos)


# ➕ Nuevo repuesto
@inventario_bp.route('/inventario/repuestos/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_repuesto():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT proveedor_id, nombre FROM Proveedor")
        proveedores = cur.fetchall()

    if request.method == 'POST':
        proveedor_id = request.form['proveedor_id']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        unidad_medida = request.form['unidad_medida']
        precio_unitario = request.form['precio_unitario']

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Repuesto (proveedor_id, nombre, descripcion, stock, unidad_medida, precio_unitario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (proveedor_id, nombre, descripcion, stock, unidad_medida, precio_unitario))
            flash('Repuesto registrado exitosamente.', 'success')
        conn.close()
        return redirect(url_for('inventario.lista_repuestos'))

    return render_template('inventario/nuevo_repuesto.html', proveedores=proveedores)

# 🛠 Editar repuesto
@inventario_bp.route('/inventario/repuestos/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_repuesto(id):
    conn = get_db_connection()
    if request.method == 'POST':
        proveedor_id = request.form['proveedor_id']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        unidad_medida = request.form['unidad_medida']
        precio_unitario = request.form['precio_unitario']

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Repuesto SET proveedor_id=%s, nombre=%s, descripcion=%s, stock=%s,
                unidad_medida=%s, precio_unitario=%s WHERE repuesto_id=%s
            """, (proveedor_id, nombre, descripcion, stock, unidad_medida, precio_unitario, id))
            flash('Repuesto actualizado correctamente.', 'success')
        conn.close()
        return redirect(url_for('inventario.lista_repuestos'))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Repuesto WHERE repuesto_id = %s", (id,))
        repuesto = cur.fetchone()
        cur.execute("SELECT proveedor_id, nombre FROM Proveedor")
        proveedores = cur.fetchall()
    conn.close()
    return render_template('inventario/editar_repuesto.html', repuesto=repuesto, proveedores=proveedores)

# 🗑 Eliminar repuesto
@inventario_bp.route('/inventario/repuestos/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_repuesto(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Repuesto WHERE repuesto_id = %s", (id,))
        flash('Repuesto eliminado correctamente.', 'success')
    conn.close()
    return redirect(url_for('inventario.lista_repuestos'))
