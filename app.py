from flask import Flask, request, render_template, send_file
import qrcode
import csv
import os
import uuid
from io import BytesIO

app = Flask(__name__)

CSV_FILE = "tickets.csv"

# Create CSV if not exists or empty
if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "password", "ticket_id", "status"])


# ---------------- LOGIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        user_tickets = []

        with open(CSV_FILE, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)

            for row in rows[1:]:
                if row[0] == name and row[1] == password:
                    user_tickets.append(row[2])

        if user_tickets:
            return render_template("dashboard.html", tickets=user_tickets)
        else:
            return "<h3>User not found. Please Sign Up.</h3>"

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        ticket_count = int(request.form["tickets"])

        new_tickets = []

        for _ in range(ticket_count):
            ticket_id = str(uuid.uuid4())
            new_tickets.append(ticket_id)

            with open(CSV_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, password, ticket_id, "unused"])

        return render_template("dashboard.html", tickets=new_tickets)

    return render_template("signup.html")


# ---------------- DYNAMIC QR ----------------
@app.route("/qr/<ticket_id>")
def generate_qr(ticket_id):
    qr_data = f"https://ticket-system-xxxx.onrender.com/verify/{ticket_id}"
    img = qrcode.make(qr_data)

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


# ---------------- VERIFY ----------------
@app.route("/verify/<ticket_id>")
def verify(ticket_id):
    message = "Invalid Ticket"

    with open(CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    header = rows[0]
    data_rows = rows[1:]

    for row in data_rows:
        if row[2] == ticket_id:
            if row[3] == "unused":
                row[3] = "used"
                message = "Done"
            else:
                message = "Already Scanned"

    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data_rows)

    return render_template("verify.html", message=message)


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form["password"]

        if password == "1234":
            summary = {}

            with open(CSV_FILE, mode="r") as file:
                reader = csv.reader(file)
                rows = list(reader)

                for row in rows[1:]:
                    name = row[0]
                    if name in summary:
                        summary[name] += 1
                    else:
                        summary[name] = 1

            return render_template("admin_dashboard.html", data=summary)
        else:
            return "<h3>Wrong Admin Password</h3>"

    return render_template("admin_login.html")

