from flask import Blueprint, render_template, request, send_file, flash
from auth import login_requerido
from db import get_db_connection
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
@login_requerido
def reportes():
    return render_template('reportes/generar.html')

# -------------------- MANTENIMIENTOS --------------------
@reportes_bp.route('/reportes/mantenimientos/preview')
@login_requerido
def vista_mantenimientos():
    i = request.args.get('inicio')
    f = request.args.get('fin')
    return generar_mantenimientos(i, f)

@reportes_bp.route('/reportes/mantenimientos/descargar')
@login_requerido
def descargar_mantenimientos():
    i = request.args.get('inicio')
    f = request.args.get('fin')
    return generar_mantenimientos(i, f, True)

def generar_mantenimientos(i, f, descarga=False):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT m.mantenimiento_id, maq.nombre, m.tipo, m.fecha_programada,
                   m.fecha_realizada, m.estado, m.descripcion, m.costo_total
            FROM Mantenimiento m
            JOIN Maquinaria maq ON m.maquinaria_id = maq.maquinaria_id
            WHERE m.fecha_programada BETWEEN %s AND %s
            ORDER BY m.fecha_programada
        """, (i, f))
        datos = cur.fetchall()
    conn.close()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 80

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Reporte de Mantenimientos")
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 65, f"Desde: {i}  Hasta: {f}    Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    headers = ["ID", "Equipo", "Tipo", "F. Prog.", "F. Real", "Estado", "Costo"]
    x = [50, 90, 190, 260, 330, 400, 470]
    for idx, h in enumerate(headers):
        c.drawString(x[idx], y, h)
    y -= 15
    c.line(45, y + 10, 580, y + 10)

    for d in datos:
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y + 30, "Reporte de Mantenimientos (continuación)")
            c.setFont("Helvetica", 9)
            c.drawString(50, y + 15, f"Desde: {i}  Hasta: {f}    Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            y -= 10
            for idx, h in enumerate(headers):
                c.drawString(x[idx], y, h)
            y -= 15
            c.line(45, y + 10, 580, y + 10)

        mantenimiento_id = str(d[0]) if d[0] else "-"
        equipo = d[1] if d[1] else "-"
        tipo = d[2] if d[2] else "-"
        fecha_prog = d[3].strftime("%Y-%m-%d") if d[3] else "-"
        fecha_real = d[4].strftime("%Y-%m-%d") if d[4] else "-"
        estado = d[5] if d[5] else "-"
        costo = f"{d[7]:.2f}" if d[7] else "0.00"

        c.drawString(x[0], y, mantenimiento_id)
        c.drawString(x[1], y, equipo)
        c.drawString(x[2], y, tipo)
        c.drawString(x[3], y, fecha_prog)
        c.drawString(x[4], y, fecha_real)
        c.drawString(x[5], y, estado)
        c.drawRightString(x[6] + 50, y, costo)
        y -= 14

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=descarga, download_name="reporte_mantenimientos.pdf", mimetype='application/pdf')


# -------------------- REPUESTOS --------------------
@reportes_bp.route('/reportes/repuestos/preview')
@login_requerido
def vista_repuestos():
    return generar_repuestos()

@reportes_bp.route('/reportes/repuestos/descargar')
@login_requerido
def descargar_repuestos():
    return generar_repuestos(True)

def generar_repuestos(descarga=False):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.repuesto_id, r.nombre, r.descripcion, r.stock, r.unidad_medida, r.precio_unitario, p.nombre
            FROM Repuesto r
            JOIN Proveedor p ON r.proveedor_id = p.proveedor_id
            ORDER BY r.nombre
        """)
        datos = cur.fetchall()
    conn.close()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 80

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Reporte de Repuestos")
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 65, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    headers = ["ID", "Nombre", "Descripción", "Stock", "Unidad", "Precio", "Proveedor"]
    x = [50, 80, 160, 290, 340, 400, 460]
    for i, h in enumerate(headers):
        c.drawString(x[i], y, h)
    y -= 15
    c.line(45, y + 10, 580, y + 10)

    for d in datos:
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y + 30, "Reporte de Repuestos (continuación)")
            c.setFont("Helvetica", 9)
            c.drawString(50, y + 15, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            y -= 10
            for i, h in enumerate(headers):
                c.drawString(x[i], y, h)
            y -= 15
            c.line(45, y + 10, 580, y + 10)

        fila = [str(val) if val is not None else "-" for val in d]
        for i, val in enumerate(fila):
            c.drawString(x[i], y, val)
        y -= 14

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=descarga, download_name="reporte_repuestos.pdf", mimetype='application/pdf')


# -------------------- ÓRDENES DE TRABAJO --------------------
@reportes_bp.route('/reportes/ordenes_trabajo')
@login_requerido
def reporte_ordenes_trabajo():
    descarga = request.args.get('download', '0') == '1'
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ot.orden_id,
                   m.mantenimiento_id,
                   COALESCE(u.nombre, 'No asignado') AS tecnico,
                   ot.fecha_asignacion,
                   ot.fecha_finalizacion,
                   ot.estado
            FROM OrdenTrabajo ot
            JOIN Mantenimiento m ON ot.mantenimiento_id = m.mantenimiento_id
            LEFT JOIN Usuario u ON ot.usuario_id_tecnico = u.usuario_id
            ORDER BY ot.fecha_asignacion;
        """)
        datos = cur.fetchall()
    conn.close()

    encabezados = ["ID Orden", "ID Mantto", "Técnico", "Asignado", "Finalizado", "Estado"]
    pdf = generar_pdf_generico("Reporte de Órdenes de Trabajo", encabezados, datos)
    return send_file(pdf, as_attachment=descarga, download_name="ordenes_trabajo.pdf", mimetype='application/pdf')


# -------------------- HISTORIAL MANTENIMIENTOS --------------------
@reportes_bp.route('/reportes/historial_mantenimientos')
@login_requerido
def reporte_historial_mantenimientos():
    descarga = request.args.get('download', '0') == '1'
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT hm.historial_id, m.mantenimiento_id, COALESCE(u.nombre, 'No asignado'), hm.fecha,
                   hm.descripcion, hm.estado
            FROM HistorialMantenimiento hm
            JOIN Mantenimiento m ON hm.mantenimiento_id = m.mantenimiento_id
            LEFT JOIN Usuario u ON hm.usuario_id_registro = u.usuario_id
            ORDER BY hm.fecha;
        """)
        datos = cur.fetchall()
    conn.close()

    encabezados = ["ID", "Mantto", "Usuario", "Fecha", "Descripción", "Estado"]
    pdf = generar_pdf_generico("Reporte de Historial de Mantenimientos", encabezados, datos)
    return send_file(pdf, as_attachment=descarga, download_name="historial_mantenimientos.pdf", mimetype='application/pdf')


# -------------------- BITÁCORA DEL SISTEMA --------------------
@reportes_bp.route('/reportes/bitacora')
@login_requerido
def reporte_bitacora():
    descarga = request.args.get('download', '0') == '1'
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT b.bitacora_id, COALESCE(u.nombre, 'Sistema'), b.accion, b.descripcion, b.fecha_hora
            FROM BitacoraSistema b
            LEFT JOIN Usuario u ON b.usuario_id = u.usuario_id
            ORDER BY b.fecha_hora DESC;
        """)
        datos = cur.fetchall()
    conn.close()

    encabezados = ["ID", "Usuario", "Acción", "Descripción", "Fecha-Hora"]
    pdf = generar_pdf_generico("Reporte de Bitácora del Sistema", encabezados, datos)
    return send_file(pdf, as_attachment=descarga, download_name="bitacora_sistema.pdf", mimetype='application/pdf')


# -------------------- FUNCIÓN GENÉRICA --------------------
def generar_pdf_generico(titulo, encabezados, filas):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 80

    if titulo == "Reporte de Bitácora del Sistema":
        titulo = "Reporte de Bitácora"

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, titulo)
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 65, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    x_positions = []
    espacio = (width - 100) / len(encabezados)
    for i in range(len(encabezados)):
        x_positions.append(50 + i * espacio)

    for i, header in enumerate(encabezados):
        c.drawString(x_positions[i], y, header)
    y -= 15
    c.line(45, y + 10, width - 45, y + 10)

    for fila in filas:
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, titulo)
            c.setFont("Helvetica", 9)
            c.drawString(50, height - 65, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            for i, header in enumerate(encabezados):
                c.drawString(x_positions[i], y, header)
            y -= 15
            c.line(45, y + 10, width - 45, y + 10)

        fila_limpia = [str(val) if val is not None else "-" for val in fila]
        for i, val in enumerate(fila_limpia):
            c.drawString(x_positions[i], y, val)
        y -= 14

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
