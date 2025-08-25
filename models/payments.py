from . import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.reservation_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    payment_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    reservation = db.relationship('Reservation', back_populates='payment')

    def __repr__(self):
        return f'<Payment #{self.payment_id} | ₹{self.amount:.2f} | {self.payment_method} | {self.payment_status}>'