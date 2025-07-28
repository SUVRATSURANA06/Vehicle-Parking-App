from celery import Celery
from extensions import celery, redis_client, db
from models import User, Reservation, ParkingLot
from datetime import datetime, timedelta
import pandas as pd
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# Configure Celery
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task
def send_daily_reminders():
    """Send daily reminders to inactive users"""
    try:
        # Find users who haven't logged in for 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        inactive_users = User.query.filter(
            User.last_login < week_ago,
            User.is_active == True,
            User.is_admin == False
        ).all()
        
        for user in inactive_users:
            # Store reminder in Redis
            reminder_key = f"reminder:{user.id}:{datetime.utcnow().date()}"
            redis_client.setex(reminder_key, 86400, "sent")  # 24 hours
            
        return f"Sent reminders to {len(inactive_users)} inactive users"
    except Exception as e:
        return f"Error sending reminders: {str(e)}"

@celery.task
def generate_monthly_report():
    """Generate monthly activity report in PDF format"""
    try:
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_reservations = Reservation.query.filter(
            Reservation.created_at >= start_of_month
        ).count()
        
        total_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(
            Reservation.created_at >= start_of_month
        ).scalar() or 0
        
        active_users = User.query.filter(
            User.last_login >= start_of_month,
            User.is_admin == False
        ).count()
        
        # PDF report
        report_filename = f"monthly_report_{now.strftime('%Y_%m')}.pdf"
        report_path = os.path.join('static', 'reports', report_filename)
        
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        
        title = Paragraph(f"Monthly Parking Report - {now.strftime('%B %Y')}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        
        data = [
            ['Metric', 'Value'],
            ['Total Reservations', str(total_reservations)],
            ['Total Revenue', f"${total_revenue:.2f}"],
            ['Active Users', str(active_users)],
            ['Report Generated', now.strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        
        report_info = {
            'filename': report_filename,
            'path': report_path,
            'generated_at': now.isoformat(),
            'total_reservations': total_reservations,
            'total_revenue': total_revenue,
            'active_users': active_users
        }
        redis_client.setex(f"monthly_report:{now.strftime('%Y_%m')}", 2592000, json.dumps(report_info))  # 30 days
        
        return f"Monthly report generated: {report_filename}"
    except Exception as e:
        return f"Error generating monthly report: {str(e)}"

@celery.task
def export_user_data_csv(user_id):
    """Export user's parking history to CSV"""
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"
        
        
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        # Prepare data for CSV
        data = []
        for reservation in reservations:
            spot = reservation.parking_spot
            lot = spot.parking_lot if spot else None
            
            data.append({
                'Reservation ID': reservation.id,
                'Parking Lot': lot.name if lot else 'N/A',
                'Spot Number': spot.spot_number if spot else 'N/A',
                'Vehicle Number': reservation.vehicle_number or 'N/A',
                'Start Time': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.parking_timestamp else 'N/A',
                'End Time': reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.leaving_timestamp else 'N/A',
                'Duration (Hours)': reservation.calculate_duration(),
                'Cost (₹)': f"₹{reservation.parking_cost:.2f}" if reservation.parking_cost else '₹0.00',
                'Status': reservation.status,
                'Created': reservation.created_at.strftime('%Y-%m-%d %H:%M:%S') if reservation.created_at else 'N/A'
            })
        
        
        df = pd.DataFrame(data)
        csv_filename = f"user_{user_id}_parking_history_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join('static', 'exports', csv_filename)
        
        
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        df.to_csv(csv_path, index=False)
        
        print(f"CSV export completed: {csv_filename} with {len(data)} records")
        
        # Store export info in Redis
        export_info = {
            'filename': csv_filename,
            'path': csv_path,
            'user_id': user_id,
            'generated_at': datetime.utcnow().isoformat(),
            'record_count': len(data)
        }
        redis_client.setex(f"csv_export:{user_id}:{datetime.utcnow().strftime('%Y%m%d')}", 86400, json.dumps(export_info))  # 24 hours
        
        return f"CSV export completed: {csv_filename}"
    except Exception as e:
        print(f"Error exporting CSV: {str(e)}")
        return f"Error exporting CSV: {str(e)}"

@celery.task
def cleanup_old_data():
    """Clean up old data and cache entries"""
    try:
        # Clean up old reservations (older than 1 year)
        year_ago = datetime.utcnow() - timedelta(days=365)
        old_reservations = Reservation.query.filter(
            Reservation.created_at < year_ago,
            Reservation.status.in_(['completed', 'cancelled'])
        ).delete()
        
        
        keys_to_delete = []
        for key in redis_client.keys("reminder:*"):
            if redis_client.ttl(key) < 0:  # Expired keys
                keys_to_delete.append(key)
        
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
        
        return f"Cleanup completed: {old_reservations} old reservations deleted, {len(keys_to_delete)} cache entries cleaned"
    except Exception as e:
        return f"Error during cleanup: {str(e)}" 