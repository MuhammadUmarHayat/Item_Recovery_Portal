from flask import Blueprint, session, render_template, request, redirect, url_for, flash
from db import get_db, close_db
import os
import mysql.connector
from werkzeug.utils import secure_filename



from PIL import Image
import numpy as np
import imageio.v3 as iio

customer_app = Blueprint('customer_app', __name__, template_folder='templates')

UPLOAD_LOST = "lostItems"
UPLOAD_FOUND = "foundItems"

def mse(img1, img2):
    return np.mean((img1.astype("float") - img2.astype("float")) ** 2)

@customer_app.route('/match', methods=['GET', 'POST'])
def match_items():
    if request.method == 'POST':
        lost_image = request.files['photo']
        lost_path = os.path.join(UPLOAD_LOST, lost_image.filename)
        lost_image.save(lost_path)

        min_error = 999999
        match_file = None

        for found_file in os.listdir(UPLOAD_FOUND):
            fpath = os.path.join(UPLOAD_FOUND, found_file)
            lost = np.array(Image.open(lost_path).resize((256,256)))
            found = np.array(Image.open(fpath).resize((256,256)))
            error = mse(lost, found)
            if error < min_error:
                min_error = error
                match_file = found_file

        if min_error < 100:  # adjust threshold
            flash(f"Match found: {match_file} (error={min_error})")
        else:
            flash("No match found.")

    return render_template('match.html')

# Define where images will be saved
#UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')  
UPLOAD_LOST_FOLDER = os.path.join(os.getcwd(), 'lostItems')  
UPLOAD_FOUND_FOLDER = os.path.join(os.getcwd(), 'foundItems') 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@customer_app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE status=1")
    items = cursor.fetchall()
    return render_template('home.html', items=items)

@customer_app.route('/found-items', methods=['GET', 'POST'])
def foundItems():
    if request.method == 'POST':
        #INSERT INTO `founds`(`id`, `photo`, `title`, `found_by`, `found_date`, `remarks`, `status`)
        title = request.form['title']
        found_by = request.form['found_by']
        found_date = request.form['found_date']
        category="found"
        remarks = request.form['remarks']
        status = 1

        file = request.files['photo']
        photo_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            category_path = os.path.join(UPLOAD_FOUND_FOLDER, category)
            os.makedirs(category_path, exist_ok=True)
            file_path = os.path.join(category_path, filename)
            file.save(file_path)

            # Save relative path for web display
            photo_path = f'foundItems/{filename}'

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO `founds`(`photo`, `title`, `found_by`, `found_date`, `remarks`, `status`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (photo_path,title, found_by, found_date, remarks, status ))
        db.commit()
        cursor.close()
        db.close()

        flash('Item added successfully!')
        return redirect(url_for('customer_app.lostItems'))

    return render_template('lost_items.html')

@customer_app.route('/lost-items', methods=['GET', 'POST'])
def lostItems():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        username = request.form['username']
        remarks = request.form['remarks']
        status = 1

        file = request.files['photo']
        photo_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            category_path = os.path.join(UPLOAD_LOST_FOLDER, category)
            os.makedirs(category_path, exist_ok=True)
            file_path = os.path.join(category_path, filename)
            file.save(file_path)

            # Save relative path for web display
           # photo_path = f'uploads/{category}/{filename}'

          

            photo_path = f'lostItems/{filename}'

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO items (title, description, category, status, username, remarks, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, category, status, username, remarks, photo_path))
        db.commit()
        cursor.close()
        db.close()

        flash('Item added successfully!')
        return redirect(url_for('customer_app.lostItems'))

    return render_template('lost_items.html')

@customer_app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

@customer_app.route('/search', methods=['GET', 'POST'])
def search():
    items = []
    if request.method == 'POST':
        keyword = "%" + request.form['keyword'] + "%"
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM items WHERE title LIKE %s OR description LIKE %s", (keyword, keyword))
        items = cursor.fetchall()
    return render_template('home.html', items=items)

# --- Database connection ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="lostfounddb"
    )
