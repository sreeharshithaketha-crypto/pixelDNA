from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import sys
import sqlite3
import uuid
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from auth import User, init_db, register_user, verify_user, init_watermarks_table, save_watermark, get_watermark
from audit import init_audit_table, log_action, get_audit_log
from embedder import embed_watermark
from extracter import extract_watermark
from detector import run_detection

app = Flask(__name__)
app.secret_key = "pixeldna_secret_key_change_later"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[2])
    return None

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Username and password are required.")
            return render_template("register.html")
        success = register_user(username, password)
        if success:
            log_action(username, "REGISTER", "New account created")
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Username already exists.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = verify_user(username, password)
        if user:
            login_user(user)
            log_action(username, "LOGIN", "Successful login")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    log_action(current_user.username, "LOGOUT", "User logged out")
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    watermarked_url = None
    watermark_text = None
    wm_bits = None
    
    if request.method == "POST":
        file = request.files["image"]
        if file:
            sec_name = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, sec_name)
            file.save(input_path)

            watermark_text = f"{current_user.username}_{os.urandom(2).hex()}"
            wm_bits = len(watermark_text.encode('utf-8')) * 8
            
            out_filename = f"watermarked_{sec_name}"
            # Force lossless container (.png) for DWT-DCT watermarking
            if not out_filename.lower().endswith('.png'):
                base, _ = os.path.splitext(out_filename)
                out_filename = base + ".png"
                
            output_path = os.path.join("static", "watermarked", out_filename)

            embed_watermark(input_path, watermark_text, output_path)
            
            # Save both keys in DB for lookups
            save_watermark(current_user.username, out_filename, watermark_text, wm_bits)
            save_watermark(current_user.username, file.filename, watermark_text, wm_bits)
            
            log_action(current_user.username, "WATERMARK_EMBED", f"{file.filename} -> {out_filename}")

            watermarked_url = url_for('static', filename=f'watermarked/{out_filename}')
            flash(f"Image watermarked successfully!")
            
    return render_template("upload.html", watermarked_url=watermarked_url, watermark_text=watermark_text, wm_bits=wm_bits)

@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify():
    result = None
    original_url = None
    suspect_url = None
    ela_url = None
    expected_wm = None
    
    if request.method == "POST":
        original = request.files["original"]
        suspect = request.files["suspect"]
        custom_watermark = request.form.get("custom_watermark", "").strip()

        if original and suspect:
            uid = uuid.uuid4().hex
            orig_sec = secure_filename(original.filename)
            susp_sec = secure_filename(suspect.filename)
            
            _, orig_ext = os.path.splitext(orig_sec)
            _, susp_ext = os.path.splitext(susp_sec)
            if not orig_ext: orig_ext = ".png"
            if not susp_ext: susp_ext = ".png"
            
            orig_filename = f"original_{uid}{orig_ext}"
            susp_filename = f"suspect_{uid}{susp_ext}"
            ela_filename = f"ela_{uid}.jpg"
            
            verify_runs_dir = os.path.join("static", "verify_runs")
            original_path = os.path.join(verify_runs_dir, orig_filename)
            suspect_path = os.path.join(verify_runs_dir, susp_filename)
            ela_path = os.path.join(verify_runs_dir, ela_filename)
            
            original.save(original_path)
            suspect.save(suspect_path)
            
            # Watermark resolution logic
            if custom_watermark:
                expected_wm = custom_watermark
                wm_bits = len(expected_wm.encode('utf-8')) * 8
            else:
                clean_name = suspect.filename.replace("watermarked_", "").replace(".png", "")
                wm_data = get_watermark(clean_name)
                if wm_data:
                    expected_wm = wm_data[0]
                    wm_bits = wm_data[1]
                else:
                    clean_name_orig = original.filename.replace("watermarked_", "").replace(".png", "")
                    wm_data_orig = get_watermark(clean_name_orig)
                    if wm_data_orig:
                        expected_wm = wm_data_orig[0]
                        wm_bits = wm_data_orig[1]
                    else:
                        expected_wm = ""
                        wm_bits = 72 # default fallback
            
            result = run_detection(original_path, suspect_path, expected_watermark=expected_wm, wm_length_bits=wm_bits, ela_output_path=ela_path)
            
            original_url = url_for('static', filename=f'verify_runs/{orig_filename}')
            suspect_url = url_for('static', filename=f'verify_runs/{susp_filename}')
            ela_url = url_for('static', filename=f'verify_runs/{ela_filename}')
            
            log_action(current_user.username, "VERIFY", f"Checked {suspect.filename} against {original.filename}")
            
    return render_template("verify.html", result=result, original_url=original_url, suspect_url=suspect_url, ela_url=ela_url, expected_wm=expected_wm)

@app.route("/audit")
@login_required
def audit():
    logs = get_audit_log(current_user.username)
    # Sort logs by timestamp descending
    logs = sorted(logs, key=lambda x: x[4], reverse=True)
    return render_template("audit.html", logs=logs)

if __name__ == "__main__":
    init_db()
    init_audit_table()
    init_watermarks_table()
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join("static", "verify_runs"), exist_ok=True)
    os.makedirs(os.path.join("static", "watermarked"), exist_ok=True)
    
    app.run(debug=True)