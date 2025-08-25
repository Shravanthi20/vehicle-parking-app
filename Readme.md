# 🚗 ParkEase - Vehicle Parking Management App V1

A comprehensive web-based application for managing 4-wheeler parking lots, built using Flask and Bootstrap. It supports multi-user roles (Admin & Users), with features like parking lot management, slot availability, vehicle tracking, and automated cost calculation.

---

## 📋 Features

### 🔐 Authentication & Authorization
- **Multi-role login system** (Admin & User)
- **Secure password hashing** with Werkzeug
- **Session management** with Flask-Login
- **Role-based access control**

### 🅿️ Admin Dashboard
- **Parking lot management**: Create, edit, delete parking lots
- **Spot management**: View and manage individual parking spots
- **User management**: View all registered users and their parking history
- **Analytics**: Real-time charts for spot occupancy and lot utilization
- **Price management**: Set and modify hourly rates per lot
- **User history tracking**: Complete parking history for each user
- **Automatic timeout system**: 24-hour limit with warnings

### 🚘 User Dashboard
- **Spot reservation**: Book available parking spots
- **Real-time availability**: View current spot status
- **Vehicle tracking**: Track your parked vehicles
- **Cost calculation**: Automatic billing based on time duration
- **Payment history**: View past reservations and payments
- **Occupy/Release system**: Mark spot as occupied or release when leaving
- **Timeout warnings**: Notifications for long-running reservations

### 💰 Cost Management
- **Time-based billing**: Calculate costs based on parking duration
- **Hourly rates**: Configurable pricing per parking lot
- **Payment tracking**: Store and display payment information
- **Cost summaries**: Show pricing in dashboards and history
- **Automatic timeout billing**: Maximum 24-hour charge for expired reservations
- **Fair pricing**: Pay only for actual usage time

---

## 🛠 Tech Stack

| Layer       | Technology Used                            |
|-------------|---------------------------------------------|
| **Frontend**    | HTML5, CSS3, Bootstrap 5.3.3, Font Awesome 6.5.0 |
| **Backend**     | Python 3.11+, Flask 3.1.1                    |
| **Database**    | SQLite with SQLAlchemy ORM                   |
| **Authentication** | Flask-Login 0.6.3                        |
| **Templating**  | Jinja2                                      |
| **Charts**      | Matplotlib 3.10.3                          |
| **Security**    | Werkzeug (password hashing)                 |

---

## 📁 Project Structure

```
vehicle-parking-app-v1/
├── 📄 app.py                          # Main Flask application
├── 📄 README.md                       # Project documentation
├── 📄 requirements.txt                # Python dependencies
├── 📁 models/                         # Database models
│   ├── 📄 __init__.py                 # Database initialization
│   ├── 📄 user_admin.py               # User and Admin model
│   ├── 📄 parking_lot.py              # Parking lot model with properties
│   ├── 📄 parking_spot.py             # Parking spot model
│   ├── 📄 reservation.py              # Reservation model
│   └── 📄 payments.py                 # Payment model
├── 📁 templates/                      # HTML templates
│   ├── 📄 home_page.html              # Landing page
│   ├── 📄 login.html                  # Login page
│   ├── 📄 register.html               # Registration page
│   ├── 📄 admin_dashboard.html        # Admin dashboard with charts
│   ├── 📄 user_dashboard.html         # User dashboard
│   ├── 📄 create_lot.html             # Create parking lot form
│   ├── 📄 edit.html                   # Edit parking lot form
│   ├── 📄 spots.html                  # View parking spots
│   ├── 📄 history.html                # User reservation history
│   ├── 📄 users.html                  # Admin user management
│   └── 📄 user_history.html           # Individual user parking history
├── 📁 static/                         # Static assets
│   └── 📁 images/                     # Parking lot images
│       ├── 📄 parking_image0.png
│       ├── 📄 parking_image1.png
│       ├── 📄 parking_image2.png
│       ├── 📄 parking_image3.png
│       └── 📄 parking_image4.jpg
├── 📁 instance/                       # Database files
│   └── 📄 parking_system.db           # SQLite database
└── 📁 venv/                          # Virtual environment
    └── 📁 Lib/site-packages/          # Python packages
```

---

## 🚀 How to Run the Code

### Prerequisites
- **Python 3.11 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/24f2008761/vehicle-parking-app-v1.git
cd vehicle-parking-app-v1
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 👤 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@parkease.com`
- **Role**: `admin`

### Create User Account
1. Navigate to the registration page
2. Fill in your details
3. Select role as "user"
4. Login with your credentials

---

## 🛣️ Application Routes

### Admin Routes
- `/admin_dashboard` - Main admin dashboard with analytics
- `/admin/lot/create` - Create new parking lot
- `/admin/lot/edit/<lot_id>` - Edit existing parking lot
- `/admin/lot/delete/<lot_id>` - Delete parking lot
- `/admin/lot/<lot_id>/spots` - View spots in a specific lot
- `/admin/users` - View all registered users
- `/admin/user/<user_id>/history` - View complete parking history of a user

### User Routes
- `/user_dashboard` - Main user dashboard
- `/reserve/<lot_id>` - Reserve a parking spot
- `/occupy/<reservation_id>` - Mark spot as occupied
- `/release/<reservation_id>` - Release spot and calculate payment
- `/history` - View personal reservation history

### Authentication Routes
- `/` - Home page
- `/login` - User login
- `/register` - User registration
- `/logout` - User logout

## 🗄️ Database Schema

### User_Admin Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `role` (admin/user)

### ParkingLot Table
- `lot_id` (Primary Key)
- `prime_location_name`
- `price` (per hour)
- `capacity`
- `address`
- `pincode`
- `contact`
- `is_active`

### ParkingSpot Table
- `spot_id` (Primary Key)
- `lot_id` (Foreign Key)
- `spot_number` (Unique)
- `status` (A=Available, O=Occupied)
- `spot_type`

### Reservation Table
- `reservation_id` (Primary Key)
- `spot_id` (Foreign Key)
- `user_id` (Foreign Key)
- `reservation_timestamp`
- `parking_timestamp`
- `leaving_timestamp`
- `parking_cost_per_time`
- `vehicle_number`
- `payment_status`

### Payment Table
- `payment_id` (Primary Key)
- `reservation_id` (Foreign Key)
- `amount`
- `payment_method`
- `payment_status`
- `payment_timestamp`

---



## 📊 Key Features Explained

### Cost Calculation
The system automatically calculates parking costs based on:
1. **Time Duration**: Difference between parking and leaving timestamps
2. **Hourly Rate**: Price per hour set for each parking lot
3. **Minimum Billing**: At least 1 hour is charged
4. **Formula**: `total_cost = max(1, hours) × price_per_hour`

### Automatic Timeout System
- **24-hour limit**: Reservations automatically expire after 24 hours
- **Warning system**: Users receive warnings at 12 and 20 hours
- **Auto-charge**: Maximum 24-hour charge for expired reservations
- **Spot release**: Parking spots become available again automatically

### User History Tracking
- **Complete history**: Admins can view all parking history for any user
- **Analytics**: Parking patterns, most used lots, average duration
- **Payment tracking**: Complete payment history and spending analysis
- **User insights**: Member since date, total reservations, active status

### Spot Management
- **Automatic Allocation**: First available spot is assigned
- **Real-time Status**: Spots show Available/Occupied status
- **Capacity Management**: Admins can modify lot capacities
- **Detailed Spot View**: See user details, vehicle numbers, and reservation times
- **Occupy/Release System**: Users can mark spots as occupied or release them

### Admin User Management
- **User List**: View all registered users with current status
- **Individual History**: Complete parking history for each user
- **User Analytics**: Statistics on user behavior and spending patterns
- **Current Status**: See which users are currently parked

### Security Features
- **Password Hashing**: Secure password storage
- **Session Management**: Flask-Login integration
- **Role-based Access**: Different dashboards for admin/user
- **Input Validation**: Form validation and sanitization

---
