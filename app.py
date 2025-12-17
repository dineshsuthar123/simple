from contextlib import closing
from datetime import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash
import pymysql

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "gymdb"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_db():
    return pymysql.connect(**DB_CONFIG)


def fetch_all(query: str, params=None):
    with closing(get_db()) as conn, conn.cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchall()


def execute(query: str, params=None):
    with closing(get_db()) as conn, conn.cursor() as cur:
        cur.execute(query, params or ())


@app.route("/")
def home():
    stats = fetch_all(
        """
        SELECT
            (SELECT COUNT(*) FROM Members) AS members,
            (SELECT COUNT(*) FROM Trainers) AS trainers,
            (SELECT COUNT(*) FROM Membership_Plans) AS plans,
            (SELECT COUNT(*) FROM Workout_Schedule) AS schedules,
            (SELECT COUNT(*) FROM Payments) AS payments,
            (SELECT COUNT(*) FROM Attendance) AS attendance
    """
    )[0]
    return render_template("index.html", stats=stats)


# Members
@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"].strip()
        gender = request.form["gender"].strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        execute(
            "INSERT INTO Members (name, gender, phone, email) VALUES (%s,%s,%s,%s)",
            (name, gender, phone, email),
        )
        flash("Member added", "success")
        return redirect("/view_members")
    return render_template("add_member.html")


@app.route("/view_members")
def view_members():
    members = fetch_all(
        """
         SELECT m.member_id, m.name, m.gender, m.phone, m.email,
             DATE_FORMAT(m.join_date,'%%d-%%b-%%Y') AS joined,
               IFNULL(GROUP_CONCAT(p.plan_name SEPARATOR ', '), '—') AS plans
        FROM Members m
        LEFT JOIN Member_Plan mp ON mp.member_id = m.member_id
        LEFT JOIN Membership_Plans p ON p.plan_id = mp.plan_id
        GROUP BY m.member_id
        ORDER BY m.member_id
    """
    )
    return render_template("view_members.html", members=members)


# Trainers
@app.route("/add_trainer", methods=["GET", "POST"])
def add_trainer():
    if request.method == "POST":
        name = request.form["name"].strip()
        specialization = request.form["specialization"].strip()
        contact = request.form.get("contact", "").strip()
        execute(
            "INSERT INTO Trainers (name, specialization, contact_no) VALUES (%s,%s,%s)",
            (name, specialization, contact),
        )
        flash("Trainer added", "success")
        return redirect("/view_trainers")
    return render_template("add_trainer.html")


@app.route("/view_trainers")
def view_trainers():
    trainers = fetch_all(
        "SELECT trainer_id, name, specialization, contact_no FROM Trainers ORDER BY trainer_id"
    )
    return render_template("view_trainers.html", trainers=trainers)


# Plans
@app.route("/add_plan", methods=["GET", "POST"])
def add_plan():
    if request.method == "POST":
        name = request.form["plan_name"].strip()
        duration = int(request.form["duration"])
        fee = float(request.form["fee"])
        execute(
            "INSERT INTO Membership_Plans (plan_name, duration_months, fee) VALUES (%s,%s,%s)",
            (name, duration, fee),
        )
        flash("Plan added", "success")
        return redirect("/view_plans")
    return render_template("add_plan.html")


@app.route("/view_plans")
def view_plans():
    plans = fetch_all(
        "SELECT plan_id, plan_name, duration_months, fee FROM Membership_Plans ORDER BY plan_id"
    )
    return render_template("view_plans.html", plans=plans)


# Assign plans
@app.route("/assign_plan", methods=["GET", "POST"])
def assign_plan():
    members = fetch_all("SELECT member_id, name FROM Members ORDER BY member_id")
    plans = fetch_all("SELECT plan_id, plan_name, duration_months FROM Membership_Plans")

    if request.method == "POST":
        member_id = int(request.form["member_id"])
        plan_id = int(request.form["plan_id"])
        start_date = request.form["start_date"]
        end_date = request.form.get("end_date")

        if not end_date:
            duration = next(p["duration_months"] for p in plans if p["plan_id"] == plan_id)
            # Let MySQL compute end_date from duration
            execute(
                """
                INSERT INTO Member_Plan (member_id, plan_id, start_date, end_date)
                VALUES (%s,%s,%s, DATE_ADD(%s, INTERVAL %s MONTH))
                """,
                (member_id, plan_id, start_date, start_date, duration),
            )
        else:
            execute(
                "INSERT INTO Member_Plan (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s)",
                (member_id, plan_id, start_date, end_date),
            )
        flash("Plan assigned", "success")
        return redirect("/view_member_plans")

    return render_template("assign_plan.html", members=members, plans=plans)


@app.route("/view_member_plans")
def view_member_plans():
    assignments = fetch_all(
        """
        SELECT m.member_id, m.name, p.plan_name,
               DATE_FORMAT(mp.start_date,'%%d-%%b-%%Y') AS start_date,
               DATE_FORMAT(mp.end_date,'%%d-%%b-%%Y') AS end_date,
               p.duration_months, p.fee
        FROM Member_Plan mp
        JOIN Members m ON m.member_id = mp.member_id
        JOIN Membership_Plans p ON p.plan_id = mp.plan_id
        ORDER BY m.member_id
    """
    )
    return render_template("view_member_plans.html", assignments=assignments)


# Schedules
@app.route("/add_schedule", methods=["GET", "POST"])
def add_schedule():
    trainers = fetch_all("SELECT trainer_id, name FROM Trainers ORDER BY trainer_id")
    if request.method == "POST":
        trainer_id = int(request.form["trainer_id"])
        name = request.form["schedule_name"].strip()
        time_slot = request.form["time_slot"].strip()
        execute(
            "INSERT INTO Workout_Schedule (trainer_id, schedule_name, time_slot) VALUES (%s,%s,%s)",
            (trainer_id, name, time_slot),
        )
        flash("Schedule added", "success")
        return redirect("/view_schedules")
    return render_template("add_schedule.html", trainers=trainers)


@app.route("/view_schedules")
def view_schedules():
    schedules = fetch_all(
        """
        SELECT ws.schedule_id, ws.schedule_name, ws.time_slot, t.name AS trainer
        FROM Workout_Schedule ws
        JOIN Trainers t ON t.trainer_id = ws.trainer_id
        ORDER BY ws.schedule_id
    """
    )
    return render_template("view_schedules.html", schedules=schedules)


# Payments
@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():
    members = fetch_all("SELECT member_id, name FROM Members ORDER BY member_id")
    schedules = fetch_all("SELECT schedule_id, schedule_name FROM Workout_Schedule ORDER BY schedule_id")

    if request.method == "POST":
        member_id = int(request.form["member_id"])
        schedule_id = int(request.form["schedule_id"])
        amount = float(request.form["amount"])
        mode = request.form["mode"].strip()
        execute(
            "INSERT INTO Payments (member_id, schedule_id, amount, mode_of_payment) VALUES (%s,%s,%s,%s)",
            (member_id, schedule_id, amount, mode),
        )
        flash("Payment recorded", "success")
        return redirect("/view_payments")

    return render_template("add_payment.html", members=members, schedules=schedules)


@app.route("/view_payments")
def view_payments():
    payments = fetch_all(
        """
        SELECT p.payment_id, m.name AS member, ws.schedule_name AS schedule,
               p.amount, DATE_FORMAT(p.payment_date,'%%d-%%b-%%Y') AS paid_on, p.mode_of_payment
        FROM Payments p
        JOIN Members m ON m.member_id = p.member_id
        JOIN Workout_Schedule ws ON ws.schedule_id = p.schedule_id
        ORDER BY p.payment_id
    """
    )
    return render_template("view_payments.html", payments=payments)


# Attendance
@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():
    members = fetch_all("SELECT member_id, name FROM Members ORDER BY member_id")
    schedules = fetch_all("SELECT schedule_id, schedule_name FROM Workout_Schedule ORDER BY schedule_id")

    if request.method == "POST":
        member_id = int(request.form["member_id"])
        schedule_id = int(request.form["schedule_id"])
        status = request.form["status"].strip()
        execute(
            "INSERT INTO Attendance (attender_id, schedule_id, status) VALUES (%s,%s,%s)",
            (member_id, schedule_id, status),
        )
        flash("Attendance marked", "success")
        return redirect("/view_attendance")

    return render_template("mark_attendance.html", members=members, schedules=schedules)


@app.route("/view_attendance")
def view_attendance():
    attendance = fetch_all(
        """
        SELECT a.attendance_id, m.name AS member, ws.schedule_name AS schedule,
               DATE_FORMAT(a.attendance_date,'%%d-%%b-%%Y') AS attended_on, a.status
        FROM Attendance a
        JOIN Members m ON m.member_id = a.attender_id
        JOIN Workout_Schedule ws ON ws.schedule_id = a.schedule_id
        ORDER BY a.attendance_id
    """
    )
    return render_template("view_attendance.html", attendance=attendance)


if __name__ == "__main__":
    app.run(debug=True)
