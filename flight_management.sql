CREATE DATABASE IF NOT EXISTS flight_management;
USE flight_management;

-- Places Table (List of locations)
CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Sample Places
INSERT INTO places (name) VALUES
    ('New York'),
    ('London'),
    ('Paris'),
    ('Tokyo'),
    ('Sydney'),
    ('Dubai'),
    ('Los Angeles');

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    address TEXT
);

-- Flights Table (with place_id references)
CREATE TABLE IF NOT EXISTS flights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(50) NOT NULL UNIQUE,
    origin_id INT NOT NULL,  -- Reference to places (origin)
    destination_id INT NOT NULL,  -- Reference to places (destination)
    departure_date DATETIME NOT NULL,
    arrival_date DATETIME NOT NULL,
    available_seats INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (origin_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES places(id) ON DELETE CASCADE
);

-- Bookings Table (with place_id reference)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    flight_id INT NOT NULL,
    seat_number VARCHAR(10),
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Booked',
    place_id INT NOT NULL,  -- Reference to the place where the booking was made
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
);

-- Sample Flights (using place_id for origin and destination)
INSERT INTO flights (flight_number, origin_id, destination_id, departure_date, arrival_date, available_seats, price) VALUES
    ('FL123', 1, 2, '2025-06-01 18:00:00', '2025-06-02 06:00:00', 100, 500.00),
    ('FL456', 3, 4, '2025-06-05 14:00:00', '2025-06-06 06:30:00', 150, 600.00),
    ('FL789', 5, 6, '2025-06-10 22:00:00', '2025-06-11 06:00:00', 120, 550.00),
    ('FL101', 7, 4, '2025-06-12 16:00:00', '2025-06-13 05:00:00', 130, 450.00),
    ('FL202', 2, 1, '2025-06-15 20:00:00', '2025-06-16 05:30:00', 80, 400.00);

-- Sample Users
INSERT INTO users (username, email, password, phone_number, address) VALUES
    ('JohnDoe', 'john@example.com', 'hashed_password_1', '1234567890', '1234 Elm St, Springfield'),
    ('JaneSmith', 'jane@example.com', 'hashed_password_2', '0987654321', '5678 Oak Rd, Shelbyville'),
    ('AliceJohnson', 'alice@example.com', 'hashed_password_3', '5551234567', '789 Pine Ln, Capital City');

-- Sample Bookings (using place_id for the place where the booking was made)
INSERT INTO bookings (user_id, flight_id, seat_number, status, place_id) VALUES
    (1, 1, 'A1', 'Booked', 1),
    (2, 2, 'B3', 'Booked', 2),
    (3, 3, 'C5', 'Completed', 3);
