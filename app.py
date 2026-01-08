from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db, User_Admin, Reservation, Payment, ParkingSpot, ParkingLot
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import io
import base64
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User_Admin.query.get(int(user_id))

def create_database():
    with app.app_context():
        db.create_all()
        if not User_Admin.query.first():
            admin = User_Admin(username='admin', 
                              email='admin@parkease.com',
                              role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

def check_expired_reservations():
    """Automatically handle expired reservations"""
    # Find reservations that are more than 24 hours old and still pending
    cutoff_time = datetime.now() - timedelta(hours=24)
    expired_reservations = Reservation.query.filter(
        Reservation.payment_status == 'Pending',
        Reservation.parking_timestamp < cutoff_time
    ).all()
    
    for reservation in expired_reservations:
        # Mark spot as available
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'A'
        
        # Calculate maximum charge (24 hours)
        max_hours = 24
        total_cost = max_hours * reservation.parking_cost_per_time
        
        # Create payment record
        payment = Payment(
            reservation_id=reservation.reservation_id,
            amount=total_cost,
            payment_method='Auto-charge',
            payment_status='Completed',
            payment_timestamp=datetime.now()
        )
        
        # Update reservation
        reservation.payment_status = 'Paid'
        reservation.leaving_timestamp = cutoff_time
        
        db.session.add(payment)
    
    if expired_reservations:
        db.session.commit()
        return len(expired_reservations)
    return 0

@app.route('/')
def home_page():
    return render_template('home_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        role = request.form['role']

        user = User_Admin.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.role == role:
            login_user(user)
            flash('Login successful!', 'success')
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash('Invalid username, password, or role. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))
        if User_Admin.query.filter_by(username=username).first() or User_Admin.query.filter_by(email=email).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        else: 
            user = User_Admin(username=username, email=email, role='user')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful! Welcome to your dashboard.', 'success')
            return redirect(url_for('user_dashboard'))
    return render_template('register.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))

    # Check for expired reservations
    expired_count = check_expired_reservations()
    if expired_count > 0:
        flash(f'{expired_count} expired reservation(s) have been automatically closed.', 'info')

    lots = ParkingLot.query.all()
    users = User_Admin.query.all()

    # Spot Occupancy Chart
    total_spots = ParkingSpot.query.count()
    available = ParkingSpot.query.filter_by(status='A').count()
    occupied = total_spots - available

    spot_data = {'Available': available, 'Occupied': occupied}
    chart1 = generate_chart(spot_data, chart_type='pie', title='Spot Occupancy')

    # Lot Utilization Chart
    lot_data = {}
    for lot in lots:
        lot_name = lot.prime_location_name
        total = ParkingSpot.query.filter_by(lot_id=lot.lot_id).count()
        occ = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='O').count()
        utilization = round((occ / total) * 100, 2) if total > 0 else 0
        lot_data[lot_name] = utilization

    chart2 = generate_chart(lot_data, chart_type='bar', title='Lot Utilization (%)')

    return render_template('admin_dashboard.html', lots=lots, users=users, chart1=chart1, chart2=chart2, available_spots=available, occupied_spots=occupied)

def generate_chart(data, chart_type='bar', title='Chart'):
    plt.switch_backend('Agg')  # Headless mode
    
    # Set figure size based on chart type
    if chart_type == 'bar':
        fig, ax = plt.subplots(figsize=(9, 9))
    else:
        fig, ax = plt.subplots(figsize=(9, 9))

    labels = list(data.keys())
    values = list(data.values())

    # Handle empty or all-zero data
    if not values or all(v == 0 for v in values):
        labels = ['No Data']
        values = [1]
        chart_type = 'bar'  # Avoid pie chart for invalid data
        title = 'No Data Available'

    if chart_type == 'bar':
        bars = ax.bar(labels, values, color='skyblue')
        # Rotate x-axis labels to prevent overlapping
        plt.xticks(rotation=45, ha='right')
        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{value}%', ha='center', va='bottom', fontsize=9)
        # Adjust bottom margin to prevent label cutoff
        plt.subplots_adjust(bottom=0.25)
    elif chart_type == 'pie':
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)

    ax.set_title(title, fontsize=12, fontweight='bold', pad=15)

    # Adjust layout with proper spacing to prevent label cutoff
    plt.tight_layout(pad=1.5)
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    chart_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return chart_base64

@app.route('/admin/lot/create', methods=['GET', 'POST'])
@login_required
def create_lot():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    if request.method == 'POST':
        lot = ParkingLot(
            prime_location_name=request.form['name'],
            price=float(request.form['price']),
            capacity=int(request.form['capacity']),
            address=request.form['address'],
            pincode=request.form['pincode'],
            contact=request.form['contact']
        )
        db.session.add(lot)
        db.session.commit()
        for i in range(1, lot.capacity + 1):
            spot = ParkingSpot(
                lot_id=lot.lot_id,
                spot_number=f"{lot.prime_location_name[:3]}-{lot.lot_id}-{i:03d}",
                status='A'  # Available
            )
            db.session.add(spot)
        
        db.session.commit()
        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/admin/lot/edit/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.prime_location_name = request.form['name']
        option = request.form['option']

        if option == 'price':
            price_input = request.form['price']
            try:
                lot.price = float(price_input)
            except ValueError:
                flash('Invalid price format', 'danger')
                return redirect(url_for('edit_lot', lot_id=lot_id))

        elif option == 'capacity':
            capacity_input = request.form['capacity']
            try:
                new_capacity = int(capacity_input)
            except ValueError:
                flash('Invalid capacity format', 'danger')
                return redirect(url_for('edit_lot', lot_id=lot_id))

            if new_capacity != lot.capacity:
                if new_capacity < lot.capacity:
                    spots_to_delete = ParkingSpot.query.filter(
                        ParkingSpot.lot_id == lot.lot_id,
                        ParkingSpot.spot_number >= f"{lot.prime_location_name[:3]}-{new_capacity + 1:03d}"
                    ).all()

                    for spot in spots_to_delete:
                        if spot.status == 'O':
                            flash('Cannot reduce capacity - some spots are occupied', 'danger')
                            return redirect(url_for('edit_lot', lot_id=lot_id))

                update_spots_for_lot(lot, new_capacity)
                lot.capacity = new_capacity

        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit.html', lot=lot)

def update_spots_for_lot(lot, new_capacity):
    """Helper function to manage spots when lot capacity changes"""
    current_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).count()
    
    if new_capacity > current_spots:
        # Add new spots
        for i in range(current_spots + 1, new_capacity + 1):
            spot = ParkingSpot(
                lot_id=lot.lot_id,
                spot_number=f"{lot.prime_location_name[:3]}-{i:03d}",
                status='A'
            )
            db.session.add(spot)
    elif new_capacity < current_spots:
        # Delete extra spots (only if not occupied)
        spots_to_delete = ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot.lot_id,
            ParkingSpot.spot_number >= f"{lot.prime_location_name[:3]}-{new_capacity+1:03d}"
        ).all()
        for spot in spots_to_delete:
            if spot.status == 'O':
                flash('Cannot reduce capacity — some spots are occupied.', 'danger')
                return

        # Safe to delete
        for spot in spots_to_delete:
            db.session.delete(spot)

@app.route('/admin/lot/delete/<int:lot_id>', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    if ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='O').count() > 0:
        flash('Cannot delete lot with occupied spots', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Delete all spots first
        ParkingSpot.query.filter_by(lot_id=lot.lot_id).delete()
        # Then delete the lot
        db.session.delete(lot)
        db.session.commit()
        flash('Parking lot deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting lot: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lot/<int:lot_id>/spots')
@login_required
def view_spots(lot_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.spot_number).all()
    
    # Get reservation details for occupied spots
    spot_details = []
    for spot in spots:
        detail = {'spot': spot}
        if spot.status == 'O':
            reservation = Reservation.query.filter_by(spot_id=spot.spot_id, payment_status='Pending').first()
            if reservation:
                detail['reservation'] = reservation
                detail['user'] = User_Admin.query.get(reservation.user_id)
        spot_details.append(detail)
    
    return render_template('spots.html', lot=lot, spots=spot_details)

@app.route('/admin/users')
@login_required
def view_users():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    users = User_Admin.query.all()
    user_details = []
    
    for user in users:
        details = {'user': user}
        active_reservation = Reservation.query.filter_by(
            user_id=user.id,
            payment_status='Pending'
        ).first()
        
        if active_reservation:
            details['spot'] = ParkingSpot.query.get(active_reservation.spot_id)
            details['reservation'] = active_reservation
        
        user_details.append(details)
    
    return render_template('users.html', users=user_details)

@app.route('/admin/user/<int:user_id>/history')
@login_required
def view_user_history(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))
    
    user = User_Admin.query.get_or_404(user_id)
    # Get all reservations for this user (both active and completed)
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(
        Reservation.reservation_timestamp.desc()
    ).all()
    
    # Get detailed information for each reservation
    reservation_details = []
    for reservation in reservations:
        detail = {
            'reservation': reservation,
            'spot': ParkingSpot.query.get(reservation.spot_id),
            'lot': ParkingLot.query.get(ParkingSpot.query.get(reservation.spot_id).lot_id) if ParkingSpot.query.get(reservation.spot_id) else None,
            'payment': Payment.query.filter_by(reservation_id=reservation.reservation_id).first()
        }
        reservation_details.append(detail)
    
    return render_template('user_history.html', user=user, reservations=reservation_details)

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home_page'))

    # Check for expired reservations
    expired_count = check_expired_reservations()
    if expired_count > 0:
        flash(f'{expired_count} expired reservation(s) have been automatically closed.', 'info')

    active_reservation = Reservation.query.filter_by(
        user_id=current_user.id, payment_status='Pending'
    ).all()

    # Check for long-running reservations and show warnings
    for res in active_reservation:
        hours_elapsed = (datetime.now() - res.parking_timestamp).total_seconds() / 3600
        if hours_elapsed > 12:
            flash(f'Warning: Your reservation has been active for {hours_elapsed:.1f} hours. Consider releasing your spot.', 'warning')
        elif hours_elapsed > 20:
            flash(f'Critical: Your reservation will be automatically closed in {24-hours_elapsed:.1f} hours.', 'danger')

    available_lots = ParkingLot.query.filter_by(is_active=True).all()

    return render_template('user_dashboard.html', lots=available_lots, reservation=active_reservation)


@app.route('/reserve/<int:lot_id>', methods=['POST'])
@login_required
def reserve_spot(lot_id):
    if current_user.role == 'admin':
        flash('Admins cannot make reservations', 'warning')
        return redirect(url_for('user_dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)
    vehicle_number = request.form['vehicle_number']
    user_parking_time = request.form['parking_time']
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    existing = Reservation.query.filter_by(vehicle_number=vehicle_number, payment_status='Pending').first()
    if existing:
        flash('An active reservation already exists for this vehicle number.', 'danger')
        return redirect(url_for('user_dashboard'))

    if spot.status != 'A':
        flash('Spot is already occupied', 'danger')
        return redirect(url_for('user_dashboard'))

    try:
        parking_timestamp = datetime.strptime(user_parking_time, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Invalid date format for parking time.', 'danger')
        return redirect(url_for('user_dashboard'))

    reservation = Reservation(
        spot_id=spot.spot_id,
        user_id=current_user.id,
        parking_cost_per_time=spot.lot.price,
        vehicle_number=vehicle_number,
        reservation_timestamp=datetime.now(),
        parking_timestamp=parking_timestamp
    )

    spot.status = 'O'  # Mark as occupied
    db.session.add(reservation)
    db.session.commit()

    flash(f'Spot {spot.spot_number} reserved successfully!', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/occupy/<int:reservation_id>', methods=['POST'])
@login_required
def occupy_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('user_dashboard'))

    # Update the parking timestamp to the actual time of occupation
    reservation.parking_timestamp = datetime.now()
    db.session.commit()

    flash(f'Spot {reservation.spot_id} occupancy confirmed. Timer started at {reservation.parking_timestamp.strftime("%H:%M")}.', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('user_dashboard'))

    if reservation.payment_status != 'Pending':
        flash('This reservation has already been paid.', 'info')
        return redirect(url_for('user_dashboard'))

    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'  # Mark spot as available

    reservation.leaving_timestamp = datetime.utcnow()

    duration = reservation.leaving_timestamp - reservation.parking_timestamp
    hours = max(1, duration.total_seconds() / 3600)
    total_cost = round(hours * reservation.parking_cost_per_time, 2)

    payment = Payment(
        reservation_id=reservation.reservation_id,
        amount=total_cost,
        payment_method='Cash',
        payment_status='Completed',
        payment_timestamp=datetime.now()
    )

    reservation.payment_status = 'Paid'
    db.session.add(payment)
    db.session.commit()

    flash(f'Spot released and payment of ₹{total_cost:.2f} recorded.', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/history')
@login_required
def history():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(
        Reservation.reservation_timestamp.desc()
    ).all()
    return render_template('history.html', reservations=reservations)



if __name__ == '__main__':
    create_database()
    app.run(debug=True)