from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from extensions import db, redis_client
from models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
from functools import wraps
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Access denied. Admin privileges required.'}), 403
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function

# All protected routes now use @login_required and @admin_required

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard data"""
    # Get cached statistics or calculate them
    stats_cache_key = "admin_stats"
    cached_stats = redis_client.get(stats_cache_key) if redis_client else None
    
    if cached_stats:
        stats = json.loads(cached_stats)
    else:
        # Calculate statistics
        total_users = User.query.filter_by(is_admin=False).count()
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        
        # Revenue calculations
        today = datetime.utcnow().date()
        today_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(
            db.func.date(Reservation.created_at) == today
        ).scalar() or 0
        
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(
            Reservation.created_at >= month_start
        ).scalar() or 0
        
        stats = {
            'total_users': total_users,
            'total_lots': total_lots,
            'total_spots': total_spots,
            'available_spots': available_spots,
            'active_reservations': active_reservations,
            'today_revenue': float(today_revenue),
            'month_revenue': float(month_revenue)
        }
        
        # Cache for 5 minutes
        if redis_client:
            redis_client.setex(stats_cache_key, 300, json.dumps(stats))
    
    return jsonify(stats)

@admin_bp.route('/parking-lots')
@login_required
@admin_required
def parking_lots():
    """Get all parking lots, with optional filters: location, user_id, spot"""
    location = request.args.get('location')
    user_id = request.args.get('user_id', type=int)
    spot = request.args.get('spot')
    query = ParkingLot.query
    if location:
        # Filter by address or pin_code (case-insensitive)
        query = query.filter(
            (ParkingLot.address.ilike(f"%{location}%")) |
            (ParkingLot.pin_code.ilike(f"%{location}%")) |
            (ParkingLot.name.ilike(f"%{location}%"))
        )
    if user_id:
        # Filter lots where user has a reservation
        lot_ids = db.session.query(ParkingSpot.lot_id).join(Reservation).filter(Reservation.user_id == user_id).distinct()
        query = query.filter(ParkingLot.id.in_(lot_ids))
    if spot:
        # Filter lots containing a spot with given spot_number (case-insensitive)
        lot_ids = db.session.query(ParkingSpot.lot_id).filter(ParkingSpot.spot_number.ilike(f"%{spot}%")).distinct()
        query = query.filter(ParkingLot.id.in_(lot_ids))
    lots = query.all()
    # For each lot, include parking_spots (id, status, spot_number) for frontend grid
    def lot_with_spots(lot):
        d = lot.to_dict()
        d['parking_spots'] = [
            {'id': s.id, 'status': s.status, 'spot_number': s.spot_number}
            for s in lot.parking_spots
        ]
        return d
    return jsonify([lot_with_spots(lot) for lot in lots])

@admin_bp.route('/parking-lots/create', methods=['POST'])
@login_required
@admin_required
def create_parking_lot():
    """Create a new parking lot"""
    try:
        data = request.get_json()
        lot = ParkingLot(
            name=data['name'],
            price=float(data['price']),
            address=data['address'],
            pin_code=data['pin_code'],
            number_of_spots=int(data['number_of_spots'])
        )
        db.session.add(lot)
        db.session.commit()
        
        # Create parking spots for this lot
        for i in range(lot.number_of_spots):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f"{lot.name}-{i+1:03d}",
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking lot created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/parking-lots/<int:lot_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_parking_lot(lot_id):
    """Edit a parking lot"""
    lot = ParkingLot.query.get_or_404(lot_id)
    
    try:
        data = request.get_json()
        lot.name = data['name']
        lot.price = float(data['price'])
        lot.address = data['address']
        lot.pin_code = data['pin_code']
        
        # Handle spot number changes
        new_spot_count = int(data['number_of_spots'])
        current_spot_count = len(lot.parking_spots)
        
        if new_spot_count > current_spot_count:
            # Add more spots
            for i in range(current_spot_count, new_spot_count):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"{lot.name}-{i+1:03d}",
                    status='A'
                )
                db.session.add(spot)
        elif new_spot_count < current_spot_count:
            # Remove excess spots (only if not occupied)
            spots_to_remove = lot.parking_spots[new_spot_count:]
            for spot in spots_to_remove:
                if spot.status == 'A':  # Only remove available spots
                    db.session.delete(spot)
        
        lot.number_of_spots = new_spot_count
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking lot updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/parking-lots/<int:lot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_parking_lot(lot_id):
    """Delete a parking lot"""
    lot = ParkingLot.query.get_or_404(lot_id)
    
    try:
        # Check if any spots are occupied
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
        if occupied_spots > 0:
            return jsonify({'success': False, 'message': f'Cannot delete lot with {occupied_spots} occupied spots'})
        
        db.session.delete(lot)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking lot deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Get all users"""
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([user.to_dict() for user in users])

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        return jsonify({'success': True, 'message': f'User {status} successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Get analytics data"""
    # Get analytics data
    cache_key = "admin_analytics"
    cached_data = redis_client.get(cache_key) if redis_client else None
    
    if cached_data:
        analytics_data = json.loads(cached_data)
    else:
        # Calculate analytics
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Monthly reservations
        monthly_reservations = Reservation.query.filter(
            Reservation.created_at >= month_start
        ).count()
        
        # Revenue by lot
        lots = ParkingLot.query.all()
        lot_revenue = {}
        for lot in lots:
            revenue = db.session.query(db.func.sum(Reservation.parking_cost)).join(
                ParkingSpot, Reservation.spot_id == ParkingSpot.id
            ).filter(
                ParkingSpot.lot_id == lot.id,
                Reservation.created_at >= month_start
            ).scalar() or 0
            lot_revenue[lot.name] = float(revenue)
        
        # User activity
        active_users = User.query.filter(
            User.last_login >= month_start,
            User.is_admin == False
        ).count()
        
        analytics_data = {
            'monthly_reservations': monthly_reservations,
            'lot_revenue': lot_revenue,
            'active_users': active_users,
            'generated_at': now.isoformat()
        }
        
        # Cache for 10 minutes
        if redis_client:
            redis_client.setex(cache_key, 600, json.dumps(analytics_data))
    
    return jsonify(analytics_data)

@admin_bp.route('/reports/generate-monthly', methods=['POST'])
@login_required
@admin_required
def generate_monthly_report():
    """Trigger monthly report generation"""
    from tasks import generate_monthly_report
    
    try:
        task = generate_monthly_report.delay()
        return jsonify({'success': True, 'message': 'Monthly report generation started', 'task_id': task.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/reports/status/<task_id>')
@login_required
@admin_required
def report_status(task_id):
    """Check report generation status"""
    from tasks import generate_monthly_report
    
    task = generate_monthly_report.AsyncResult(task_id)
    if task.ready():
        return jsonify({'status': 'completed', 'result': task.result})
    else:
        return jsonify({'status': 'pending'})

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats_cache_key = "admin_stats"
    cached_stats = redis_client.get(stats_cache_key) if redis_client else None
    
    if cached_stats:
        return jsonify(json.loads(cached_stats))
    else:
        # Recalculate and return
        total_users = User.query.filter_by(is_admin=False).count()
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        
        stats = {
            'total_users': total_users,
            'total_lots': total_lots,
            'total_spots': total_spots,
            'available_spots': available_spots,
            'active_reservations': active_reservations
        }
        
        return jsonify(stats)

# --- Parking Spot Management ---
@admin_bp.route('/parking-spots', methods=['GET'])
@login_required
@admin_required
def get_parking_spots():
    """View all parking spots, with optional filters for lot and status"""
    lot_id = request.args.get('lot_id', type=int)
    status = request.args.get('status')
    query = ParkingSpot.query
    if lot_id:
        query = query.filter_by(lot_id=lot_id)
    if status:
        query = query.filter_by(status=status)
    spots = query.all()
    
    # Include lot information for each spot
    result = []
    for spot in spots:
        spot_data = spot.to_dict()
        spot_data['lot_name'] = spot.parking_lot.name if spot.parking_lot else None
        result.append(spot_data)
    
    return jsonify(result)

@admin_bp.route('/parking-spots/add', methods=['POST'])
@login_required
@admin_required
def add_parking_spot():
    """Add a new parking spot to a lot"""
    try:
        data = request.get_json()
        lot_id = data['lot_id']
        spot_number = data['spot_number']
        status = data.get('status', 'A')
        
        # Validate lot exists
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'success': False, 'message': 'Parking lot not found'})
        
        # Check if spot number already exists in this lot
        existing_spot = ParkingSpot.query.filter_by(lot_id=lot_id, spot_number=spot_number).first()
        if existing_spot:
            return jsonify({'success': False, 'message': 'Spot number already exists in this lot'})
        
        spot = ParkingSpot(lot_id=lot_id, spot_number=spot_number, status=status)
        db.session.add(spot)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking spot added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/parking-spots/<int:spot_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_parking_spot(spot_id):
    """Edit a parking spot's number or status"""
    spot = ParkingSpot.query.get_or_404(spot_id)
    try:
        data = request.get_json()
        new_spot_number = data.get('spot_number')
        new_status = data.get('status')
        
        # Check if new spot number conflicts with existing spot in same lot
        if new_spot_number and new_spot_number != spot.spot_number:
            existing_spot = ParkingSpot.query.filter_by(
                lot_id=spot.lot_id, 
                spot_number=new_spot_number
            ).first()
            if existing_spot:
                return jsonify({'success': False, 'message': 'Spot number already exists in this lot'})
        
        # Update spot
        if new_spot_number:
            spot.spot_number = new_spot_number
        if new_status:
            spot.status = new_status
        
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking spot updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/parking-spots/<int:spot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_parking_spot(spot_id):
    """Delete a parking spot (only if not occupied)"""
    spot = ParkingSpot.query.get_or_404(spot_id)
    try:
        # Check if spot is occupied
        if spot.status == 'O':
            return jsonify({'success': False, 'message': 'Cannot delete an occupied spot. Please wait for the user to release it.'})
        
        # Check if spot has active reservation
        active_reservation = Reservation.query.filter_by(spot_id=spot.id, status='active').first()
        if active_reservation:
            return jsonify({'success': False, 'message': 'Cannot delete spot with active reservation'})
        
        db.session.delete(spot)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': 'Parking spot deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# --- Booking Management ---
@admin_bp.route('/bookings', methods=['GET'])
@login_required
@admin_required
def get_bookings():
    """View all bookings with optional filters"""
    lot_id = request.args.get('lot_id', type=int)
    user_id = request.args.get('user_id', type=int)
    spot_id = request.args.get('spot_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Reservation.query
    
    if lot_id:
        query = query.join(ParkingSpot).filter(ParkingSpot.lot_id == lot_id)
    if user_id:
        query = query.filter(Reservation.user_id == user_id)
    if spot_id:
        query = query.filter(Reservation.spot_id == spot_id)
    if status:
        query = query.filter(Reservation.status == status)
    if date_from:
        query = query.filter(Reservation.created_at >= date_from)
    if date_to:
        query = query.filter(Reservation.created_at <= date_to)
    
    bookings = query.order_by(Reservation.created_at.desc()).all()
    
    # Include user and spot details
    result = []
    for booking in bookings:
        booking_data = booking.to_dict()
        booking_data['user'] = booking.user.to_dict() if booking.user else None
        booking_data['spot'] = booking.parking_spot.to_dict() if booking.parking_spot else None
        booking_data['lot'] = booking.parking_spot.parking_lot.to_dict() if booking.parking_spot and booking.parking_spot.parking_lot else None
        result.append(booking_data)
    
    return jsonify(result)

@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_booking(booking_id):
    """Admin can cancel any booking"""
    booking = Reservation.query.get_or_404(booking_id)
    try:
        booking.status = 'cancelled'
        booking.leaving_timestamp = datetime.utcnow()
        
        # Free up the spot
        if booking.parking_spot:
            booking.parking_spot.status = 'A'
        
        db.session.commit()
        if redis_client:
            redis_client.delete("admin_stats")
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/spot/<int:spot_id>/reservation')
@login_required
@admin_required
def get_spot_reservation(spot_id):
    """Get reservation details for a specific spot"""
    try:
        # Get the spot
        spot = ParkingSpot.query.get_or_404(spot_id)
        
        # Get active reservation for this spot
        reservation = Reservation.query.filter_by(spot_id=spot_id, status='active').first()
        
        if reservation:
            # Include user and lot details
            reservation_data = reservation.to_dict()
            reservation_data['user'] = reservation.user.to_dict() if reservation.user else None
            reservation_data['spot'] = reservation.parking_spot.to_dict() if reservation.parking_spot else None
            reservation_data['lot'] = reservation.parking_spot.parking_lot.to_dict() if reservation.parking_spot and reservation.parking_spot.parking_lot else None
            
            return jsonify({
                'success': True,
                'reservation': reservation_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No active reservation found for this spot'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- PDF Download ---
@admin_bp.route('/reports/download/<filename>')
@login_required
@admin_required
def download_report(filename):
    """Download generated PDF report"""
    from flask import send_from_directory
    import os
    
    reports_dir = os.path.join('static', 'reports')
    if os.path.exists(os.path.join(reports_dir, filename)):
        return send_from_directory(reports_dir, filename, as_attachment=True)
    else:
        return jsonify({'success': False, 'message': 'Report file not found'}), 404

@admin_bp.route('/reports/list')
@login_required
@admin_required
def list_reports():
    """List all available reports"""
    import os
    import glob
    
    reports_dir = os.path.join('static', 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
    
    report_files = glob.glob(os.path.join(reports_dir, '*.pdf'))
    reports = []
    
    for file_path in report_files:
        filename = os.path.basename(file_path)
        file_stats = os.stat(file_path)
        reports.append({
            'filename': filename,
            'size': file_stats.st_size,
            'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'download_url': f'/admin/reports/download/{filename}'
        })
    
    return jsonify(reports)

# --- Spot Status Override ---
@admin_bp.route('/parking-spots/<int:spot_id>/override-status', methods=['POST'])
@login_required
@admin_required
def override_spot_status(spot_id):
    """Admin can override spot status (force available/occupied)"""
    spot = ParkingSpot.query.get_or_404(spot_id)
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['A', 'O']:
            return jsonify({'success': False, 'message': 'Invalid status. Use A (Available) or O (Occupied)'})
        
        # If making spot occupied, check if it has active reservation
        if new_status == 'O' and spot.status == 'A':
            active_reservation = Reservation.query.filter_by(spot_id=spot.id, status='active').first()
            if active_reservation:
                return jsonify({'success': False, 'message': 'Spot has active reservation. Cannot force occupied.'})
        
        spot.status = new_status
        db.session.commit()
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({'success': True, 'message': f'Spot status changed to {"Available" if new_status == "A" else "Occupied"}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 