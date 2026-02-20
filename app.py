from flask import Flask, request, render_template, send_file, redirect, url_for
import qrcode
import uuid
from io import BytesIO
import psycopg2

app = Flask(__name__)

DATABASE_URL = "postgresql://ticket_2rx5_user:2eCxcBOdngYTBvXGPCX2zveIwPbX8fXN@dpg-d6c64phr0fns73avn04g-a/ticket_2rx5"
BASE_URL = "https://ticket-system-bosm.onrender.com"


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# ---------- INIT DATABASE ----------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

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
    cur.close()
    conn.close()

init_db()


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE name=%s AND password=%s", (name, password))
        user = cur.fetchone()

        if user:
            cur.execute("SELECT ticket_id FROM tickets WHERE user_name=%s", (name,))
            tickets = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return render_template("dashboard.html", tickets=tickets)

        cur.close()
        conn.close()
        return "<h3>User not found</h3>"

    return render_template("login.html")


# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        ticket_count = int(request.form["tickets"])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE name=%s", (name,))
        if not cur.fetchone():
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
        cur.close()
        conn.close()

        return render_template("dashboard.html", tickets=new_tickets)

    return render_template("signup.html")


# ---------- QR ----------
@app.route("/qr/<ticket_id>")
def generate_qr(ticket_id):
    qr_data = f"{BASE_URL}/verify/{ticket_id}"
    img = qrcode.make(qr_data)

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


# ---------- VERIFY ----------
@app.route("/verify/<ticket_id>")
def verify(ticket_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT status FROM tickets WHERE ticket_id=%s", (ticket_id,))
    ticket = cur.fetchone()

    if not ticket:
        cur.close()
        conn.close()
        return render_template("verify.html", message="Invalid Ticket")

    if ticket[0] == "unused":
        cur.execute("UPDATE tickets SET status='used' WHERE ticket_id=%s", (ticket_id,))
        conn.commit()
        message = "Done"
    else:
        message = "Already Scanned"

    cur.close()
    conn.close()

    return render_template("verify.html", message=message)


# ---------- ADMIN LOGIN ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "1234":
            return redirect(url_for("admin_dashboard"))
        return "<h3>Wrong Password</h3>"

    return render_template("admin_login.html")


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin/dashboard")
def admin_dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_name, COUNT(*)
        FROM tickets
        GROUP BY user_name
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin_dashboard.html", data=data)


# ---------- EDIT TICKETS ----------
@app.route("/edit_tickets/<username>", methods=["POST"])
def edit_tickets(username):
    new_count = int(request.form["new_count"])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT ticket_id FROM tickets WHERE user_name=%s", (username,))
    tickets = cur.fetchall()
    current_count = len(tickets)

    if new_count > current_count:
        for _ in range(new_count - current_count):
            new_ticket = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO tickets (ticket_id, user_name, status) VALUES (%s, %s, %s)",
                (new_ticket, username, "unused")
            )
    elif new_count < current_count:
        for t in tickets[new_count:]:
            cur.execute("DELETE FROM tickets WHERE ticket_id=%s", (t[0],))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ---------- DELETE USER ----------
@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tickets WHERE user_name=%s", (username,))
    cur.execute("DELETE FROM users WHERE name=%s", (username,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))
