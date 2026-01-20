from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas  
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfMerger # sirve para importar la clase PdfMerger del módulo PyPDF2, que se utiliza para combinar (mergear) múltiples archivos PDF en uno solo.  pip install PyPDF2
from django.conf import settings

def generar_pdf_resultado(resultado_estudio):
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(
            f"No se encontró la fuente '{font_path}'.\n"
            "Asegúrate de haber descargado DejaVuSans.ttf y de colocarla en /static/fonts/"
        )

    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    
    tipo = resultado_estudio.turno_estudio.orden.tipo_estudio.tipo_resultado
    turno = resultado_estudio.turno_estudio
    paciente = turno.orden.paciente.persona
    profesional = turno.orden.solicitado_por.persona
    especialidad = turno.orden.consulta.turno.especialidad
    estudio = turno.orden.tipo_estudio

    # Encabezado para todos los tipos
    encabezado = [
        f"<b>Paciente:</b> {paciente.get_full_name()} - <b>DNI:</b> {paciente.dni}",
        f"<b>Estudio:</b> {estudio.nombre_estudio} - Servicio encargado: {estudio.servicio_diagnostico.nombre_servicio} - Lugar: {turno.lugar.nombre}",
        f"<b>Fecha del estudio:</b> {turno.fecha_turno.strftime('%d/%m/%Y')}",
        f"<b>Solicitado por:</b> {profesional.get_full_name()} - <b>DNI:</b> {profesional.dni} - <b>Especialidad:</b> {especialidad.nombre_especialidad}",
        f"<b>N° Orden:</b> {turno.orden.id}",
        f"<b>Motivo del estudio:</b> {turno.orden.motivo_estudio}",
    ]
    
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = 'DejaVuSans'
    styles["Heading1"].fontName = 'DejaVuSans'
    styles["Heading2"].fontName = 'DejaVuSans'    

    # --- CASO: Imagen ---
    if tipo == "img":
        # Primera página con encabezado e informe
        buffer_texto = BytesIO()
        doc = SimpleDocTemplate(
            buffer_texto,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )  

        elements = []
        elements.append(Paragraph("Resultado del Estudio", styles["Heading1"]))
        elements.append(Spacer(1, 20))

        for linea in encabezado:
            elements.append(Paragraph(linea, styles["Normal"]))
            elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 12))

        if resultado_estudio.informe:
            elements.append(Paragraph("<b>Informe</b>", styles["Heading2"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(str(resultado_estudio.informe).replace("\n", "<br/>"), styles["Normal"]))

        doc.build(elements)

        # Páginas de imágenes (una por hoja, tamaño completo)
        buffer_imagenes = BytesIO()
        c = canvas.Canvas(buffer_imagenes, pagesize=A4)
        imagenes = resultado_estudio.imagenes.all()
        for img in imagenes:
            try:
                c.drawImage(img.imagen.path, 0, 0, width=A4[0], height=A4[1])
                c.showPage()

                # Limpiar archivos temporales
                if os.path.exists(img.imagen.path):
                    os.remove(img.imagen.path)
                img.delete()
            except Exception as e:
                print(f"Error procesando imagen {img}: {e}")

        c.save()

        # Combinar textos + imágenes
        pdf_final = BytesIO()
        merger = PdfMerger()
        merger.append(buffer_texto)
        if imagenes.exists():
            merger.append(buffer_imagenes)
        merger.write(pdf_final)
        merger.close()

        # Guardar PDF final
        nombre_archivo = f"resultado_estudio_{resultado_estudio.id}.pdf"
        resultado_estudio.archivo_pdf.save(nombre_archivo, ContentFile(pdf_final.getvalue()))
        resultado_estudio.save()
        return

    # --- Para el resto de tipos (lab, fisio, eval) ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=40,
        bottomMargin=40
    )
    elements = []
    elements.append(Paragraph("Resultado del Estudio", styles["Heading1"]))
    elements.append(Spacer(1, 20))

    for linea in encabezado:
        elements.append(Paragraph(linea, styles["Normal"]))
        elements.append(Spacer(1, 6))
    elements.append(Spacer(1, 12))

    # Laboratorio
    if tipo == "lab" and resultado_estudio.datos_especificos:
        data = [["Parámetro", "Valor", "Unidad", "Referencia"]]
        for param, detalle in resultado_estudio.datos_especificos.items():
            data.append([
                Paragraph(str(param), styles["Normal"]),
                Paragraph(str(detalle.get("valor", "")), styles["Normal"]),
                Paragraph(str(detalle.get("unidad", "")), styles["Normal"]),
                Paragraph(str(detalle.get("referencia", "")), styles["Normal"])
            ])

        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]))
        elements.append(Paragraph("<b>Resultados de Laboratorio</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        elements.append(tabla)
        elements.append(Spacer(1, 20))

    # Estudio fisiológico
    elif tipo == "fisio" and resultado_estudio.datos_especificos:
        data = [["Parámetro", "Valor", "Unidad","Referencia","Interpretacion"]]
        for param, detalle in resultado_estudio.datos_especificos.items():
            data.append([
                Paragraph(str(param), styles["Normal"]),
                Paragraph(str(detalle.get("valor", "")), styles["Normal"]),
                Paragraph(str(detalle.get("unidad", "")), styles["Normal"]),
                Paragraph(str(detalle.get("referencia", "")), styles["Normal"]),
                Paragraph(str(detalle.get("interpretacion", "")), styles["Normal"])
            ])

        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]))
        elements.append(Paragraph("<b>Resultados de Estudio Fisiológico</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        elements.append(tabla)
        elements.append(Spacer(1, 20))

    # Evaluación clínica
    elif tipo == "eval":
        elements.append(Paragraph("<b>Evaluación Clínica</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))

    # Informe (para lab, fisio, eval)
    if resultado_estudio.informe:
        elements.append(Paragraph("<b>Informe</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(str(resultado_estudio.informe).replace("\n", "<br/>"), styles["Normal"]))

    # Guardar PDF final
    doc.build(elements)
    nombre_archivo = f"resultado_estudio_{resultado_estudio.id}.pdf"
    resultado_estudio.archivo_pdf.save(nombre_archivo, ContentFile(buffer.getvalue()))
    resultado_estudio.save()