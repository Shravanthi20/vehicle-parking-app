from . import db 
from datetime import datetime

class Reservation(db.Model):
    __tablename__ = 'reservation'
    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.spot_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_admin.id'), nullable=False)
    reservation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost_per_time = db.Column(db.Float, nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), default="Pending")

    payment = db.relationship('Payment', back_populates='reservation', uselist=False, cascade="all, delete")