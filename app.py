from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- UPLOAD ----------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------- USERS ----------
def load_users():
    if not os.path.exists("users.json"):
        return []
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ---------- ITEMS ----------
def load_items():
    if not os.path.exists("data.json"):
        return []
    with open("data.json", "r") as f:
        return json.load(f)

def save_items(items):
    with open("data.json", "w") as f:
        json.dump(items, f, indent=4)

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        for user in users:
            if user["username"] == username and user["password"] == password:
                session["user"] = username
                return redirect(url_for('dashboard'))

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        users = load_users()
        users.append({
            "username": request.form["username"],
            "password": request.form["password"]
        })
        save_users(users)
        return redirect(url_for('login'))

    return render_template("register.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for('login'))

    items = load_items()
    return render_template("dashboard.html", items=items)

# ---------- ADD ITEM ----------
@app.route("/add", methods=["POST"])
def add_item():
    if "user" not in session:
        return redirect(url_for('login'))

    items = load_items()

    file = request.files.get("image")
    filename = ""

    if file and file.filename != "":
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    new_item = {
        "type": request.form["type"],
        "name": request.form["name"],
        "description": request.form["description"],
        "contact": request.form["contact"],
        "image": filename
    }

    items.append(new_item)
    save_items(items)

    return redirect(url_for('dashboard'))

# ---------- DELETE ----------
@app.route("/delete/<int:index>")
def delete_item(index):
    if "user" not in session:
        return redirect(url_for('login'))

    items = load_items()

    if 0 <= index < len(items):
        items.pop(index)
        save_items(items)

    return redirect(url_for('dashboard'))

# ---------- LOST ----------
@app.route("/lost")
def lost():
    if "user" not in session:
        return redirect(url_for('login'))

    items = load_items()
    lost_items = [i for i in items if i["type"] == "lost"]

    return render_template("lost.html", items=lost_items)

# ---------- FOUND ----------
@app.route("/found")
def found():
    if "user" not in session:
        return redirect(url_for('login'))

    items = load_items()
    found_items = [i for i in items if i["type"] == "found"]

    return render_template("found.html", items=found_items)

# ---------- IMAGE ----------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True, port=5011)