from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flight_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    seat_number = db.Column(db.String(10))
    status = db.Column(db.String(50), default='Confirmed')
    flight = db.relationship('Flight', backref='bookings')

@app.route('/')
def home():
    flights = Flight.query.all()
    bookings = []
    if 'user_id' in session:
        bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('home.html', flights=flights, bookings=bookings)

@app.route('/book_flight/<int:flight_id>', methods=['GET', 'POST'])
def book_flight(flight_id):
    if 'user_id' not in session:
        flash("Please login to book a flight")
        return redirect(url_for('login'))
    
    flight = Flight.query.get_or_404(flight_id)
    
    if request.method == 'GET':
        return render_template('book_flight.html', flight=flight)
    
    if flight.available_seats <= 0:
        flash("Sorry, no seats available")
        return redirect(url_for('home'))

    booking = Booking(
        user_id=session['user_id'],
        flight_id=flight_id,
        seat_number=f"A{flight.available_seats}"
    )
    
    flight.available_seats -= 1
    
    try:
        db.session.add(booking)
        db.session.commit()
        flash("Flight booked successfully!")
        return redirect(url_for('booking_confirmation', booking_id=booking.id))
    except Exception as e:
        db.session.rollback()
        flash(f"Booking failed! Error: {str(e)}")
        return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for('signup'))

        user = User(username=username, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            flash("Signup successful! Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}")
            db.session.rollback()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields', 'danger')
            return render_template('login.html')

        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                # Set session variables
                session['user_id'] = user.id
                session['username'] = user.username
                
                # Commit the session
                session.modified = True
                
                flash('Login successful!', 'success')
                # Explicitly return a redirect response
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')
                return render_template('login.html')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('login.html')

    # GET request - show the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('home'))

@app.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash("Unauthorized access")
        return redirect(url_for('home'))
    
    return render_template('booking_confirmation.html', booking=booking)

@app.route('/mybookings')
def mybookings():
    if 'user_id' not in session:
        flash("You must log in to view your bookings.")
        return redirect(url_for('login'))

    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('booking.html', bookings=bookings)

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample flights if none exist
        if not Flight.query.first():
            sample_flights = [
                Flight(
                    flight_number='AI101',
                    origin='Mumbai',
                    destination='Delhi',
                    departure_date=datetime(2024, 2, 1, 10, 0),
                    arrival_date=datetime(2024, 2, 1, 12, 0),
                    available_seats=150,
                    price=199.99
                ),
                Flight(
                    flight_number='AI102',
                    origin='Delhi',
                    destination='Bangalore',
                    departure_date=datetime(2024, 2, 1, 14, 0),
                    arrival_date=datetime(2024, 2, 1, 16, 30),
                    available_seats=120,
                    price=249.99
                ),
                Flight(
                    flight_number='AI103',
                    origin='Bangalore',
                    destination='Chennai',
                    departure_date=datetime(2024, 2, 2, 9, 0),
                    arrival_date=datetime(2024, 2, 2, 10, 30),
                    available_seats=100,
                    price=149.99
                )
            ]
            db.session.add_all(sample_flights)
            db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
