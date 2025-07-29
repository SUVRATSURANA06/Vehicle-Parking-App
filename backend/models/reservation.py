from extensions import db
from datetime import datetime

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vehicle_number = db.Column(db.String(20))
    parked_in_time = db.Column(db.DateTime)
    released_time = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Reservation {self.id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_number': self.vehicle_number,
            'parking_timestamp': self.parking_timestamp.isoformat() + 'Z' if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() + 'Z' if self.leaving_timestamp else None,
            'parked_in_time': self.parked_in_time.isoformat() + 'Z' if self.parked_in_time else None,
            'released_time': self.released_time.isoformat() + 'Z' if self.released_time else None,
            'parking_cost': self.parking_cost,
            'total_cost': self.total_cost,
            'status': self.status,
            'duration_hours': self.calculate_duration(),
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
    
    def calculate_duration(self):
        """Calculate parking duration in hours"""
        if not self.parking_timestamp:
            return 0
        
        end_time = self.leaving_timestamp or datetime.utcnow()
        duration = end_time - self.parking_timestamp
        return round(duration.total_seconds() / 3600, 2)
    
    def calculate_cost(self, hourly_rate):
        """Calculate parking cost based on duration and hourly rate"""
        duration = self.calculate_duration()
        self.parking_cost = duration * hourly_rate
        return self.parking_cost 