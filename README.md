# Vehicle Parking App V2 - Complete Admin & User System

A comprehensive parking management system with full admin and user functionalities, built with Flask backend and Vue.js frontend.

## 🚀 Features

### **Admin Features (FULLY IMPLEMENTED)**
- ✅ **Dashboard** - Real-time statistics and analytics
- ✅ **Parking Lot Management** - Create, edit, delete parking lots
- ✅ **Parking Spot Management** - Add, edit, delete individual spots
- ✅ **User Management** - View all users, activate/deactivate accounts
- ✅ **Booking Management** - View all bookings, cancel bookings
- ✅ **Analytics & Reports** - Monthly reports, revenue tracking
- ✅ **Real-time Data** - Live statistics and monitoring

### **User Features (FULLY IMPLEMENTED)**
- ✅ **Registration & Login** - Secure authentication
- ✅ **Parking Lot Browsing** - View available lots and spots
- ✅ **Spot Reservation** - Select specific spots with vehicle numbers
- ✅ **Session Management** - Start/end parking sessions
- ✅ **Booking History** - View past reservations
- ✅ **Profile Management** - Update personal information

## 🛠️ Setup Instructions

### 1. Backend Setup
```bash
docker-compose up --build
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Mailhog API**: http://localhost:8025

## 👤 Admin Access

**Login Credentials:**
- Email: `admin@parking.com`
- Password: `admin123`

**Admin Capabilities:**
1. **Dashboard** - View system statistics
2. **Parking Lots** - Manage all parking facilities
3. **Parking Spots** - Manage individual spots
4. **Bookings** - View and manage all reservations
5. **Users** - Manage user accounts
6. **Analytics** - View reports and analytics

## 🧪 Testing Admin Functions

### Quick Test Script
```bash
cd backend
python test_admin_functions.py
```

## 📊 Database Schema

### Tables
- **user** - User accounts and authentication
- **parking_lot** - Parking facility information
- **parking_spot** - Individual parking spots
- **reservation** - Booking records with vehicle numbers

### Key Features
- JWT authentication
- Redis caching for performance
- Celery for background tasks
- SQLite database

## 🔧 API Endpoints

### Admin Endpoints
- `GET /admin/dashboard` - Dashboard statistics
- `GET /admin/parking-lots` - List all lots
- `POST /admin/parking-lots/create` - Create new lot
- `POST /admin/parking-lots/{id}/edit` - Edit lot
- `POST /admin/parking-lots/{id}/delete` - Delete lot
- `GET /admin/users` - List all users
- `POST /admin/users/{id}/toggle-status` - Toggle user status
- `GET /admin/bookings` - List all bookings
- `POST /admin/bookings/{id}/cancel` - Cancel booking
- `GET /admin/analytics` - Analytics data

### User Endpoints
- `POST /register` - User registration
- `POST /login` - User login
- `GET /user/dashboard` - User dashboard
- `POST /user/reserve/{lot_id}` - Reserve parking spot
- `POST /user/end-session` - End parking session
- `GET /user/history` - Booking history


## 🚨 Troubleshooting

### Admin Login Issues
```bash
cd backend
python fix_admin.py
python test_admin.py
```

### Database Issues
```bash
cd backend
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database recreated')"
```

### Frontend Issues
```bash
cd frontend
npm install
npm run dev
```

## 📈 Performance Features

- **Redis Caching** - Fast data retrieval
- **JWT Authentication** - Secure sessions
- **Background Tasks** - Report generation
- **Real-time Updates** - Live statistics