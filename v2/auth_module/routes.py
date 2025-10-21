# auth_routes.py
from flask import Blueprint, render_template, request
from flask import flash, session, redirect, url_for
from db import get_db

auth_app = Blueprint('auth_app', __name__, template_folder='templates')

@auth_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        address = request.form['address']
        user_type = "customer"
        status = "ok"
        return signup_user(username, name, email, password, mobile, address, user_type, status)
    return render_template('signup.html')

@auth_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        return login_user(username, password, user_type)
    return render_template('login.html')

@auth_app.route('/logout')
def logout():
    logout_user()
    
   
################################method definations #################

def signup_user(username, name, email, password, mobile, address, user_type, status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users (username, name, email, password, mobile, address, user_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (username, name, email, password, mobile, address, user_type, status))
    db.commit()
    flash('Signup successful. Please login.')
    return redirect(url_for('auth_app.login'))

def login_user(username, password, user_type):
    db = get_db()
    cursor = db.cursor()

    if username == 'admin' and password == 'admin' and user_type == 'admin':
        session['username'] = username
        flash('Login successful.')
        return redirect(url_for('customer_app.home'))

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = username
        flash('Login successful.')
        return redirect(url_for('customer_app.home'))
    else:
        flash('Invalid credentials.')
        return redirect(url_for('auth_app.login'))

def logout_user():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('auth_app.login'))
    
