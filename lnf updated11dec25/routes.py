# routes.py
from flask import Blueprint, session, render_template, request, redirect, url_for, flash
from db import get_db
import os
from werkzeug.utils import secure_filename

from PIL import Image
import numpy as np

from flask import request, render_template, flash
import numpy as np
from customer_module.model import extract_features
#from model import extract_features
from sklearn.metrics.pairwise import cosine_similarity


customer_app = Blueprint('customer_app', __name__, template_folder='templates')

# Folders
# UPLOAD_LOST_FOLDER = os.path.join(os.getcwd(), "lostItems")
# UPLOAD_FOUND_FOLDER = os.path.join(os.getcwd(), "foundItems")
UPLOAD_LOST_FOLDER = os.path.join("static", "lostItems")
UPLOAD_FOUND_FOLDER = os.path.join("static", "foundItems")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# ------------------------------
# Helper Functions
# ------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def mse(img1, img2):
    return np.mean((img1.astype("float") - img2.astype("float")) ** 2)


# ------------------------------
# Home Page
# ------------------------------
@customer_app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("auth_app.login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE status = 1")
    items = cursor.fetchall()# returns tuples

    return render_template("home.html", items=items)


# ------------------------------
# Lost/Found Image Matching
# ------------------------------
#new match model

@customer_app.route("/match", methods=["GET", "POST"])
def match_items():
    if request.method == "POST":
        uploaded = request.files["photo"]
        lost_path = os.path.join(UPLOAD_LOST_FOLDER, uploaded.filename)
        uploaded.save(lost_path)

        # Extract features for uploaded (lost) image
        lost_feat = extract_features(lost_path)

        best_match_file = None
        best_similarity = 0

        # Loop through all FOUND images
        for file in os.listdir(UPLOAD_FOUND_FOLDER):
            found_path = os.path.join(UPLOAD_FOUND_FOLDER, file)

            found_feat = extract_features(found_path)

            # Compute similarity (0–1)
            sim = cosine_similarity([lost_feat], [found_feat])[0][0]

            if sim > best_similarity:
                best_similarity = sim
                best_match_file = file

        # Convert similarity to percentage accuracy
        accuracy = round(best_similarity * 100, 2)

        if best_similarity > 0.70:   # threshold 70%
            flash(f"Match found: {best_match_file} (Accuracy: {accuracy}%)")
        else:
            flash(f"No match found! Best accuracy = {accuracy}%")

    return render_template("match.html")




"""
######################old match method###############
@customer_app.route("/match", methods=["GET", "POST"])
def match_items():
    if request.method == "POST":
        uploaded = request.files["photo"]
        lost_path = os.path.join(UPLOAD_LOST_FOLDER, uploaded.filename)
        uploaded.save(lost_path)

        min_error = 999999
        match_file = None

        for file in os.listdir(UPLOAD_FOUND_FOLDER):
            found_path = os.path.join(UPLOAD_FOUND_FOLDER, file)

            lost_img = np.array(Image.open(lost_path).resize((256, 256)))
            found_img = np.array(Image.open(found_path).resize((256, 256)))

            error = mse(lost_img, found_img)
            if error < min_error:
                min_error = error
                match_file = file

        if min_error < 100:
            flash(f"Match found: {match_file}")
            #flash(f"Match found: {match_file} (error={min_error})")
        else:
            flash("No match found!")

    return render_template("match.html")

"""

# ------------------------------
# Add Found Items
# ------------------------------
@customer_app.route("/found-items", methods=["GET", "POST"])
def foundItems():
    
    if request.method == "POST":
        title = request.form["title"]
        found_by = request.form["found_by"]
        found_date = request.form["found_date"]
        remarks = request.form["remarks"]
        status = 1

        file = request.files["photo"]
        photo_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            os.makedirs(UPLOAD_FOUND_FOLDER, exist_ok=True)
            saved_path = os.path.join(UPLOAD_FOUND_FOLDER, filename)
            file.save(saved_path)

            photo_path = f"foundItems/{filename}"
            

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO founds (photo, title, found_by, found_date, remarks, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (photo_path, title, found_by, found_date, remarks, status))

        db.commit()

        flash("Found item added successfully!")
        return redirect(url_for("customer_app.foundItems"))

    return render_template("found_items.html")


# ------------------------------
# Add Lost Items
# ------------------------------
@customer_app.route("/lost-items", methods=["GET", "POST"])
def lostItems():
    db = get_db()
    cursor = db.cursor()

    # Fetch categories
    cursor.execute("SELECT id, title FROM category WHERE status = 1")
    categories = cursor.fetchall()
   # print (categories)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category_id = request.form["category_id"]
        user_id = request.form["username"]
        remarks = request.form["remarks"]
        status = 1

        file = request.files["photo"]
        photo_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            os.makedirs(UPLOAD_LOST_FOLDER, exist_ok=True)
            saved_path = os.path.join(UPLOAD_LOST_FOLDER, filename)
            file.save(saved_path)

            photo_path = f"lostItems/{filename}"

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO items (title, description, category_id, status, user_id, remarks, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, category_id, status, user_id, remarks, photo_path))

        db.commit()

        flash("Lost item added successfully!")
        return redirect(url_for("customer_app.lostItems"))

    # ✅ MUST pass categories
    return render_template("lost_items.html", categories=categories)


# ------------------------------
# Search Items
# ------------------------------
@customer_app.route("/search", methods=["GET", "POST"])
def search():
    items = []
    if request.method == "POST":
        keyword = "%" + request.form["keyword"] + "%"
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT * FROM items 
            WHERE title LIKE %s OR description LIKE %s
        """, (keyword, keyword))
        items = cursor.fetchall()

    return render_template("home.html", items=items)


# ------------------------------
# Logout
# ------------------------------
# @customer_app.route("/logout")
# def logout():
#     session.clear()
#     return render_template("login.html")

