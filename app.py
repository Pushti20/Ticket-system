from flask import Flask, request, render_template, send_file
import qrcode
import uuid
from io import BytesIO
import psycopg2

app = Flask(__name__)

# ================= DATABASE =================
DATABASE_URL = "postgresql://ticket_2rx5_user:2eCxcBOdngYTBvXGPCX2zveIwPbX8fXN@dpg-d6c64phr0fns73avn04g-a/ticket_2rx5"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create tables if not exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    user_name TEXT NOT NULL,
    status TEXT DEFAULT 'unused'
);
""")

conn.commit()

BASE_URL = "https://ticket-system-bosm.onrender.com"


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()

        cur.execute("SELECT * FROM users WHERE name=%s AND password=%s", (name, password))
        user = cur.fetchone()

        if user:
            cur.execute("SELECT ticket_id FROM tickets WHERE user_name=%s", (name,))
            tickets = [row[0] for row in cur.fetchall()]
            return render_template("dashboard.html", tickets=tickets)
        else:
            return "<h3>User not found. Please Sign Up.</h3>"

    return render_template("login.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()
        ticket_count = int(request.form["tickets"])

        # Insert user if not exists
        cur.execute("SELECT * FROM users WHERE name=%s", (name,))
        existing = cur.fetchone()

        if not existing:
            cur.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))

        new_tickets = []

        for _ in range(ticket_count):
            ticket_id = str(uuid.uuid4())
            new_tickets.append(ticket_id)

            cur.execute(
                "INSERT INTO tickets (ticket_id, user_name, status) VALUES (%s, %s, %s)",
                (ticket_id, name, "unused")
            )

        conn.commit()

        return render_template("dashboard.html", tickets=new_tickets)

    return render_template("signup.html")


# ================= QR GENERATION =================
@app.route("/qr/<ticket_id>")
def generate_qr(ticket_id):
    qr_data = f"{BASE_URL}/verify/{ticket_id}"
    img = qrcode.make(qr_data)

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


# ================= VERIFY =================
@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    cur.execute("SELECT status FROM tickets WHERE ticket_id=%s", (ticket_id,))
    ticket = cur.fetchone()

    if not ticket:
        return render_template("verify.html", message="Invalid Ticket")

    if ticket[0] == "unused":
        cur.execute("UPDATE tickets SET status='used' WHERE ticket_id=%s", (ticket_id,))
        conn.commit()
        return render_template("verify.html", message="Done")
    else:
        return render_template("verify.html", message="Already Scanned")


# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])

from flask import Flask, request, render_template, send_file
import qrcode
import uuid
from io import BytesIO
import psycopg2

app = Flask(__name__)

# ================= DATABASE =================
DATABASE_URL = "postgresql://ticket_2rx5_user:2eCxcBOdngYTBvXGPCX2zveIwPbX8fXN@dpg-d6c64phr0fns73avn04g-a/ticket_2rx5"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create tables if not exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    user_name TEXT NOT NULL,
    status TEXT DEFAULT 'unused'
);
""")

conn.commit()

BASE_URL = "https://ticket-system-bosm.onrender.com"


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()

        cur.execute("SELECT * FROM users WHERE name=%s AND password=%s", (name, password))
        user = cur.fetchone()

        if user:
            cur.execute("SELECT ticket_id FROM tickets WHERE user_name=%s", (name,))
            tickets = [row[0] for row in cur.fetchall()]
            return render_template("dashboard.html", tickets=tickets)
        else:
            return "<h3>User not found. Please Sign Up.</h3>"

    return render_template("login.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()
        ticket_count = int(request.form["tickets"])

        # Insert user if not exists
        cur.execute("SELECT * FROM users WHERE name=%s", (name,))
        existing = cur.fetchone()

        if not existing:
            cur.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))

        new_tickets = []

        for _ in range(ticket_count):
            ticket_id = str(uuid.uuid4())
            new_tickets.append(ticket_id)

            cur.execute(
                "INSERT INTO tickets (ticket_id, user_name, status) VALUES (%s, %s, %s)",
                (ticket_id, name, "unused")
            )

        conn.commit()

        return render_template("dashboard.html", tickets=new_tickets)

    return render_template("signup.html")


# ================= QR GENERATION =================
@app.route("/qr/<ticket_id>")
def generate_qr(ticket_id):
    qr_data = f"{BASE_URL}/verify/{ticket_id}"
    img = qrcode.make(qr_data)

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


# ================= VERIFY =================
@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    cur.execute("SELECT status FROM tickets WHERE ticket_id=%s", (ticket_id,))
    ticket = cur.fetchone()

    if not ticket:
        return render_template("verify.html", message="Invalid Ticket")

    if ticket[0] == "unused":
        cur.execute("UPDATE tickets SET status='used' WHERE ticket_id=%s", (ticket_id,))
        conn.commit()
        return render_template("verify.html", message="Done")
    else:
        return render_template("verify.html", message="Already Scanned")


# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form["password"]

        if password == "1234":
            cur.execute("""
                SELECT user_name, COUNT(*) 
                FROM tickets 
                GROUP BY user_name
            """)
            data = cur.fetchall()
            return render_template("admin_dashboard.html", data=data)
        else:
            return "<h3>Wrong Admin Password</h3>"

    return render_template("admin_login.html")
    
@app.route("/edit_tickets/<username>", methods=["POST"])
def edit_tickets(username):
    new_count = int(request.form["new_count"])

    # Get current tickets
    cur.execute("SELECT ticket_id FROM tickets WHERE user_name=%s", (username,))
    tickets = cur.fetchall()
    current_count = len(tickets)

    if new_count > current_count:
        # Add extra tickets
        for _ in range(new_count - current_count):
            new_ticket = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO tickets (ticket_id, user_name, status) VALUES (%s, %s, %s)",
                (new_ticket, username, "unused")
            )

    elif new_count < current_count:
        # Delete extra tickets (delete newest first)
        tickets_to_delete = tickets[new_count:]
        for t in tickets_to_delete:
            cur.execute("DELETE FROM tickets WHERE ticket_id=%s", (t[0],))

    conn.commit()
    return "<script>window.location='/admin'</script>"

@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("DELETE FROM tickets WHERE user_name=%s", (username,))
    cur.execute("DELETE FROM users WHERE name=%s", (username,))

    conn.commit()

    cur.close()
    conn.close()

    return "<script>window.location='/admin'</script>"
