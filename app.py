from flask import Flask, render_template, request, redirect, session, send_from_directory
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- USERS ----------------

def load_users():
    if not os.path.exists("users.json"):
        return []
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ---------------- ITEMS ----------------

def load_items():
    if not os.path.exists("data.json"):
        return []
    with open("data.json", "r") as f:
        return json.load(f)

def save_items(items):
    with open("data.json", "w") as f:
        json.dump(items, f, indent=4)

# ---------------- AUTH ----------------

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        users.append({"username": username, "password": password})
        save_users(users)

        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        for u in users:
            if u["username"] == username and u["password"] == password:
                session["user"] = username
                return redirect("/dashboard")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    items = load_items()
    lost_items = [i for i in items if i["type"] == "lost"]
    found_items = [i for i in items if i["type"] == "found"]

    return render_template("dashboard.html",
                           lost_items=lost_items,
                           found_items=found_items)

# ---------------- ADD ITEM ----------------

@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form["name"]
    item = request.form["item"]
    desc = request.form["desc"]
    contact = request.form["contact"]
    type_ = request.form["type"]

    file = request.files["image"]
    filename = ""

    if file:
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    items = load_items()

    items.append({
        "name": name,
        "item": item,
        "desc": desc,
        "contact": contact,
        "type": type_,
        "image": filename
    })

    save_items(items)
    return redirect("/dashboard")

# ---------------- DELETE ----------------

@app.route("/delete/<int:index>")
def delete(index):
    items = load_items()
    if index < len(items):
        items.pop(index)
        save_items(items)
    return redirect("/dashboard")

# ---------------- IMAGE ----------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True,port=5001)