
-- -------------------------------------------------------------
-- DATABASE: f1_openf1
-- Cleaned + structured to support Flask Dashboard with login
-- -------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS f1_openf1;
USE f1_openf1;

-- -------------------------------------------------------------
-- USERS TABLE (for login/register)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  state VARCHAR(100),
  country VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- MEETING TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS meeting (
  meeting_key INT AUTO_INCREMENT PRIMARY KEY,
  meeting_name VARCHAR(255) NOT NULL,
  official_name VARCHAR(255),
  year INT,
  country VARCHAR(100),
  location VARCHAR(255),
  date_start DATE,
  date_end DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- SESSION TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS session (
  session_key INT AUTO_INCREMENT PRIMARY KEY,
  meeting_key INT NOT NULL,
  session_name VARCHAR(255) NOT NULL,
  session_type VARCHAR(100),
  date_start DATETIME,
  date_end DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_session_meeting FOREIGN KEY (meeting_key)
    REFERENCES meeting(meeting_key)
    ON DELETE CASCADE
);

-- -------------------------------------------------------------
-- DRIVER SESSION TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS driver_session (
  driver_session_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT NOT NULL,
  driver_number INT NOT NULL,
  full_name VARCHAR(255),
  broadcast_name VARCHAR(255),
  team_name VARCHAR(255),
  team_colour VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_driver_session FOREIGN KEY (session_key)
    REFERENCES session(session_key)
    ON DELETE CASCADE
);

-- -------------------------------------------------------------
-- SESSION RESULT TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS session_result (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT NOT NULL,
  driver_number INT NOT NULL,
  position INT,
  points DECIMAL(5,2) DEFAULT 0,
  time VARCHAR(50),
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_result_session FOREIGN KEY (session_key)
    REFERENCES session(session_key)
    ON DELETE CASCADE
);

-- -------------------------------------------------------------
-- CAR TELEMETRY TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS car_telemetry (
  telemetry_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT,
  driver_number INT,
  speed FLOAT,
  throttle FLOAT,
  brake FLOAT,
  gear INT,
  rpm INT,
  drs INT,
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_telemetry_session FOREIGN KEY (session_key)
    REFERENCES session(session_key)
    ON DELETE SET NULL
);

-- -------------------------------------------------------------
-- WEATHER TABLE
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather (
  weather_id INT AUTO_INCREMENT PRIMARY KEY,
  meeting_key INT,
  session_key INT,
  air_temperature FLOAT,
  humidity FLOAT,
  pressure FLOAT,
  rainfall FLOAT,
  track_temperature FLOAT,
  wind_direction FLOAT,
  wind_speed FLOAT,
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_weather_meeting FOREIGN KEY (meeting_key)
    REFERENCES meeting(meeting_key)
    ON DELETE SET NULL,
  CONSTRAINT fk_weather_session FOREIGN KEY (session_key)
    REFERENCES session(session_key)
    ON DELETE SET NULL
);

-- -------------------------------------------------------------
-- OPTIONAL: PROCEDURE FOR LEADERBOARD
-- -------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE sp_get_session_leaderboard(IN sess_key INT)
BEGIN
  SELECT sr.position, sr.driver_number, ds.full_name, sr.points
  FROM session_result sr
  LEFT JOIN driver_session ds
    ON sr.session_key = ds.session_key
   AND sr.driver_number = ds.driver_number
  WHERE sr.session_key = sess_key
  ORDER BY sr.points DESC;
END //
DELIMITER ;

-- -------------------------------------------------------------
-- DONE
-- -------------------------------------------------------------
drop table if exists admin;
select* from users;
drop database if exists f1_openf1;
-- f1.sql

CREATE DATABASE f1_openf1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE f1_openf1;

-- USERS
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADMINS
CREATE TABLE admins (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FAN (users' favourites)
CREATE TABLE fan (
  fan_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  favourite_driver VARCHAR(150),
  favourite_team VARCHAR(150),
  favourite_track VARCHAR(150),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- MEETINGS (Grand Prix events)
CREATE TABLE meeting (
  meeting_key INT AUTO_INCREMENT PRIMARY KEY,
  meeting_name VARCHAR(200) NOT NULL,
  official_name VARCHAR(200),
  year INT,
  country VARCHAR(100),
  location VARCHAR(200),
  date_start DATE,
  date_end DATE
);

-- SESSIONS (practice/qualifying/race)
CREATE TABLE session (
  session_key INT AUTO_INCREMENT PRIMARY KEY,
  meeting_key INT,
  session_name VARCHAR(200),
  session_type VARCHAR(50),
  date_start DATETIME,
  date_end DATETIME,
  FOREIGN KEY (meeting_key) REFERENCES meeting(meeting_key) ON DELETE SET NULL
);

-- DRIVER_SESSION (portal name: driver, actual table driver_session)
CREATE TABLE driver_session (
  driver_session_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT,
  driver_number INT NOT NULL,
  full_name VARCHAR(200),
  broadcast_name VARCHAR(100),
  team_name VARCHAR(150),
  team_colour VARCHAR(20),
  FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE SET NULL
);

-- SESSION_RESULT (leaderboard)
CREATE TABLE session_result (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT,
  driver_number INT,
  position INT,
  points DECIMAL(6,2) DEFAULT 0,
  time VARCHAR(100),
  status VARCHAR(100),
  FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE CASCADE
);

-- CAR_TELEMETRY
CREATE TABLE car_telemetry (
  telemetry_id INT AUTO_INCREMENT PRIMARY KEY,
  session_key INT,
  driver_number INT,
  speed FLOAT,
  throttle FLOAT,
  brake FLOAT,
  gear INT,
  rpm INT,
  drs TINYINT(1),
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE SET NULL
);

-- Optional: initial admin account (password hash placeholder)
-- Replace '<HASHED_PASSWORD>' with an actual hash produced by werkzeug.security.generate_password_hash
-- Example: in Python -> generate_password_hash("your_admin_password")
DROP TABLE IF EXISTS admins;
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
INSERT INTO admins (username, password_hash)
VALUES ('admin', 'pbkdf2:sha256:600000$qyHhTDTtUtJH9v3L$83e6c481c771ffde5d9ed24a2450d4a06763b76d7135275f36d9918efcda7e2c');
select * from admins;
drop database if exists f1_openf1;
-- f1_openf1.sql
-- Formula 1 Dashboard Database Schema (Admin/User Access)

CREATE DATABASE IF NOT EXISTS f1_openf1;
USE f1_openf1;

-- -----------------------
-- ADMINS TABLE
-- -----------------------
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Default admin: username=admin, password=Admin@123
INSERT INTO admins (username, password_hash) VALUES
('admin', '$pbkdf2-sha256$600000$8uREPOY8Z8VhXULgt9ZCAQ$Da8q6aDEx5j5DnLt8aefL5oeR7gHZKrSc1uOucCTMok'); 
-- Hash generated via werkzeug.security.generate_password_hash("Admin@123")

-- -----------------------
-- USERS TABLE
-- -----------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- sample user
INSERT INTO users (name, password_hash) VALUES
('fanuser', '$pbkdf2-sha256$600000$DJbdGZq7kG6cwOl7RSxViK$6O4PzK2KtrFqF9ItO7Jnxas93GknWvGcBPRH4jPppzU'); 
-- password: fan123

-- -----------------------
-- MEETING TABLE
-- -----------------------
CREATE TABLE meeting (
    meeting_key INT AUTO_INCREMENT PRIMARY KEY,
    meeting_name VARCHAR(255),
    official_name VARCHAR(255),
    year INT,
    country VARCHAR(100),
    location VARCHAR(100),
    date_start DATE,
    date_end DATE
);

INSERT INTO meeting (meeting_name, official_name, year, country, location, date_start, date_end)
VALUES ('Italian GP', 'Formula 1 Pirelli Gran Premio D’Italia', 2024, 'Italy', 'Monza', '2024-09-01', '2024-09-03');

-- -----------------------
-- SESSION TABLE
-- -----------------------
CREATE TABLE session (
    session_key INT AUTO_INCREMENT PRIMARY KEY,
    meeting_key INT,
    session_name VARCHAR(255),
    session_type VARCHAR(100),
    date_start DATETIME,
    date_end DATETIME,
    FOREIGN KEY (meeting_key) REFERENCES meeting(meeting_key) ON DELETE CASCADE
);

INSERT INTO session (meeting_key, session_name, session_type, date_start, date_end)
VALUES (1, 'Qualifying', 'Q', '2024-09-01 14:00:00', '2024-09-01 15:00:00');

-- -----------------------
-- DRIVER SESSION TABLE
-- -----------------------
CREATE TABLE driver_session (
    driver_session_id INT AUTO_INCREMENT PRIMARY KEY,
    session_key INT,
    driver_number INT,
    full_name VARCHAR(255),
    broadcast_name VARCHAR(255),
    team_name VARCHAR(255),
    team_colour VARCHAR(10),
    FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE CASCADE
);

INSERT INTO driver_session (session_key, driver_number, full_name, broadcast_name, team_name, team_colour)
VALUES (1, 16, 'Charles Leclerc', 'LEC', 'Ferrari', '#DC0000');

-- -----------------------
-- SESSION RESULT TABLE
-- -----------------------
CREATE TABLE session_result (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_key INT,
    driver_number INT,
    position INT,
    points FLOAT,
    time VARCHAR(50),
    status VARCHAR(50),
    FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE CASCADE
);

INSERT INTO session_result (session_key, driver_number, position, points, time, status)
VALUES (1, 16, 1, 25, '1:21:45.123', 'Finished');

-- -----------------------
-- CAR TELEMETRY TABLE
-- -----------------------
CREATE TABLE car_telemetry (
    telemetry_id INT AUTO_INCREMENT PRIMARY KEY,
    session_key INT,
    driver_number INT,
    speed FLOAT,
    throttle FLOAT,
    brake FLOAT,
    gear INT,
    rpm INT,
    drs INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_key) REFERENCES session(session_key) ON DELETE CASCADE
);

INSERT INTO car_telemetry (session_key, driver_number, speed, throttle, brake, gear, rpm, drs)
VALUES (1, 16, 312.5, 0.98, 0.0, 8, 11500, 1);

-- -----------------------
-- FAN TABLE
-- -----------------------
CREATE TABLE fan (
    fan_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    favourite_driver VARCHAR(100),
    favourite_team VARCHAR(100),
    favourite_track VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO fan (user_id, favourite_driver, favourite_team, favourite_track)
VALUES (1, 'Charles Leclerc', 'Ferrari', 'Monza');
drop table if exists admins;
USE f1_openf1;

CREATE TABLE IF NOT EXISTS admins (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE session_result ADD COLUMN dnf_reason VARCHAR(100);
SELECT * FROM driver_session;
ALTER TABLE session_result 
ADD UNIQUE KEY unique_session_position (session_key, position);


