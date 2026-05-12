-- Aviation Database Initialization Script

-- Airports Table
CREATE TABLE airports (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    elevation_ft INTEGER
);

INSERT INTO airports (code, name, city, country, latitude, longitude, elevation_ft) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 40.6413, -73.7781, 13),
('LHR', 'Heathrow Airport', 'London', 'UK', 51.4700, -0.4543, 83),
('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan', 35.5494, 139.7798, 21),
('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', -33.9399, 151.1753, 21),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 25.2532, 55.3657, 62);


-- Flights Table
CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    airline VARCHAR(100),
    origin VARCHAR(10) REFERENCES airports(code),
    destination VARCHAR(10) REFERENCES airports(code),
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    status VARCHAR(50)
);

INSERT INTO flights (flight_number, airline, origin, destination, departure_time, arrival_time, status) VALUES
('AA100', 'American Airlines', 'JFK', 'LHR', '2026-05-11 18:00:00', '2026-05-12 06:00:00', 'Scheduled'),
('BA200', 'British Airways', 'LHR', 'DXB', '2026-05-11 14:30:00', '2026-05-12 00:30:00', 'On Time'),
('JL300', 'Japan Airlines', 'HND', 'SYD', '2026-05-11 20:00:00', '2026-05-12 07:30:00', 'Delayed'),
('QF400', 'Qantas', 'SYD', 'JFK', '2026-05-11 10:00:00', '2026-05-12 16:00:00', 'Scheduled'),
('EK500', 'Emirates', 'DXB', 'HND', '2026-05-11 08:00:00', '2026-05-11 22:30:00', 'Boarding');


-- Weather Table
CREATE TABLE weather (
    weather_id SERIAL PRIMARY KEY,
    airport_code VARCHAR(10) REFERENCES airports(code),
    observation_time TIMESTAMP,
    temperature_c DECIMAL(5,2),
    wind_speed_knots INTEGER,
    wind_direction_deg INTEGER,
    visibility_km DECIMAL(5,2),
    conditions VARCHAR(100)
);

INSERT INTO weather (airport_code, observation_time, temperature_c, wind_speed_knots, wind_direction_deg, visibility_km, conditions) VALUES
('JFK', '2026-05-11 10:00:00', 15.5, 12, 270, 10.0, 'Clear'),
('LHR', '2026-05-11 10:00:00', 12.0, 15, 220, 8.0, 'Partly Cloudy'),
('HND', '2026-05-11 10:00:00', 22.3, 5, 180, 15.0, 'Sunny'),
('SYD', '2026-05-11 10:00:00', 18.7, 8, 90, 12.0, 'Clear'),
('DXB', '2026-05-11 10:00:00', 35.0, 10, 310, 6.0, 'Haze');


-- Radar Tracks Table
CREATE TABLE radar_tracks (
    track_id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20),
    timestamp TIMESTAMP,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    altitude_ft INTEGER,
    speed_knots INTEGER,
    heading_deg INTEGER
);

INSERT INTO radar_tracks (flight_number, timestamp, latitude, longitude, altitude_ft, speed_knots, heading_deg) VALUES
('AA100', '2026-05-11 18:15:00', 40.7000, -73.6000, 10000, 250, 45),
('AA100', '2026-05-11 18:30:00', 41.0000, -73.0000, 30000, 450, 50),
('BA200', '2026-05-11 15:00:00', 51.0000, 0.5000, 25000, 400, 120),
('BA200', '2026-05-11 15:15:00', 50.5000, 1.5000, 35000, 460, 125),
('JL300', '2026-05-11 20:30:00', 34.0000, 140.0000, 20000, 350, 170);
