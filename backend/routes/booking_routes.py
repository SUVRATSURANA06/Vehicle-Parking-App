from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.parking_spot import ParkingSpot
from models.booking import Booking
from datetime import datetime, timedelta

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    spots = ParkingSpot.query.filter_by(is_available=True).all()

    if request.method == 'POST':
        spot_id = request.form['spot_id']
        end_time = datetime.utcnow() + timedelta(hours=1)

        booking = Booking(user_id=current_user.id, parking_spot_id=spot_id, end_time=end_time)
        db.session.add(booking)

        spot = ParkingSpot.query.get(spot_id)
        spot.is_available = False

        db.session.commit()
        return redirect(url_for('main.dashboard'))

    return render_template('booking.html', spots=spots)
