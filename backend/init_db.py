from app import create_app
from extensions import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot

def init_db():
    app = create_app()
    with app.app_context():
    
        db.create_all()

    
        if ParkingLot.query.first() is None:
            
            demo_lots = [
                {
                    'name': 'Mahakaleshwar Parking A',
                    'price': 40,
                    'address': 'Shree Mahakaleswar Jyotrilinga',
                    'pin_code': '456010',
                    'number_of_spots': 40,
                    'available': 40,
                    'occupied': 0
                },
                {
                    'name': 'Ujjain Railway Station Parking (Platform 1)',
                    'price': 50,
                    'address': 'Station Road, Platform 1',
                    'pin_code': '456010',
                    'number_of_spots': 20,
                    'available': 20,
                    'occupied': 0
                },
                {
                    'name': 'Airport',
                    'price': 50,
                    'address': 'Airport Road',
                    'pin_code': '456010',
                    'number_of_spots': 25,
                    'available': 25,
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
                db.session.flush()
                
                for i in range(1, lot_data['available'] + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        status='A',
                        spot_number=f"A{i:02d}"
                    )
                    db.session.add(spot)
                
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