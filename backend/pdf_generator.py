from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from pathlib import Path
import os
from datetime import datetime

def generate_certificate_pdf(equipment_data, output_path):
    """
    Genera un certificado PDF similar al formato ASCONSA original.
    Diseño basado en el certificado de ejemplo con logo, tablas y estructura específica.
    """
    # Crear el documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # Ancho disponible para tablas
    available_width = 180*mm
    
    # Header con logos
    logo_path = Path(__file__).parent / 'static' / 'logo_asconsa.png'
    
    # Crear tabla para header con logos
    header_data = []
    header_row = []
    
    # Logo ASCONSA izquierda
    if os.path.exists(logo_path):
        logo_asconsa = Image(str(logo_path), width=50*mm, height=25*mm)
        header_row.append(logo_asconsa)
    else:
        header_row.append(Paragraph("ASCONSA", styles['Heading1']))
    
    # Espacio central para número de certificado
    cert_number = equipment_data.get('certificate_number', 'N/A')
    cert_style = ParagraphStyle(
        'CertNum',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    cert_text = f"CERTIFICADO Nº<br/>{cert_number}"
    header_row.append(Paragraph(cert_text, cert_style))
    
    # Logo MSA derecha (placeholder si no existe)
    header_row.append(Paragraph("", styles['Normal']))  # MSA logo placeholder
    
    header_data.append(header_row)
    
    header_table = Table(header_data, colWidths=[60*mm, 60*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5*mm))
    
    # Título principal
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=5*mm
    )
    title = Paragraph("AJUSTE, VERIFICACIÓN, INSPECCIÓN Y/O REPARACIÓN", title_style)
    elements.append(title)
    
    # Información del equipo en cajas
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=9, leading=11)
    
    info_data = [
        [Paragraph("<b>CLIENTE:</b>", info_style), Paragraph(equipment_data.get('client_name', 'N/A'), info_style),
         Paragraph("<b>LOCALIDAD:</b>", info_style), Paragraph(equipment_data.get('client_departamento', 'N/A'), info_style)],
        [Paragraph("<b>EQUIPO:</b>", info_style), Paragraph(f"{equipment_data.get('brand', '')} {equipment_data.get('model', '')}", info_style),
         Paragraph("<b>No. SERIE:</b>", info_style), Paragraph(equipment_data.get('serial_number', 'N/A'), info_style)],
        [Paragraph("<b>Nº ALBARÁN:</b>", info_style), Paragraph(equipment_data.get('delivery_note', ''), info_style),
         Paragraph("<b>FECHA:</b>", info_style), Paragraph(equipment_data.get('calibration_date', 'N/A'), info_style)]
    ]
    
    info_table = Table(info_data, colWidths=[30*mm, 60*mm, 30*mm, 60*mm])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5*mm))
    
    # Texto legal
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_JUSTIFY,
        leading=10,
        spaceAfter=3*mm
    )
    
    legal_text = """
    <b>ASCONSA Soluciones de Seguridad, SL</b>, como taller autorizado por MSA certifica que los instrumentos 
    cuyos datos de identificación se relacionan han sido inspeccionados y/o reparados, verificados y 
    ajustados en nuestros talleres siguiendo el procedimiento establecido por el fabricante y utilizando 
    materiales originales, y quedando por tanto el aparato en condiciones de uso.
    """
    elements.append(Paragraph(legal_text, legal_style))
    
    disclaimers = """
    Este certificado no supone ninguna garantía para las partes o materiales no sustituidos. Toda información 
    sobre garantías de los equipos y sus componentes se recoge en su manual de instrucciones. Se recomienda 
    comprobar su operatividad antes de cada uso, así como pasar gas patrón por el mismo para, si procede, 
    ajustarlo periódicamente en función del uso y asegurar la confianza de las lecturas. Se recomienda así 
    mismo que el instrumento sea verificado por MSA o por taller autorizado con al menos una periodicidad 
    anual, según etiqueta de PROXIMO MANTENIMIENTO pegada al instrumento, o antes si se observasen anomalías 
    en su funcionamiento o deterioro en alguna de sus partes.
    """
    elements.append(Paragraph(disclaimers, legal_style))
    elements.append(Spacer(1, 3*mm))
    
    # Repuestos Utilizados
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
    spare_parts = equipment_data.get('spare_parts', [])
    
    if spare_parts and len(spare_parts) > 0:
        elements.append(Paragraph("REPUESTOS UTILIZADOS", section_style))
        elements.append(Spacer(1, 2*mm))
        
        # Crear tabla de repuestos
        spare_headers = [
            Paragraph("<b>DESCRIPCIÓN</b>", info_style),
            Paragraph("<b>REFERENCIA</b>", info_style),
            Paragraph("<b>GARANTÍA</b>", info_style)
        ]
        spare_rows = [spare_headers]
        
        for part in spare_parts:
            row = [
                Paragraph(part.get('descripcion', ''), info_style),
                Paragraph(part.get('referencia', ''), info_style),
                Paragraph('GARANTÍA' if part.get('garantia', False) else '', info_style)
            ]
            spare_rows.append(row)
        
        spare_table = Table(spare_rows, colWidths=[90*mm, 60*mm, 30*mm])
        spare_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(spare_table)
        elements.append(Spacer(1, 3*mm))
    
    # Tabla de Datos de Calibración
    elements.append(Paragraph("DATOS DE CALIBRACIÓN", section_style))
    elements.append(Spacer(1, 2*mm))
    
    calibration_data = equipment_data.get('calibration_data', [])
    if calibration_data:
        # Headers
        cal_headers = [
            Paragraph("<b>GAS/SENSOR</b>", info_style),
            Paragraph("<b>PRE-ALARMA</b>", info_style),
            Paragraph("<b>ALARMA</b>", info_style),
            Paragraph("<b>VALOR CAL.</b>", info_style),
            Paragraph("<b>ZERO</b>", info_style),
            Paragraph("<b>SPAN</b>", info_style),
            Paragraph("<b>Nº BOTELLA</b>", info_style),
            Paragraph("<b>APTO</b>", info_style)
        ]
        cal_rows = [cal_headers]
        
        for sensor in calibration_data:
            row = [
                Paragraph(sensor.get('sensor', ''), info_style),
                Paragraph(sensor.get('pre_alarm', ''), info_style),
                Paragraph(sensor.get('alarm', ''), info_style),
                Paragraph(sensor.get('calibration_value', ''), info_style),
                Paragraph(sensor.get('valor_zero', ''), info_style),
                Paragraph(sensor.get('valor_span', ''), info_style),
                Paragraph(sensor.get('calibration_bottle', ''), info_style),
                Paragraph('SÍ' if sensor.get('approved', False) else 'NO', info_style)
            ]
            cal_rows.append(row)
        
        # Calcular anchos para llenar el espacio disponible
        col_widths = [35*mm, 18*mm, 18*mm, 20*mm, 18*mm, 18*mm, 25*mm, 15*mm]
        cal_table = Table(cal_rows, colWidths=col_widths)
        cal_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(cal_table)
    
    elements.append(Spacer(1, 3*mm))
    
    # Observaciones
    observations = equipment_data.get('observations', '')
    if observations and observations.strip():
        elements.append(Paragraph("OBSERVACIONES", section_style))
        elements.append(Spacer(1, 2*mm))
        
        obs_data = [[Paragraph(observations, info_style)]]
        obs_table = Table(obs_data, colWidths=[available_width])
        obs_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(obs_table)
        elements.append(Spacer(1, 3*mm))
    
    # Firma del Técnico (sin supervisor)
    elements.append(Paragraph("FIRMAS Y SELLO", section_style))
    elements.append(Spacer(1, 3*mm))
    
    signature_data = [
        ["", ""],
        ["", ""],
        ["", ""],
        [Paragraph("<b>Operario:</b>", info_style), ""],
        [Paragraph(equipment_data.get('technician', ''), info_style), ""]
    ]
    
    signature_table = Table(signature_data, colWidths=[90*mm, 90*mm])
    signature_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 3), (0, 3), 1, colors.black),
        ('ALIGN', (0, 3), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 3), (-1, 3), 15),
    ]))
    elements.append(signature_table)
    
    # Footer
    elements.append(Spacer(1, 5*mm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER)
    footer_text = f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}"
    elements.append(Paragraph(footer_text, footer_style))
    
    # Construir el PDF
    doc.build(elements)
    return output_path
