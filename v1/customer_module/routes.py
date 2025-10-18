# customer_module/routes.py
from flask import Blueprint,session, render_template, request
from db import get_db

customer_app = Blueprint('customer_app', __name__, template_folder='templates')

@customer_app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE status=1")
    items = cursor.fetchall()
    return render_template('home.html', items=items)

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
