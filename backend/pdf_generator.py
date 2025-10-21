from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import os
from datetime import datetime

def generate_certificate_pdf(equipment_data, output_path):
    """
    Genera un certificado PDF de calibración para un equipo.
    Diseño moderno y compacto que cabe en una sola página.
    """
    # Crear el documento con márgenes reducidos
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Logo pequeño en esquina superior izquierda
    logo_path = Path(__file__).parent / 'static' / 'logo_asconsa.png'
    if os.path.exists(logo_path):
        logo = Image(str(logo_path), width=4*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        elements.append(logo)
        elements.append(Spacer(1, 0.3*cm))
    
    # Título compacto
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a5f3d'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    title = Paragraph("CERTIFICADO DE CALIBRACIÓN", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*cm))
    
    # Texto legal específico de ASCONSA
    legal_style = ParagraphStyle(
        'LegalText',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=10
    )
    
    legal_text = """
    ASCONSA Soluciones de Seguridad, SL, como taller autorizado por MSA certifica que los instrumentos 
    cuyos datos de identificación se relacionan han sido inspeccionados y/o reparados, verificados y 
    ajustados en nuestros talleres siguiendo el procedimiento establecido por el fabricante y utilizando 
    materiales originales, y quedando por tanto el aparato en condiciones de uso. Este certificado no 
    supone ninguna garantía para las partes o materiales no sustituidos. Toda información sobre garantías 
    de los equipos y sus componentes se recoge en su manual de instrucciones. Se recomienda comprobar su 
    operatividad antes de cada uso, así como pasar gas patrón por el mismo para, si procede, ajustarlo 
    periódicamente en función del uso y asegurar la confianza de las lecturas. Se recomienda así mismo 
    que el instrumento sea verificado por MSA o por taller autorizado con al menos una periodicidad anual, 
    según etiqueta de PROXIMO MANTENIMIENTO pegada al instrumento, o antes si se observasen anomalías 
    en su funcionamiento o deterioro en alguna de sus partes.
    """
    legal_para = Paragraph(legal_text, legal_style)
    elements.append(legal_para)
    elements.append(Spacer(1, 0.3*cm))
    
    # Información del Equipo y Cliente en formato compacto
    heading_style = ParagraphStyle(
        'Heading',
        fontSize=10,
        textColor=colors.HexColor('#1a5f3d'),
        fontName='Helvetica-Bold',
        spaceAfter=5
    )
    elements.append(Paragraph("DATOS DEL EQUIPO Y CLIENTE", heading_style))
    
    info_data = [
        ["Nº Serie:", equipment_data.get('serial_number', 'N/A'), "Marca:", equipment_data.get('brand', 'N/A')],
        ["Modelo:", equipment_data.get('model', 'N/A'), "Cliente:", equipment_data.get('client_name', 'N/A')],
        ["CIF:", equipment_data.get('client_cif', 'N/A'), "Departamento:", equipment_data.get('client_departamento', 'N/A')],
        ["Fecha Calibración:", equipment_data.get('calibration_date', 'N/A'), "Técnico:", equipment_data.get('technician', 'N/A')]
    ]
    
    info_table = Table(info_data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Tabla de Sensores compacta
    elements.append(Paragraph("RESULTADOS DE CALIBRACIÓN", heading_style))
    
    calibration_data = equipment_data.get('calibration_data', [])
    if calibration_data:
        sensor_headers = ['Sensor', 'Pre-Alarma', 'Alarma', 'Valor Cal.', 'Zero', 'SPAN', 'Botella', 'APTO']
        sensor_rows = [sensor_headers]
        
        for sensor in calibration_data:
            row = [
                sensor.get('sensor', '')[:15],  # Truncar si es muy largo
                sensor.get('pre_alarm', ''),
                sensor.get('alarm', ''),
                sensor.get('calibration_value', ''),
                sensor.get('valor_zero', ''),
                sensor.get('valor_span', ''),
                sensor.get('calibration_bottle', ''),
                'SÍ' if sensor.get('approved', False) else 'NO'
            ]
            sensor_rows.append(row)
        
        sensor_table = Table(sensor_rows, colWidths=[3*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.5*cm, 1.5*cm, 2*cm, 1.3*cm])
        sensor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5f3d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(sensor_table)
    
    elements.append(Spacer(1, 0.3*cm))
    
    # Repuestos y Observaciones en formato compacto
    spare_parts = equipment_data.get('spare_parts', 'Ninguno')
    if spare_parts and spare_parts.strip():
        elements.append(Paragraph("REPUESTOS UTILIZADOS", heading_style))
        spare_style = ParagraphStyle('Spare', parent=styles['Normal'], fontSize=8, spaceAfter=5)
        elements.append(Paragraph(spare_parts, spare_style))
    
    observations = equipment_data.get('observations', '')
    if observations and observations.strip():
        elements.append(Paragraph("OBSERVACIONES", heading_style))
        obs_style = ParagraphStyle('Obs', parent=styles['Normal'], fontSize=8, spaceAfter=5)
        elements.append(Paragraph(observations, obs_style))
    
    elements.append(Spacer(1, 0.4*cm))
    
    # Firmas compactas
    signature_data = [
        ["", ""],
        ["_______________________", "_______________________"],
        ["Técnico", "Supervisor"],
        [equipment_data.get('technician', ''), ""]
    ]
    
    signature_table = Table(signature_data, colWidths=[8.5*cm, 8.5*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, 1), 15),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 3),
    ]))
    elements.append(signature_table)
    
    # Pie de página
    elements.append(Spacer(1, 0.3*cm))
    footer_text = f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}"
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(footer_text, footer_style))
    
    # Construir el PDF
    doc.build(elements)
    return output_path
