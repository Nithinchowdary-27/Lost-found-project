from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DB ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        phone TEXT,
        image TEXT,
        type TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return redirect("/login")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",(u,p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM items WHERE type='lost'")
    lost = c.fetchall()

    c.execute("SELECT * FROM items WHERE type='found'")
    found = c.fetchall()

    conn.close()

    return render_template("dashboard.html", lost=lost, found=found)

# ---------- ADD ----------
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    desc = request.form["description"]
    phone = request.form["phone"]
    type_ = request.form["type"]

    file = request.files["image"]
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO items (name,description,phone,image,type) VALUES (?,?,?,?,?)",
              (name,desc,phone,filepath,type_))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)