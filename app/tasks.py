"""
Celery tasks for medicalreserva app.
"""
from celery import shared_task
import logging
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta, datetime
from app.models import Reserva, Doctor, Paciente
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def recordatorio_reserva_proxima(self):
    """
    Tarea periódica que envía recordatorios para reservas próximas (en 24 horas).
    Incluye lógica de reintento en caso de fallo.
    """
    try:
        ahora = timezone.now()
        manana = ahora + timedelta(hours=24)
        
        reservas_proximas = Reserva.objects.filter(
            fecha_hora__range=[ahora, manana],
            estado__in=['pendiente', 'confirmada']
        )
        
        for reserva in reservas_proximas:
            logger.info(f"[RECORDATORIO] Reserva #{reserva.id} próxima en 24 horas")
            # Aquí integrarías tu lógica de envío de email o SMS
            print(f"RECORDATORIO: Reserva #{reserva.id} de {reserva.paciente.usuario.get_full_name()} con Dr. {reserva.doctor.nombre} en 24 horas")
        
        return {
            'status': 'success',
            'recordatorios_enviados': reservas_proximas.count()
        }
    except Exception as exc:
        logger.error(f"Error en recordatorio_reserva_proxima: {exc}")
        # Reintenta la tarea en 60 segundos si ocurre un error
        raise self.retry(exc=exc, countdown=60)


@shared_task
def limpiar_reservas_antiguas():
    """
    Tarea periódica que marca como completadas las reservas que ya pasaron.
    """
    try:
        ahora = timezone.now()
        
        reservas_pasadas = Reserva.objects.filter(
            fecha_hora__lt=ahora,
            estado__in=['pendiente', 'confirmada']
        )
        
        count = reservas_pasadas.update(estado='completada')
        
        logger.info(f"[LIMPIAR] {count} reservas marcadas como completadas")
        print(f"LIMPIAR: {count} reservas marcadas como completadas")
        
        return {
            'status': 'success',
            'reservas_completadas': count
        }
    except Exception as exc:
        logger.error(f"Error en limpiar_reservas_antiguas: {exc}")
        return {'status': 'error', 'message': str(exc)}


@shared_task
def generar_reporte_mensual():
    """
    Tarea que genera un reporte mensual de reservas y estadísticas de la clínica.
    Retorna la ruta del archivo generado.
    """
    try:
        logger.info("[REPORTE] Iniciando generación de reporte mensual...")
        
        # Obtener datos del mes actual
        ahora = timezone.now()
        primer_dia = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ultimo_dia = (primer_dia + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Estadísticas
        reservas_mes = Reserva.objects.filter(
            fecha_hora__range=[primer_dia, ultimo_dia]
        )
        reservas_confirmadas = reservas_mes.filter(estado='confirmada').count()
        reservas_completadas = reservas_mes.filter(estado='completada').count()
        reservas_canceladas = reservas_mes.filter(estado='cancelada').count()
        reservas_pendientes = reservas_mes.filter(estado='pendiente').count()
        total_reservas = reservas_mes.count()
        
        total_doctores = Doctor.objects.filter(disponible=True).count()
        total_pacientes = Paciente.objects.count()
        
        # Crear PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=8
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.textColor = colors.HexColor('#333333')
        
        # Contenido
        story = []
        
        # Encabezado
        story.append(Paragraph("CLÍNICA MEDICAL RESERVA", title_style))
        story.append(Paragraph(f"Reporte Mensual de Reservas - {ahora.strftime('%B de %Y')}", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fecha de generación
        story.append(Paragraph(f"<b>Fecha de Generación:</b> {ahora.strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Sección de estadísticas generales
        story.append(Paragraph("ESTADÍSTICAS GENERALES", heading_style))
        
        general_data = [
            ['Concepto', 'Cantidad'],
            ['Total de Reservas', str(total_reservas)],
            ['Doctores Disponibles', str(total_doctores)],
            ['Pacientes Registrados', str(total_pacientes)],
        ]
        
        general_table = Table(general_data, colWidths=[3.5*inch, 1.5*inch])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        story.append(general_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Sección de estadísticas de reservas
        story.append(Paragraph("ANÁLISIS DE RESERVAS", heading_style))
        
        reservas_data = [
            ['Estado', 'Cantidad'],
            ['Confirmadas', str(reservas_confirmadas)],
            ['Completadas', str(reservas_completadas)],
            ['Pendientes', str(reservas_pendientes)],
            ['Canceladas', str(reservas_canceladas)],
        ]
        
        reservas_table = Table(reservas_data, colWidths=[3.5*inch, 1.5*inch])
        reservas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#009900')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        story.append(reservas_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Detalle de reservas
        if total_reservas > 0:
            story.append(Paragraph("DETALLE DE RESERVAS DEL MES", heading_style))
            
            detalle_data = [
                ['#', 'Paciente', 'Doctor', 'Fecha', 'Estado']
            ]
            
            for idx, reserva in enumerate(reservas_mes.order_by('-fecha_hora')[:20], 1):
                detalle_data.append([
                    str(idx),
                    reserva.paciente.usuario.get_full_name(),
                    reserva.doctor.nombre,
                    reserva.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                    reserva.estado.upper()
                ])
            
            detalle_table = Table(detalle_data, colWidths=[0.5*inch, 1.8*inch, 1.5*inch, 1.2*inch, 1*inch])
            detalle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            
            story.append(detalle_table)
        
        # Pie de página
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "<i>Este es un reporte confidencial generado automáticamente por el sistema Medical Reserva.</i>",
            styles['Normal']
        ))
        
        # Generar PDF
        doc.build(story)
        
        # Obtener contenido del buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Crear nombre de archivo
        filename = f"reporte_reservas_{ahora.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        
        # Crear directorio si no existe
        os.makedirs('temp', exist_ok=True)
        
        # Guardar archivo
        with open(filepath, 'wb') as f:
            f.write(pdf_content)
        
        logger.info(f"[REPORTE] Reporte generado exitosamente: {filepath}")
        
        return {
            'status': 'success',
            'filename': filename,
            'filepath': filepath,
            'total_reservas': total_reservas,
            'message': 'Reporte generado exitosamente'
        }
    
    except Exception as exc:
        logger.error(f"Error al generar reporte mensual: {exc}")
        return {
            'status': 'error',
            'message': str(exc)
        }