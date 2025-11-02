DROP DATABASE IF EXISTS pythonproject;
CREATE DATABASE pythonproject CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE pythonproject;

-- ===========================================
-- 1️⃣ Table: airline
-- ===========================================

CREATE TABLE airline (
    name VARCHAR(30) NOT NULL,
    PRIMARY KEY (name)
) ENGINE=InnoDB;

INSERT INTO airline (name)
VALUES ('China Eastern'), ('Ha Noi');

-- ===========================================
-- 2️⃣ Table: airline_staff
-- ===========================================

CREATE TABLE airline_staff (
    username VARCHAR(30) NOT NULL,
    password VARCHAR(30),
    name VARCHAR(30),
    yourname VARCHAR(30),
    PRIMARY KEY (username),
    FOREIGN KEY (name) REFERENCES airline(name) ON DELETE SET NULL
) ENGINE=InnoDB;

INSERT INTO airline_staff (username, password, name)
VALUES
    ('admin', 'admin', 'Ha Noi'),
    ('mneedle', 'password', 'China Eastern');

-- ===========================================
-- 3️⃣ Table: airplane
-- ===========================================

CREATE TABLE airplane (
    ID DECIMAL(30,0) NOT NULL,
    name VARCHAR(30) NOT NULL,
    seats DECIMAL(5,0),
    PRIMARY KEY (ID),
    FOREIGN KEY (name) REFERENCES airline(name) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO airplane (ID, name, seats)
VALUES
    (12345, 'China Eastern', 50),
    (54321, 'China Eastern', 100);

-- ===========================================
-- 4️⃣ Table: airport
-- ===========================================

CREATE TABLE airport (
    name VARCHAR(30) NOT NULL,
    city VARCHAR(30),
    PRIMARY KEY (name)
) ENGINE=InnoDB;

INSERT INTO airport (name, city)
VALUES
    ('JFK', 'New York City'),
    ('PVG', 'Shanghai');

-- ===========================================
-- 5️⃣ Table: customer
-- ===========================================

CREATE TABLE customer (
    email VARCHAR(30) NOT NULL,
    name VARCHAR(30),
    password VARCHAR(30),
    phone_number DECIMAL(30,0),
    date_of_birth DATE,
    PRIMARY KEY (email)
) ENGINE=InnoDB;

INSERT INTO customer (email, name, password, phone_number, date_of_birth)
VALUES
    ('admin', 'duc', 'admin', 1, '2005-01-17'),
    ('email@123.com', 'Max Needle', 'password', 1234567890, '2000-08-30'),
    ('email@345.com', 'Matt Needle', 'password', 1234567891, '1985-11-03');

-- ===========================================
-- 6️⃣ Table: flight
-- ===========================================

CREATE TABLE flight (
    flight_number DECIMAL(30,0) NOT NULL,
    name VARCHAR(30) NOT NULL,
    dep_date_time TIMESTAMP NOT NULL,
    dep_airport VARCHAR(30),
    arr_airport VARCHAR(30),
    arr_date_time TIMESTAMP,
    base_price DECIMAL(6,2),
    ID DECIMAL(30,0),
    status VARCHAR(30),
    PRIMARY KEY (flight_number),
    FOREIGN KEY (name) REFERENCES airline(name) ON DELETE CASCADE,
    FOREIGN KEY (dep_airport) REFERENCES airport(name) ON DELETE CASCADE,
    FOREIGN KEY (arr_airport) REFERENCES airport(name) ON DELETE SET NULL,
    FOREIGN KEY (ID) REFERENCES airplane(ID) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO flight (name, flight_number, dep_date_time, dep_airport, arr_airport, arr_date_time, base_price, ID, status)
VALUES
    ('China Eastern', 1234567890, '2020-10-11 03:00:00', 'JFK', 'PVG', '2020-10-11 19:00:00', 1000.00, 12345, 'on-time'),
    ('China Eastern', 1234567891, '2020-10-12 03:00:00', 'PVG', 'JFK', '2020-10-12 19:00:00', 1200.00, 12345, 'on-time'),
    ('China Eastern', 1234567892, '2020-10-14 03:00:00', 'JFK', 'PVG', '2020-10-14 19:00:00', 1200.00, 54321, 'delayed'),
    ('China Eastern', 1234567893, '2020-10-15 03:00:00', 'PVG', 'JFK', '2020-10-15 19:00:00', 1000.00, 54321, 'delayed');

-- ===========================================
-- 7️⃣ Table: flight_ratings
-- ===========================================

CREATE TABLE flight_ratings (
    rating_id DECIMAL(5,0) NOT NULL,
    name VARCHAR(30),
    flight_number DECIMAL(30,0),
    rating DECIMAL(2,0),
    comment VARCHAR(500),
    PRIMARY KEY (rating_id),
    FOREIGN KEY (name) REFERENCES airline(name) ON DELETE CASCADE,
    FOREIGN KEY (flight_number) REFERENCES flight(flight_number) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ===========================================
-- 8️⃣ Table: phone_number
-- ===========================================

CREATE TABLE phone_number (
    username VARCHAR(30) NOT NULL,
    phone_number DECIMAL(30,0) NOT NULL,
    PRIMARY KEY (username, phone_number),
    FOREIGN KEY (username) REFERENCES airline_staff(username) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ===========================================
-- 9️⃣ Table: ticket
-- ===========================================

CREATE TABLE ticket (
    ID DECIMAL(30,0) NOT NULL,
    email VARCHAR(30),
    name VARCHAR(30),
    flight_number DECIMAL(30,0),
    sold_price DECIMAL(6,2),
    card_type VARCHAR(30),
    card_number DECIMAL(30,0),
    name_on_card VARCHAR(30),
    exp_date DATE,
    purchase_date_time TIMESTAMP,
    PRIMARY KEY (ID),
    FOREIGN KEY (email) REFERENCES customer(email) ON DELETE SET NULL,
    FOREIGN KEY (name) REFERENCES airline(name) ON DELETE SET NULL,
    FOREIGN KEY (flight_number) REFERENCES flight(flight_number) ON DELETE SET NULL
) ENGINE=InnoDB;

INSERT INTO ticket (ID, email, name, flight_number, sold_price, card_type, card_number, name_on_card, exp_date, purchase_date_time)
VALUES
    (13579, 'email@123.com', 'China Eastern', 1234567890, 950.00, 'credit', 1234567887654321, 'Max Needle', '2025-01-05', '2020-01-04 22:00:00'),
    (24680, 'email@123.com', 'China Eastern', 1234567891, 1350.00, 'debit', 8765432112345678, 'Max Needle', '2024-05-06', '2020-01-04 22:00:00');

-- ===========================================
-- 🔟 View: monthly_spending
-- ===========================================

CREATE OR REPLACE VIEW monthly_spending AS
SELECT
    t.ID,
    t.email,
    t.name,
    t.flight_number,
    t.sold_price,
    t.card_type,
    t.card_number,
    t.name_on_card,
    t.exp_date,
    t.purchase_date_time,
    MONTH(CURDATE()) - MONTH(t.purchase_date_time) AS relative_month
FROM ticket t;
