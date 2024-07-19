import os

from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from app import app, db
from .forms import LoginForm, SearchForm, RegistrationForm
from .models import Book, User, BookDTO
from .modules.jackett_integration import jackett_search
from .modules.transmission_integration import add_torrent, del_torrent
from .modules.utilities import check_download_statuses, get_filename, compress_folder, move_file


@app.route('/')
@login_required
def home():
    check_download_statuses()
    form = SearchForm()
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', books=books, form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print('User is already authenticated')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/search', methods=['POST'])
@login_required
def search():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        book_name = form.query.data
        search_type = form.search_type.data
        results = jackett_search(book_name) if search_type == 'rutracker' else []
    return render_template('search_results.html', form=form, results=results)


@app.route('/download', methods=['POST'])
@login_required
def download():
    title = request.form.get('title')
    description = request.form.get('description')
    link = request.form.get('link')
    source_page = request.form.get('source_page')

    book = BookDTO(title=title, description=description, link=link, source_page=source_page)
    db_book = book.to_db_model()
    db_book.user_id = current_user.id
    add_torrent(link)
    try:
        db.session.add(db_book)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('This book is already in your library', 'danger')
        return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/download_file/<int:book_id>', methods=['GET'])
@login_required
def download_file(book_id):
    filename = get_filename(book_id)
    if os.path.exists(os.path.join('app', 'files', filename)):
        return send_from_directory('files', filename, as_attachment=True)

    filepath = os.path.join('downloads', 'complete', filename)
    if os.path.isfile(filepath):
        move_file(filepath)
        return send_from_directory('files', filename, as_attachment=True)
    elif os.path.isdir(filepath):
        compress_folder(filepath)
        filename = f'{filename}.zip'
        filepath = os.path.join('downloads', 'complete', filename)
        move_file(filepath)
        return send_from_directory('files', filename, as_attachment=True)

    return redirect(url_for('home'))


@app.route('/delete/<int:book_id>', methods=['GET'])
@login_required
def delete(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    db.session.delete(book)
    db.session.commit()
    del_torrent(book_id)
    return redirect(url_for('home'))
