# admin_module/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

admin_app = Blueprint('admin_app', __name__, template_folder='templates')

@admin_app.route('/add', methods=['GET', 'POST'])
def add_product():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        status = request.form['status']
        cursor.execute("INSERT INTO items (title, description, category, status, username, remarks) VALUES (%s,%s,%s,%s,%s,%s)",
                       (title, description, category, status, 'admin', 'Added by admin'))
        db.commit()
        flash('Product added successfully.')
        return redirect(url_for('admin_app.list_products'))
    return render_template('add_product.html')

@admin_app.route('/list')
def list_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('list_products.html', items=items)

@admin_app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        status = request.form['status']
        cursor.execute("UPDATE items SET title=%s, description=%s, category=%s, status=%s WHERE id=%s",
                       (title, description, category, status, id))
        db.commit()
        flash('Product updated successfully.')
        return redirect(url_for('admin_app.list_products'))

    cursor.execute("SELECT * FROM items WHERE id=%s", (id,))
    item = cursor.fetchone()
    return render_template('edit_product.html', item=item)

@admin_app.route('/delete/<int:id>')
def delete_product(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM items WHERE id=%s", (id,))
    db.commit()
    flash('Product deleted successfully.')
    return redirect(url_for('admin_app.list_products'))
