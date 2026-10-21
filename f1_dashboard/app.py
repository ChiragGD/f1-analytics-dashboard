# app.py (updated)
from flask import Flask, render_template, request, redirect, url_for, session as flask_session, flash
import mysql.connector
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import socket
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "super-secret-key")  # change in prod

# ---------- Configuration ----------
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", "Liverpool@12"),
    "database": os.environ.get("DB_NAME", "f1_openf1"),
    "autocommit": True
}

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")  # set in env for live weather

# ------------------------------
# Database helpers
# ------------------------------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_db(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute_db(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    cur.close()
    conn.close()

# ------------------------------
# Auth helper decorators
# ------------------------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not flask_session.get("user_id") and not flask_session.get("admin_id"):
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not flask_session.get("admin_id"):
            flash("Admin access required.", "warning")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def safe_route(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # For security don't leak DB internals in production
            return render_template("error.html", error=str(e))
    return wrapper

# ------------------------------
# Authentication routes - User
# ------------------------------
@app.route("/register", methods=["GET", "POST"])
@safe_route
def register():
    # public user registration
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        if not name or not password:
            flash("Name and password required", "danger")
            return redirect(url_for("register"))

        pw_hash = generate_password_hash(password)
        try:
            execute_db("INSERT INTO users (name, password_hash) VALUES (%s, %s)", (name, pw_hash))
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@safe_route
def login():
    if request.method == "POST":
        name = request.form.get("name", "")
        password = request.form.get("password", "")
        row = query_db("SELECT * FROM users WHERE name=%s", (name,))
        if not row:
            flash("No such user.", "danger")
            return redirect(url_for("login"))
        user = row[0]
        if check_password_hash(user["password_hash"], password):
            flask_session.clear()
            flask_session["user_id"] = user["user_id"]
            flask_session["user_name"] = user["name"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    flask_session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ------------------------------
# Authentication routes - Admin
# ------------------------------
@app.route("/admin/register", methods=["GET", "POST"])
@safe_route
def admin_register():
    # Only allow register if no admin exists (simple bootstrap)
    existing = query_db("SELECT COUNT(*) AS c FROM admin")[0]["c"]
    if existing > 0:
        flash("Admin already exists. Use admin login.", "info")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("admin_name", "").strip()
        password = request.form.get("admin_password", "")
        if not name or not password:
            flash("Admin name and password required", "danger")
            return redirect(url_for("admin_register"))
        pw_hash = generate_password_hash(password)
        execute_db("INSERT INTO admin (admin_name, admin_password_hash) VALUES (%s, %s)", (name, pw_hash))
        flash("Admin registered. Please log in.", "success")
        return redirect(url_for("admin_login"))
    return render_template("admin_register.html")

@app.route("/admin/login", methods=["GET", "POST"])
@safe_route
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        admin = query_db("SELECT * FROM admin WHERE admin_name=%s", (username,))
        if not admin:
            flash("No such admin.", "danger")
            return redirect(url_for("admin_login"))
        admin = admin[0]
        if check_password_hash(admin["admin_password_hash"], password):
            flask_session.clear()
            flask_session["admin_id"] = admin["admin_id"]
            flask_session["admin_name"] = admin["admin_name"]
            flask_session["is_admin"] = True
            flash("Admin login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")

# ------------------------------
# Home / Dashboard
# ------------------------------
@app.route("/")
@safe_route
@login_required
def index():
    stats = {
        "meetings": query_db("SELECT COUNT(*) AS c FROM meeting")[0]["c"],
        "sessions": query_db("SELECT COUNT(*) AS c FROM session")[0]["c"],
        "drivers": query_db("SELECT COUNT(*) AS c FROM driver_session")[0]["c"],
        "leaderboard": query_db("SELECT COUNT(*) AS c FROM session_result")[0]["c"],
        "telemetry": query_db("SELECT COUNT(*) AS c FROM car_telemetry")[0]["c"]
    }
    return render_template("index.html", stats=stats)

# ------------------------------
# Meetings CRUD (admin-only for create/delete)
# ------------------------------
@app.route("/meetings")
@safe_route
@login_required
def meetings():
    rows = query_db("SELECT * FROM meeting ORDER BY date_start DESC")
    return render_template("meetings.html", meetings=rows)

@app.route("/add_meeting", methods=["POST"])
@safe_route
@admin_required
def add_meeting():
    execute_db("""
        INSERT INTO meeting (meeting_name, official_name, year, country, location, date_start, date_end)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form.get("meeting_name"),
        request.form.get("official_name"),
        request.form.get("year") or None,
        request.form.get("country"),
        request.form.get("location"),
        request.form.get("date_start") or None,
        request.form.get("date_end") or None
    ))
    flash("Meeting added.", "success")
    return redirect(url_for("meetings"))

@app.route("/delete_meeting/<int:meeting_key>", methods=["POST"])
@safe_route
@admin_required
def delete_meeting(meeting_key):
    execute_db("DELETE FROM meeting WHERE meeting_key=%s", (meeting_key,))
    flash("Meeting deleted.", "info")
    return redirect(url_for("meetings"))
# ------------------------------
# Driver Position Entry Page (Admin edit, User view only)
# ------------------------------
@app.route("/positions", methods=["GET", "POST"])
@safe_route
@login_required
def positions():
    sessions = query_db("SELECT session_key, session_name FROM session ORDER BY date_start DESC")
    session_key = request.args.get("session_key") or (sessions[0]["session_key"] if sessions else None)

    # ✅ Only admin can make POST (update)
    if request.method == "POST":
        if not flask_session.get("admin_id"):
            flash("Only admin can update results.", "danger")
            return redirect(url_for("positions", session_key=session_key))

        driver_number = request.form.get("driver_number")
        position = request.form.get("position")
        points = request.form.get("points")

        # Upsert into session_result
        existing = query_db(
            "SELECT result_id FROM session_result WHERE session_key=%s AND driver_number=%s",
            (session_key, driver_number),
        )
        if existing:
            execute_db(
                "UPDATE session_result SET position=%s, points=%s WHERE session_key=%s AND driver_number=%s",
                (position, points, session_key, driver_number),
            )
        else:
            execute_db(
                "INSERT INTO session_result (session_key, driver_number, position, points) VALUES (%s, %s, %s, %s)",
                (session_key, driver_number, position, points),
            )
        flash("Driver result updated.", "success")
        return redirect(url_for("positions", session_key=session_key))

    # Retrieve driver list for the selected session
    drivers = []
    if session_key:
        drivers = query_db(
            """
            SELECT ds.driver_number, ds.full_name, sr.position, sr.points
            FROM driver_session ds
            LEFT JOIN session_result sr
              ON ds.session_key = sr.session_key AND ds.driver_number = sr.driver_number
            WHERE ds.session_key = %s
            ORDER BY ds.driver_number ASC
            """,
            (session_key,),
        )

    return render_template("positions.html", sessions=sessions, session_key=session_key, drivers=drivers)
# ------------------------------
# Compare Two Drivers (Leaderboard Comparison)
# ------------------------------
@app.route("/compare", methods=["GET", "POST"])
@safe_route
@login_required
def compare_leaderboard():
    sessions = query_db("SELECT session_key, session_name FROM session ORDER BY date_start DESC")
    selected_session = request.args.get("session") or (sessions[0]["session_key"] if sessions else None)

    drivers = []
    result_data = None

    if selected_session:
        drivers = query_db("""
            SELECT ds.driver_number, ds.full_name, sr.position, sr.points
            FROM driver_session ds
            LEFT JOIN session_result sr
              ON ds.session_key = sr.session_key AND ds.driver_number = sr.driver_number
            WHERE ds.session_key = %s
            ORDER BY ds.driver_number ASC
        """, (selected_session,))

    if request.method == "POST":
        d1 = request.form.get("driver1")
        d2 = request.form.get("driver2")
        if d1 and d2 and selected_session:
            result_data = query_db("""
                SELECT ds.driver_number, ds.full_name, sr.position, sr.points
                FROM driver_session ds
                LEFT JOIN session_result sr
                  ON ds.session_key = sr.session_key AND ds.driver_number = sr.driver_number
                WHERE ds.session_key = %s AND ds.driver_number IN (%s, %s)
            """ % (selected_session, d1, d2))  # Safe since driver numbers are numeric

    return render_template(
        "leaderboard_compare.html",
        sessions=sessions,
        selected_session=selected_session,
        drivers=drivers,
        result_data=result_data,
    )


# ------------------------------
# Sessions CRUD (admin-only create/delete)
# ------------------------------
@app.route("/sessions")
@safe_route
@login_required
def sessions():
    rows = query_db("""SELECT s.*, m.meeting_name FROM session s
                       LEFT JOIN meeting m ON s.meeting_key = m.meeting_key
                       ORDER BY s.date_start DESC""")
    meetings = query_db("SELECT meeting_key, meeting_name FROM meeting ORDER BY date_start DESC")
    return render_template("sessions.html", sessions=rows, meetings=meetings)

@app.route("/add_session", methods=["POST"])
@safe_route
@admin_required
def add_session():
    execute_db("""
        INSERT INTO session (meeting_key, session_name, session_type, date_start, date_end)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        request.form.get("meeting_key") or None,
        request.form.get("session_name"),
        request.form.get("session_type"),
        request.form.get("date_start") or None,
        request.form.get("date_end") or None
    ))
    flash("Session created.", "success")
    return redirect(url_for("sessions"))

@app.route("/delete_session/<int:session_key>", methods=["POST"])
@safe_route
@admin_required
def delete_session(session_key):
    execute_db("DELETE FROM session WHERE session_key=%s", (session_key,))
    flash("Session deleted.", "info")
    return redirect(url_for("sessions"))

# ------------------------------
# Drivers (driver_session) CRUD (admin-only create/delete)
# ------------------------------
@app.route("/drivers")
@safe_route
@login_required
def drivers():
    rows = query_db("""SELECT ds.*, s.session_name FROM driver_session ds
                       LEFT JOIN session s ON ds.session_key = s.session_key
                       ORDER BY ds.driver_number ASC""")
    sessions = query_db("SELECT session_key, session_name FROM session ORDER BY date_start DESC")
    return render_template("drivers.html", drivers=rows, sessions=sessions)

@app.route("/add_driver", methods=["POST"])
@safe_route
@admin_required
def add_driver():
    execute_db("""
        INSERT INTO driver_session (session_key, driver_number, full_name, broadcast_name, team_name, team_colour)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        request.form.get("session_key") or None,
        request.form.get("driver_number"),
        request.form.get("full_name"),
        request.form.get("broadcast_name"),
        request.form.get("team_name"),
        request.form.get("team_colour")
    ))
    flash("Driver added.", "success")
    return redirect(url_for("drivers"))

@app.route("/delete_driver/<int:driver_session_id>", methods=["POST"])
@safe_route
@admin_required
def delete_driver(driver_session_id):
    execute_db("DELETE FROM driver_session WHERE driver_session_id=%s", (driver_session_id,))
    flash("Driver removed.", "info")
    return redirect(url_for("drivers"))

# ------------------------------
# Leaderboard (session_result) CRUD (admin add/delete) + comparison
# ------------------------------
@app.route("/leaderboard")
@safe_route
@login_required
def leaderboard():
    rows = query_db("""SELECT sr.*, ds.full_name FROM session_result sr
                       LEFT JOIN driver_session ds ON sr.session_key = ds.session_key AND sr.driver_number = ds.driver_number
                       ORDER BY sr.session_key DESC, sr.position ASC""")
    sessions = query_db("SELECT session_key, session_name FROM session ORDER BY date_start DESC")
    return render_template("leaderboard.html", leaderboard=rows, sessions=sessions)

@app.route("/add_leaderboard", methods=["POST"])
@safe_route
@admin_required
def add_leaderboard():
    execute_db("""
        INSERT INTO session_result (session_key, driver_number, position, points, time, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        request.form.get("session_key") or None,
        request.form.get("driver_number"),
        request.form.get("position"),
        request.form.get("points") or 0,
        request.form.get("time"),
        request.form.get("status")
    ))
    flash("Result added.", "success")
    return redirect(url_for("leaderboard"))

@app.route("/delete_leaderboard/<int:result_id>", methods=["POST"])
@safe_route
@admin_required
def delete_leaderboard(result_id):
    execute_db("DELETE FROM session_result WHERE result_id=%s", (result_id,))
    flash("Result deleted.", "info")
    return redirect(url_for("leaderboard"))

# Leaderboard comparison: query params ?session=xxx&d1=driver_number&d2=driver_number
@app.route("/leaderboard/compare")
@safe_route
@login_required
def compare_leaderboard():
    sess = request.args.get("session")
    d1 = request.args.get("d1")
    d2 = request.args.get("d2")
    if not sess or not d1 or not d2:
        flash("Please provide session, d1 and d2 query parameters.", "warning")
        return redirect(url_for("leaderboard"))

    q = """
      SELECT sr.driver_number, sr.position, sr.points, ds.full_name
      FROM session_result sr
      LEFT JOIN driver_session ds ON sr.session_key=ds.session_key AND sr.driver_number=ds.driver_number
      WHERE sr.session_key=%s AND sr.driver_number IN (%s, %s)
      ORDER BY sr.points DESC
    """
    rows = query_db(q, (sess, d1, d2))
    return render_template("leaderboard_compare.html", results=rows, session_key=sess, d1=d1, d2=d2)

# ------------------------------
# Telemetry CRUD (admin add/delete) + no-negative validation
# ------------------------------
@app.route("/telemetry")
@safe_route
@login_required
def telemetry():
    rows = query_db("SELECT * FROM car_telemetry ORDER BY date DESC LIMIT 200")
    sessions = query_db("SELECT session_key, session_name FROM session ORDER BY date_start DESC")
    return render_template("telemetry.html", telemetry=rows, sessions=sessions)

@app.route("/add_telemetry", methods=["POST"])
@safe_route
@admin_required
def add_telemetry():
    # Validate numeric inputs and reject negative values
    try:
        speed = float(request.form.get("speed") or 0)
        throttle = float(request.form.get("throttle") or 0)
        brake = float(request.form.get("brake") or 0)
        gear = int(request.form.get("gear") or 0)
        rpm = int(request.form.get("rpm") or 0)
        drs = int(request.form.get("drs") or 0)
    except ValueError:
        flash("Telemetry values must be numeric.", "danger")
        return redirect(url_for("telemetry"))

    if speed < 0 or throttle < 0 or brake < 0 or rpm < 0:
        flash("Telemetry values cannot be negative.", "danger")
        return redirect(url_for("telemetry"))

    # clamp throttle/brake to 0..1
    throttle = max(0.0, min(1.0, throttle))
    brake = max(0.0, min(1.0, brake))

    execute_db("""
        INSERT INTO car_telemetry (session_key, driver_number, speed, throttle, brake, gear, rpm, drs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form.get("session_key") or None,
        request.form.get("driver_number"),
        speed,
        throttle,
        brake,
        gear,
        rpm,
        drs
    ))
    flash("Telemetry added.", "success")
    return redirect(url_for("telemetry"))

@app.route("/delete_telemetry/<int:telemetry_id>", methods=["POST"])
@safe_route
@admin_required
def delete_telemetry(telemetry_id):
    execute_db("DELETE FROM car_telemetry WHERE telemetry_id=%s", (telemetry_id,))
    flash("Telemetry entry removed.", "info")
    return redirect(url_for("telemetry"))

# ------------------------------
# Weather page (dynamic via OpenWeatherMap)
# ------------------------------
@app.route("/weather", methods=["GET", "POST"])
@safe_route
@login_required
def weather():
    weather_data = {}
    location = request.form.get("location") if request.method == "POST" else request.args.get("location", "Monza,IT")
    API_KEY = WEATHER_API_KEY or os.environ.get("OPENWEATHER_API") or ""

    if not API_KEY:
        weather_data = {
            "error": "No WEATHER_API_KEY set. Set env var WEATHER_API_KEY for live data.",
            "location": location
        }
        return render_template("weather.html", weather=weather_data)

    # simple DNS check then request
    try:
        socket.gethostbyname("api.openweathermap.org")
    except socket.gaierror:
        weather_data = {"error": "Could not resolve api.openweathermap.org. Check network/DNS.", "location": location}
        return render_template("weather.html", weather=weather_data)

    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        j = resp.json()
        weather_data = {
            "location": f"{j.get('name')}, {j['sys'].get('country')}",
            "temperature": f"{j['main'].get('temp')} °C",
            "humidity": f"{j['main'].get('humidity')}%",
            "conditions": j['weather'][0].get('description').title(),
            "wind_speed": f"{j['wind'].get('speed')} m/s"
        }
    except requests.exceptions.RequestException as e:
        weather_data = {"error": f"Could not fetch weather: {str(e)}", "location": location}
    except Exception as e:
        weather_data = {"error": f"Unexpected error: {str(e)}", "location": location}

    return render_template("weather.html", weather=weather_data)

# ------------------------------
# Site / utility page
# ------------------------------
@app.route("/site")
@safe_route
@login_required
def site():
    stats = {
        "meetings": query_db("SELECT COUNT(*) AS c FROM meeting")[0]["c"],
        "sessions": query_db("SELECT COUNT(*) AS c FROM session")[0]["c"],
        "drivers": query_db("SELECT COUNT(*) AS c FROM driver_session")[0]["c"],
        "results": query_db("SELECT COUNT(*) AS c FROM session_result")[0]["c"],
    }
    return render_template("site.html", stats=stats)

# ------------------------------
# Error handler
# ------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found (404)"), 404

# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
