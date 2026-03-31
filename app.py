from flask import Flask, request, jsonify, render_template
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Folder to store uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Limit file size (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


# ✅ HOME ROUTE (FIXES YOUR ERROR)
@app.route("/")
def home():
    return render_template("index.html")  # Put your HTML in templates/


# ✅ UPLOAD ROUTE
@app.route("/upload", methods=["POST"])
def upload():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        utr = request.form.get("utr")

        ieee_card = request.files.get("ieee_card")
        screenshot = request.files.get("payment_screenshot")

        ieee_path = ""
        screenshot_path = ""

        # ✅ Save IEEE card
        if ieee_card and ieee_card.filename != "":
            filename = secure_filename(ieee_card.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            ieee_path = os.path.join(UPLOAD_FOLDER, unique_name)
            ieee_card.save(ieee_path)

        # ✅ Save Screenshot
        if screenshot and screenshot.filename != "":
            filename = secure_filename(screenshot.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            screenshot_path = os.path.join(UPLOAD_FOLDER, unique_name)
            screenshot.save(screenshot_path)

        # ✅ Save to DB
        save_to_db(name, email, utr, ieee_path, screenshot_path)

        return jsonify({"status": "success", "message": "Uploaded successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ DATABASE FUNCTION
def save_to_db(name, email, utr, ieee_path, screenshot_path):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        utr TEXT,
        ieee_card TEXT,
        screenshot TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO registrations (name, email, utr, ieee_card, screenshot)
    VALUES (?, ?, ?, ?, ?)
    """, (name, email, utr, ieee_path, screenshot_path))

    conn.commit()
    conn.close()


# ✅ RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)