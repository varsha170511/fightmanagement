from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dbconfig import db

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret in production

cursor = db.cursor(dictionary=True)

# Home Route
@app.route('/')
def home():
    cursor.execute("SELECT * FROM places")
    places = cursor.fetchall()
    return render_template('home.html', places=places)

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            flash("Email already registered.")
            return redirect(url_for('signup'))

        # Insert new user into the database
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
            flash("Signup successful! Please log in.")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            db.rollback()

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password.")

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Simply clear the session to log the user out
    flash("Logged out successfully.")
    return redirect(url_for('home'))

# Search Route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    if not query:
        flash("Please enter a search query.")
        return redirect(url_for('home'))

    try:
        cursor.execute("SELECT * FROM places WHERE name LIKE %s", (f"%{query}%",))
        results = cursor.fetchall()
        if not results:
            flash("No places found matching your search.")
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
        results = []

    return render_template('home.html', results=results)

# View Place + Check-in/Check-out Form
@app.route('/place/<int:place_id>', methods=['GET', 'POST'])
def place(place_id):
    cursor.execute("SELECT * FROM places WHERE id = %s", (place_id,))
    place = cursor.fetchone()
    if not place:
        flash("Place not found.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'user_id' not in session:
            flash("You need to log in to make a booking.")
            return redirect(url_for('login'))

        hotel_name = request.form['hotel_name']
        room_size = request.form['room_size']
        num_persons = request.form['num_persons']
        in_date = request.form['in_date']
        out_date = request.form['out_date']
        special_request = request.form['special_requests']  # Selected special request
        other_request = request.form.get('other_request', '')  # Other request if "Others" is selected

        # Validate the booking details
        if not hotel_name or not room_size or not num_persons or not in_date or not out_date:
            flash("All fields are required.")
            return render_template('place.html', place=place)

        if special_request == "Others" and other_request:
            special_request = f"{special_request}: {other_request}"

        user_id = session['user_id']

        # Insert booking details into the database
        try:
            cursor.execute("""
                INSERT INTO bookings (user_id, place_id, hotel_name, room_size, num_persons, check_in, check_out, special_requests)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, place_id, hotel_name, room_size, num_persons, in_date, out_date, special_request))
            db.commit()
            flash(f"Booking for {place['name']} confirmed from {in_date} to {out_date}!")
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            db.rollback()

        return redirect(url_for('home'))

    return render_template('place.html', place=place)

# Booking Route (View bookings)
@app.route('/booking')
def booking():
    if 'user_id' not in session:
        flash("You must log in to view your bookings.")
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT b.*, p.name AS place_name
        FROM bookings b
        JOIN places p ON b.place_id = p.id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """, (session['user_id'],))

    bookings = cursor.fetchall()

    return render_template('booking.html', bookings=bookings)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
