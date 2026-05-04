from flask import Flask, render_template, request, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Files
USER_FILE = "users.json"
DATA_FILE = "data.json"

# Ensure files exist
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Home → redirect to login
@app.route("/")
def home():
    return redirect("/login")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USER_FILE, "r") as f:
            users = json.load(f)

        # Check user exists
        for user in users:
            if user["username"] == username:
                return "User already exists"

        users.append({"username": username, "password": password})

        with open(USER_FILE, "w") as f:
            json.dump(users, f)

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USER_FILE, "r") as f:
            users = json.load(f)

        for user in users:
            if user["username"] == username and user["password"] == password:
                session["user"] = username   # ✅ IMPORTANT
                return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    with open(DATA_FILE, "r") as f:
        items = json.load(f)

    lost_items = [i for i in items if i["type"] == "lost"]
    found_items = [i for i in items if i["type"] == "found"]

    return render_template("dashboard.html", lost=lost_items, found=found_items)

# ---------------- ADD ITEM ----------------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]
    desc = request.form["description"]
    item_type = request.form["type"]

    with open(DATA_FILE, "r") as f:
        items = json.load(f)

    items.append({
        "name": name,
        "description": desc,
        "type": item_type
    })

    with open(DATA_FILE, "w") as f:
        json.dump(items, f)

    return redirect("/dashboard")

# ---------------- DELETE ITEM ----------------
@app.route("/delete/<int:index>")
def delete(index):
    if "user" not in session:
        return redirect("/login")

    with open(DATA_FILE, "r") as f:
        items = json.load(f)

    if index < len(items):
        items.pop(index)

    with open(DATA_FILE, "w") as f:
        json.dump(items, f)

    return redirect("/dashboard")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)