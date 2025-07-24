from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from extensions import db, redis_client
from models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
from functools import wraps

import json

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin:
            return jsonify({'success': False, 'message': 'Access denied. User privileges required.'}), 403
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function

# All protected routes now use @login_required and @user_required

@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    """User dashboard data"""
    user = g.current_user
    # Get user's active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=user.id, 
        status='active'
    ).first()
    
    # Get user's recent reservations
    recent_reservations = Reservation.query.filter_by(
        user_id=user.id
    ).order_by(Reservation.created_at.desc()).limit(5).all()

    def reservation_with_nested(r):
        d = r.to_dict()
        d['spot'] = r.parking_spot.to_dict() if r.parking_spot else None
        d['lot'] = r.parking_spot.parking_lot.to_dict() if r.parking_spot and r.parking_spot.parking_lot else None
        return d
    
    # Get parking statistics
    total_reservations = Reservation.query.filter_by(user_id=user.id).count()
    # Sum total_cost if available, else parking_cost
    total_spent = db.session.query(db.func.sum(
        db.case(
            [(Reservation.total_cost != None, Reservation.total_cost)],
            else_=Reservation.parking_cost
        )
    )).filter_by(user_id=user.id).scalar() or 0
    
    # Get available parking lots
    lots = ParkingLot.query.all()
    lot_availability = {}
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(
            lot_id=lot.id, 
            status='A'
        ).count()
        lot_availability[lot.id] = available_spots
    
    return jsonify({
        'active_reservation': active_reservation.to_dict() if active_reservation else None,
        'recent_reservations': [reservation_with_nested(r) for r in recent_reservations],
        'total_reservations': total_reservations,
        'total_spent': float(total_spent),
        'lots': [lot.to_dict() for lot in lots],
        'lot_availability': lot_availability
    })

@user_bp.route('/parking-lots')
@login_required
@user_required
def parking_lots():
    """Get available parking lots"""
    lots = ParkingLot.query.all()
    
    # Get availability for each lot
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(
            lot_id=lot.id, 
            status='A'
        ).count()
        lot.available_spots = available_spots
        lot.occupied_spots = lot.number_of_spots - available_spots
    
    return jsonify([lot.to_dict() for lot in lots])

@user_bp.route('/reserve/<int:lot_id>', methods=['POST'])
@login_required
@user_required
def reserve_spot(lot_id):
    """Reserve a parking spot (user selects spot and provides vehicle number)"""
    lot = ParkingLot.query.get_or_404(lot_id)
    user = g.current_user
    active_reservation = Reservation.query.filter_by(user_id=user.id, status='active').first()
    if active_reservation:
        return jsonify({'success': False, 'message': 'You already have an active parking reservation.'})
    try:
        data = request.get_json()
        spot_id = data.get('spot_id')
        vehicle_number = data.get('vehicle_number')
        
        if not spot_id or not vehicle_number:
            return jsonify({'success': False, 'message': 'Spot ID and vehicle number are required.'})
        
        # Validate spot exists and is available
        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id, status='A').first()
        if not spot:
            return jsonify({'success': False, 'message': 'Selected spot is not available or does not exist.'})
        
        # Check if spot is still available (double-check)
        if spot.status != 'A':
            return jsonify({'success': False, 'message': 'Selected spot is no longer available.'})
        
        # Create reservation with slot_id (spot_id)
        reservation = Reservation(
            spot_id=spot.id,  # This is the slot_id
            user_id=user.id,
            vehicle_number=vehicle_number,
            parking_timestamp=datetime.utcnow(),
            status='active'
        )
        
        # Mark spot as occupied
        spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        
        return jsonify({
            'success': True, 
            'message': 'Parking spot reserved successfully!',
            'reservation': {
                'id': reservation.id,
                'slot_id': reservation.spot_id,
                'vehicle_number': reservation.vehicle_number,
                'parking_timestamp': reservation.parking_timestamp.isoformat(),
                'lot_name': lot.name,
                'spot_number': spot.spot_number
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/parked-in/<int:reservation_id>', methods=['POST'])
@login_required
@user_required
def parked_in(reservation_id):
    """Mark reservation as Parked In (record entry time)"""
    user = g.current_user
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    if reservation.parked_in_time:
        return jsonify({'success': False, 'message': 'Already marked as Parked In'})
    reservation.parked_in_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Parked In time recorded', 'parked_in_time': reservation.parked_in_time.isoformat()})

@user_bp.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
@user_required
def release_reservation(reservation_id):
    """Mark reservation as Released (record exit time, calculate cost, free spot)"""
    user = g.current_user
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    if not reservation.parked_in_time and not reservation.parking_timestamp:
        return jsonify({'success': False, 'message': 'You must Park In before releasing.'})
    if reservation.released_time:
        return jsonify({'success': False, 'message': 'Already released.'})
    now = datetime.utcnow()
    reservation.released_time = now
    reservation.leaving_timestamp = now  # Ensure both fields are set
    # Use parked_in_time if available, else fallback to parking_timestamp
    start_time = reservation.parked_in_time or reservation.parking_timestamp
    if not reservation.parked_in_time:
        print(f"[WARNING] parked_in_time missing for reservation {reservation.id}, using parking_timestamp for cost calculation.")
    
    # Debug logging for cost calculation
    duration_seconds = (reservation.released_time - start_time).total_seconds()
    duration_hours = duration_seconds / 3600
    duration_minutes = duration_seconds / 60
    hourly_rate = reservation.parking_spot.parking_lot.price
    total_cost = round(duration_hours * hourly_rate, 2)
    
    print(f"[DEBUG] Cost calculation for reservation {reservation.id}:")
    print(f"  Start time: {start_time}")
    print(f"  End time: {reservation.released_time}")
    print(f"  Duration: {duration_seconds} seconds = {duration_hours:.2f} hours = {duration_minutes:.2f} minutes")
    print(f"  Hourly rate: ₹{hourly_rate}")
    print(f"  Total cost: ₹{total_cost}")
    
    reservation.total_cost = total_cost
    reservation.parking_cost = total_cost  # Ensure both fields are set
    reservation.status = 'completed'
    # Free up the spot
    reservation.parking_spot.status = 'A'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Parking session released', 'duration': round(duration_hours, 2), 'total_cost': total_cost})

@user_bp.route('/end-session', methods=['POST'])
@login_required
@user_required
def end_session():
    """End current parking session"""
    user = g.current_user
    try:
        active_reservation = Reservation.query.filter_by(
            user_id=user.id, 
            status='active'
        ).first()
        if not active_reservation:
            return jsonify({'success': False, 'message': 'No active reservation found'})
        # Use parked_in_time if available, else fallback to parking_timestamp
        start_time = active_reservation.parked_in_time or active_reservation.parking_timestamp
        if not active_reservation.parked_in_time:
            print(f"[WARNING] parked_in_time missing for reservation {active_reservation.id}, using parking_timestamp for cost calculation.")
        end_time = datetime.utcnow()
        
        # Debug logging for cost calculation
        duration_seconds = (end_time - start_time).total_seconds()
        duration_hours = duration_seconds / 3600
        duration_minutes = duration_seconds / 60
        hourly_rate = active_reservation.parking_spot.parking_lot.price
        cost = round(duration_hours * hourly_rate, 2)
        
        print(f"[DEBUG] Cost calculation for reservation {active_reservation.id}:")
        print(f"  Start time: {start_time}")
        print(f"  End time: {end_time}")
        print(f"  Duration: {duration_seconds} seconds = {duration_hours:.2f} hours = {duration_minutes:.2f} minutes")
        print(f"  Hourly rate: ₹{hourly_rate}")
        print(f"  Total cost: ₹{cost}")
        
        # Update reservation
        active_reservation.leaving_timestamp = end_time
        active_reservation.released_time = end_time  # Ensure both fields are set
        active_reservation.parking_cost = cost
        active_reservation.total_cost = cost  # Ensure both fields are set
        active_reservation.status = 'completed'
        # Free up the spot
        active_reservation.parking_spot.status = 'A'
        db.session.commit()
        # Clear cache
        if redis_client:
            redis_client.delete("admin_stats")
        return jsonify({
            'success': True, 
            'message': 'Parking session ended successfully',
            'duration': round(duration_hours, 2),
            'cost': cost
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/history')
@login_required
@user_required
def history():
    """Get parking history with filters and sorting"""
    user = g.current_user
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=str)
    sort = request.args.get('sort', 'created_at', type=str)
    order = request.args.get('order', 'desc', type=str)

    query = Reservation.query.filter_by(user_id=user.id)
    if status:
        query = query.filter_by(status=status)
    # Only allow sorting by certain fields
    allowed_sorts = {'created_at', 'parking_timestamp', 'parking_cost'}
    sort_field = sort if sort in allowed_sorts else 'created_at'
    sort_col = getattr(Reservation, sort_field)
    if order == 'asc':
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    reservations = query.paginate(page=page, per_page=10, error_out=False)
    def reservation_with_nested(r):
        d = r.to_dict()
        d['spot'] = r.parking_spot.to_dict() if r.parking_spot else None
        d['lot'] = r.parking_spot.parking_lot.to_dict() if r.parking_spot and r.parking_spot.parking_lot else None
        return d
    return jsonify({
        'items': [reservation_with_nested(r) for r in reservations.items],
        'total': reservations.total,
        'pages': reservations.pages,
        'current_page': reservations.page
    })

@user_bp.route('/export-csv', methods=['POST'])
@login_required
@user_required
def export_csv():
    """Export user's parking history to CSV"""
    user = g.current_user
    try:
        # Get user's reservations
        reservations = Reservation.query.filter_by(user_id=user.id).all()
        
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
        
        # Create DataFrame and export to CSV
        import pandas as pd
        import os
        from datetime import datetime
        
        df = pd.DataFrame(data)
        csv_filename = f"user_{user.id}_parking_history_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join('static', 'exports', csv_filename)
        
        # Ensure exports directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        df.to_csv(csv_path, index=False)

        print(f"CSV export completed: {csv_filename} with {len(data)} records")
        print(f"File saved to: {csv_path}")
        print(f"Download URL: /user/download-csv/{csv_filename}")

        # Send email with CSV attachment
        from flask_mail import Message
        from extensions import mail
        with open(csv_path, 'rb') as f:
            msg = Message(
                subject="Your Parking History Report",
                recipients=[user.email],
                body="Attached is your parking history report as requested."
            )
            msg.attach(csv_filename, "text/csv", f.read())
            mail.send(msg)
        
        return jsonify({
            'success': True, 
            'message': f'CSV export completed successfully with {len(data)} records.',
            'filename': csv_filename,
            'download_url': f'/user/download-csv/{csv_filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/export-status/<task_id>')
@login_required
@user_required
def export_status(task_id):
    """Check CSV export status"""
    task = export_user_data_csv.AsyncResult(task_id)
    if task.ready():
        result = task.result
        if 'completed' in result:
            # Extract filename from result
            filename = result.split(': ')[-1]
            return jsonify({
                'status': 'completed', 
                'filename': filename,
                'download_url': f'/user/download-csv/{filename}'
            })
        else:
            return jsonify({'status': 'error', 'message': result})
    else:
        return jsonify({'status': 'pending'})

@user_bp.route('/profile')
@login_required
@user_required
def profile():
    """Get user profile"""
    user = g.current_user
    return jsonify(user.to_dict())

@user_bp.route('/profile/edit', methods=['POST'])
@login_required
@user_required
def edit_profile():
    """Edit user profile"""
    user = g.current_user
    try:
        data = request.get_json()
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.phone = data.get('phone', '')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/api/active-reservation')
@login_required
@user_required
def api_active_reservation():
    """API endpoint for active reservation"""
    user = g.current_user
    active_reservation = Reservation.query.filter_by(
        user_id=user.id, 
        status='active'
    ).first()
    
    if active_reservation:
        return jsonify(active_reservation.to_dict())
    else:
        return jsonify(None)

@user_bp.route('/api/parking-stats')
@login_required
@user_required
def api_parking_stats():
    """API endpoint for user parking statistics"""
    user = g.current_user
    total_reservations = Reservation.query.filter_by(user_id=user.id).count()
    # Sum total_cost if available, else parking_cost
    total_spent = db.session.query(db.func.sum(
        db.case(
            [(Reservation.total_cost != None, Reservation.total_cost)],
            else_=Reservation.parking_cost
        )
    )).filter_by(user_id=user.id).scalar() or 0
    # This month's reservations
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.created_at >= month_start
    ).count()
    stats = {
        'total_reservations': total_reservations,
        'total_spent': float(total_spent),
        'this_month': this_month
    }
    return jsonify(stats)

@user_bp.route('/available-spots/<int:lot_id>')
@login_required
@user_required
def available_spots(lot_id):
    """Get available spots for a lot"""
    user = g.current_user
    spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').all()
    return jsonify([spot.to_dict() for spot in spots])

@user_bp.route('/download-csv/<filename>')
@login_required
@user_required
def download_csv(filename):
    """Download generated CSV file"""
    from flask import send_from_directory
    import os
    
    exports_dir = os.path.join('static', 'exports')
    file_path = os.path.join(exports_dir, filename)
    print(f"Download request for: {filename}")
    print(f"Looking for file at: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        return send_from_directory(exports_dir, filename, as_attachment=True)
    else:
        return jsonify({'success': False, 'message': 'CSV file not found'}), 404 