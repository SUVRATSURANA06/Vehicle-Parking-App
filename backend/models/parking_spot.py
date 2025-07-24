from extensions import db
from datetime import datetime

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A-available, O-occupied
    spot_number = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with reservations
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status,
            'spot_number': self.spot_number,
            'is_available': self.status == 'A',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
