import os
import certifi
import pymysql
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", 4000)),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "test"),
        ssl_ca=certifi.where(),
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                course VARCHAR(100) NOT NULL
            )
        """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO students (name, email, course) VALUES (%s, %s, %s)",
                (name, email, course)
            )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
    conn.close()
    return render_template("index.html", students=students)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
