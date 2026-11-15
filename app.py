
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_connection, create_table

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-only")

create_table()
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (username == os.environ.get("ADMIN_USERNAME")
                and password == os.environ.get("ADMIN_PASSWORD")):
            session["admin_logged_in"] = True
            flash("Login successful!")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!")

    return render_template("login.html")
def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("home"))



@app.route("/")
def home():

    conn = get_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = conn.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    year_counts = conn.execute(
        """SELECT year, COUNT(*)
        FROM students
        GROUP BY year"""
    ).fetchall()

    conn.close()

    year_stats = dict(year_counts)

    return render_template(
        "index.html",
        total_students=total_students,
        total_courses=total_courses,
        year_stats=year_stats,
admin_logged_in=session.get("admin_logged_in", False)
    )



@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        year = request.form["year"]

        conn = get_connection()

        try:
            conn.execute(
                """INSERT INTO students
                (name, email, course, year)
                VALUES (?, ?, ?, ?)""",
                (name, email, course, year)
            )

            conn.commit()
            flash("Student registered successfully!")

        except sqlite3.IntegrityError:
            flash("This email is already registered!")

        finally:
            conn.close()

        return redirect(url_for("add_student"))

    return render_template("add_student.html")


@app.route("/students")
def view_students():

    search = request.args.get("search", "").strip()

    conn = get_connection()

    if search:
        students = conn.execute(
            """SELECT * FROM students
            WHERE CAST(id AS TEXT) LIKE ?
            OR name LIKE ?
            OR email LIKE ?
            OR course LIKE ?
            OR CAST(year AS TEXT) LIKE ?
            ORDER BY id""",
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students,
        search=search
    )

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):

    conn = get_connection()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        year = request.form["year"]

        try:
            conn.execute(
                """UPDATE students
                SET name = ?, email = ?, course = ?, year = ?
                WHERE id = ?""",
                (name, email, course, year, student_id)
            )

            conn.commit()
            flash("Student details updated successfully!")

        except sqlite3.IntegrityError:
            flash("This email is already registered!")

        finally:
            conn.close()

        return redirect(url_for("view_students"))

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/delete_student/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!")

    return redirect(url_for("view_students"))

if __name__ == "__main__":
    app.run(debug=True)
