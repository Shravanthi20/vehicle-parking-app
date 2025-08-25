from . import db

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    spot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)
    spot_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(1), default="A")  # A = Available, O = Occupied
    spot_type = db.Column(db.String(20), default="Standard")

    reservations = db.relationship('Reservation', backref='spot', lazy=True, cascade="all, delete")