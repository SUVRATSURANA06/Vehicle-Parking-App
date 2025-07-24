from app import create_app
from extensions import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()

        # Check if parking lots already exist
        if ParkingLot.query.first() is None:
            # Demo parking lots and their spot distributions
            demo_lots = [
                {
                    'name': 'Central Mall Parking',
                    'price': 30,
                    'address': '123 Main St, Downtown',
                    'pin_code': '400001',
                    'number_of_spots': 10,
                    'available': 10,
                    'occupied': 0
                },
                {
                    'name': 'Airport Lot A',
                    'price': 50,
                    'address': 'Airport Road, Terminal 1',
                    'pin_code': '400099',
                    'number_of_spots': 20,
                    'available': 20,
                    'occupied': 0
                },
                {
                    'name': 'Tech Park Basement',
                    'price': 25,
                    'address': 'IT Park, Block B',
                    'pin_code': '400076',
                    'number_of_spots': 15,
                    'available': 15,
                    'occupied': 0
                }
            ]

            for lot_data in demo_lots:
                lot = ParkingLot(
                    name=lot_data['name'],
                    price=lot_data['price'],
                    address=lot_data['address'],
                    pin_code=lot_data['pin_code'],
                    number_of_spots=lot_data['number_of_spots']
                )
                db.session.add(lot)
                db.session.flush()  # Get lot.id before adding spots
                # Add available spots
                for i in range(1, lot_data['available'] + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        status='A',
                        spot_number=f"A{i:02d}"
                    )
                    db.session.add(spot)
                # Add occupied spots
                for i in range(lot_data['available'] + 1, lot_data['number_of_spots'] + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        status='O',
                        spot_number=f"O{i:02d}"
                    )
                    db.session.add(spot)
            db.session.commit()
            print("Database initialized with demo parking lots and spots!")
        else:
            print("Database already contains data.")

if __name__ == '__main__':
    init_db() 