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
    
    Args:
        equipment_data: dict con toda la información del equipo, cliente y calibración
        output_path: ruta donde se guardará el PDF
    """
    # Crear el documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a5f3d'),  # Verde oscuro
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a5f3d'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # Logo en la parte superior izquierda
    logo_path = Path(__file__).parent / 'static' / 'logo_asconsa.png'
    if os.path.exists(logo_path):
        logo = Image(str(logo_path), width=6*cm, height=3*cm)
        elements.append(logo)
        elements.append(Spacer(1, 0.5*cm))
    
    # Título
    title = Paragraph("CERTIFICADO DE CALIBRACIÓN", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Texto legal
    legal_text = """
    En cumplimiento de la normativa vigente y los estándares de calidad establecidos, 
    se certifica que el equipo descrito a continuación ha sido sometido a un proceso 
    de calibración y verificación técnica en nuestras instalaciones. Los resultados 
    obtenidos cumplen con los requisitos técnicos y de seguridad aplicables.
    """
    legal_para = Paragraph(legal_text, normal_style)
    elements.append(legal_para)
    elements.append(Spacer(1, 0.5*cm))
    
    # Información del Equipo y Cliente
    elements.append(Paragraph("DATOS DEL EQUIPO Y CLIENTE", heading_style))
    
    info_data = [
        ["Número de Serie:", equipment_data.get('serial_number', 'N/A')],
        ["Marca:", equipment_data.get('brand', 'N/A')],
        ["Modelo:", equipment_data.get('model', 'N/A')],
        ["Cliente:", equipment_data.get('client_name', 'N/A')],
        ["CIF:", equipment_data.get('client_cif', 'N/A')],
        ["Departamento:", equipment_data.get('client_departamento', 'N/A')],
        ["Fecha de Entrada:", equipment_data.get('entry_date', 'N/A')],
        ["Fecha de Calibración:", equipment_data.get('calibration_date', 'N/A')],
        ["Técnico Responsable:", equipment_data.get('technician', 'N/A')]
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabla de Sensores
    elements.append(Paragraph("RESULTADOS DE CALIBRACIÓN DE SENSORES", heading_style))
    
    calibration_data = equipment_data.get('calibration_data', [])
    if calibration_data:
        sensor_headers = [
            'Sensor', 'Pre-Alarma', 'Alarma', 
            'Valor Cal.', 'Valor Zero', 'Valor SPAN', 
            'Botella', 'APTO'
        ]
        sensor_rows = [sensor_headers]
        
        for sensor in calibration_data:
            row = [
                sensor.get('sensor', ''),
                sensor.get('pre_alarm', ''),
                sensor.get('alarm', ''),
                sensor.get('calibration_value', ''),
                sensor.get('valor_zero', ''),
                sensor.get('valor_span', ''),
                sensor.get('calibration_bottle', ''),
                'SÍ' if sensor.get('approved', False) else 'NO'
            ]
            sensor_rows.append(row)
        
        sensor_table = Table(sensor_rows, colWidths=[2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 1.5*cm])
        sensor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5f3d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(sensor_table)
    else:
        elements.append(Paragraph("No se registraron datos de calibración de sensores.", normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Repuestos Utilizados
    elements.append(Paragraph("REPUESTOS UTILIZADOS", heading_style))
    spare_parts = equipment_data.get('spare_parts', 'Ninguno')
    spare_parts_para = Paragraph(spare_parts if spare_parts else 'Ninguno', normal_style)
    elements.append(spare_parts_para)
    elements.append(Spacer(1, 1*cm))
    
    # Observaciones
    observations = equipment_data.get('observations', '')
    if observations:
        elements.append(Paragraph("OBSERVACIONES", heading_style))
        obs_para = Paragraph(observations, normal_style)
        elements.append(obs_para)
        elements.append(Spacer(1, 1*cm))
    
    # Firmas
    elements.append(Spacer(1, 1*cm))
    signature_data = [
        ["", ""],
        ["_______________________", "_______________________"],
        ["Técnico", "Supervisor"],
        [equipment_data.get('technician', ''), ""]
    ]
    
    signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 20),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 5),
    ]))
    elements.append(signature_table)
    
    # Pie de página
    elements.append(Spacer(1, 1*cm))
    footer_text = f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}"
    footer_para = Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    ))
    elements.append(footer_para)
    
    # Construir el PDF
    doc.build(elements)
    return output_path
