# app.py
from flask import Flask, render_template
from config import *
from db import close_db
from auth_module.routes import auth_app
from admin_module.routes import admin_app
from customer_module.routes import customer_app

app = Flask(__name__)
app.secret_key = 'atiya_and_khadija'
app.debug = True  # Enables debugging
app.config.from_object('config')
app.teardown_appcontext(close_db)

# Register Blueprints
app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(admin_app, url_prefix='/admin')
app.register_blueprint(customer_app, url_prefix='/customer')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
