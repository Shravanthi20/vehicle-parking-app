from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user_admin import User_Admin
from .reservation import Reservation
from .payments import Payment
from .parking_spot import ParkingSpot
from .parking_lot import ParkingLot