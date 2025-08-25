from . import db

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    lot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.BigInteger, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete")
    
    @property
    def available(self):
        """Number of available spots in this lot"""
        return len([spot for spot in self.spots if spot.status == 'A'])
    
    @property
    def occupied(self):
        """Number of occupied spots in this lot"""
        return len([spot for spot in self.spots if spot.status == 'O'])
