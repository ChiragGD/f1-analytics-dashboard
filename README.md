
# 🏎️ Formula 1 Analytics Dashboard

A web-based Formula 1 analytics platform built with **Python, Flask, and MySQL** to organize and explore race weekends, circuits, drivers, session results, leaderboard standings, car telemetry, and weather information through a centralized dashboard.

## 📌 Project Overview

The Formula 1 Analytics Dashboard provides an interactive interface for managing and analyzing F1-related data. It brings together race meeting information, session details, driver performance, championship points, and telemetry data in one application.

The project combines a relational database with a Flask web application to support structured data management, dynamic visualizations, and a user-friendly interface for exploring race statistics.

## ✨ Key Features

### 🏁 Race Meeting Management
- View and manage Formula 1 race meetings.
- Store meeting names, official event names, seasons, countries, locations, and event dates.
- Add and delete meeting records.

### ⏱️ Session Management
- Organize sessions associated with race meetings.
- Maintain session names, session types, and start and end times.
- Manage session records through the dashboard.

### 🏎️ Driver Management
- Maintain driver information associated with individual sessions.
- Store driver numbers, full names, broadcast names, teams, and team colours.
- Add, view, and remove driver-session records.

### 🏆 Leaderboard and Performance Analysis
- Display session results and driver positions.
- Track championship points and finishing status.
- Compare leaderboard results.
- Visualize driver points using a bar chart.

### 📊 Car Telemetry
- Store and explore telemetry records for individual drivers.
- Work with measurements including speed, throttle, brake, gear, RPM, and DRS.
- Associate telemetry data with a particular session and driver.

### 🌦️ Dynamic Weather Information
- Retrieve current weather information using the OpenWeatherMap API.
- Display weather conditions and temperature for a requested location.
- Handle missing API configuration and network errors.

### 🔐 User and Admin Authentication
- Provide user registration and login functionality.
- Include separate administrator registration and login routes.
- Use password hashing utilities for authentication.
- Apply access-control decorators to protected routes.

### 🗺️ Dashboard Navigation
- Navigate between meetings, sessions, drivers, leaderboards, telemetry, weather, positions, and site-map pages through a shared interface.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and backend processing |
| Flask | Web framework and routing |
| MySQL | Relational database and persistent storage |
| MySQL Connector/Python | Database connectivity |
| HTML5 and CSS3 | Page structure and styling |
| Bootstrap 5 | Responsive UI components |
| JavaScript | Client-side interactions |
| Chart.js | Leaderboard data visualization |
| OpenWeatherMap API | Live weather data |
| Werkzeug Security | Password hashing and verification |

## 🏗️ System Architecture

The application follows a three-layer architecture.

1. **Presentation layer:** HTML templates, CSS, Bootstrap, and JavaScript render the dashboard and provide user interactions.
2. **Application layer:** Flask handles HTTP requests, authentication, business logic, database queries, and external weather API requests.
3. **Data layer:** MySQL stores users, meetings, sessions, driver records, session results, telemetry, and related information.

```text
             User / Administrator
                      |
                      v
          Flask Web Application
          /         |          \
         v          v           v
   HTML Templates  MySQL    Weather API
   Bootstrap       Database  OpenWeatherMap
   JavaScript
         |
         v
   Charts and Analytics
```

## 📂 Project Structure

```text
f1-analytics-dashboard/
├── app.py
├── db/
│   └── f1.sql
├── static/
│   ├── chart.js
│   └── style.css
├── templates/
│   ├── layout.html
│   ├── admin_login.html
│   ├── admin_register.html
│   ├── login.html
│   ├── register.html
│   ├── meetings.html
│   ├── sessions.html
│   ├── drivers.html
│   ├── positions.html
│   ├── leaderboard_compare.html
│   ├── telemetry.html
│   ├── weather.html
│   ├── site.html
│   └── error.html
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.10 or a compatible version
- MySQL Server
- Git
- A modern web browser

A free OpenWeatherMap API key is required for live weather functionality.

### 1. Clone the repository

```bash
git clone https://github.com/ChiragGD/f1-analytics-dashboard.git
cd f1-analytics-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install Flask mysql-connector-python requests
```

### 4. Configure MySQL

Start your MySQL server and execute the database script from the MySQL command line:

```bash
mysql -u root -p < db/f1.sql
```

This initializes the `f1_openf1` database and creates the tables defined in the SQL script.

Review `db/f1.sql` before importing it, particularly if you already have a database with the same name.

### 5. Configure environment variables

Set your database credentials and Flask secret using environment variables instead of committing credentials to the repository.

Example for PowerShell:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASS = "your_mysql_password"
$env:DB_NAME = "f1_openf1"
$env:FLASK_SECRET = "your_random_secret"
$env:WEATHER_API_KEY = "your_openweathermap_api_key"
```

Use your own credentials. Never publish real passwords, API keys, or secret values.

### 6. Run the application

```bash
python app.py
```

Open the local URL printed by Flask in your browser. If the application uses its default local configuration, this is commonly:

`http://127.0.0.1:5000/`

## 🗄️ Database Design

The database schema covers the following main entities:

- **Users and administrators:** Account and authentication information.
- **Meeting:** Race event, season, location, and date information.
- **Session:** Session type, timing, and its associated meeting.
- **Driver session:** Driver identity and team information for a session.
- **Session result:** Finishing positions, points, times, and status.
- **Car telemetry:** Driver-specific vehicle measurements for a session.
- **Weather and fan preferences:** Additional weather and personalization data where defined in the schema.

The relational structure connects race meetings to sessions, and sessions to drivers, results, and telemetry records.

## 📈 Potential Applications

- Exploring Formula 1 race-weekend information.
- Comparing driver results and championship points.
- Reviewing telemetry measurements across sessions.
- Organizing motorsport data using a relational database.
- Practicing Flask application development, SQL queries, authentication, and data visualization.

## 🔮 Future Improvements

- Integrate a verified historical F1 data source for automated data ingestion.
- Add lap-by-lap and sector-time analysis.
- Introduce interactive telemetry charts and driver comparisons.
- Add filters for season, circuit, team, and session.
- Implement pagination, improved validation, and more comprehensive automated tests.
- Deploy the application using a production-ready WSGI server and managed database.

## 🎯 Learning Outcomes

This project demonstrates practical experience with:

- Full-stack web application development.
- REST-style routing and server-side rendering with Flask.
- Relational database design and SQL operations.
- CRUD operations and database integration.
- Authentication and password hashing.
- External API integration and error handling.
- Data visualization and dashboard design.

## 👨‍💻 Author

**Chirag GD**

- GitHub: [@ChiragGD](https://github.com/ChiragGD)
- LeetCode: [chiraggd](https://leetcode.com/u/chiraggd/)

---

*This project is intended for educational and portfolio purposes. Formula 1 and related trademarks belong to their respective owners.*
