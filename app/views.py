import os

from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import app, db
from .forms import LoginForm, SearchForm, RegistrationForm
from .models import Book, User, BookDTO, Chapter
from .modules.jackett_integration import jackett_search
from .modules.transmission_integration import add_torrent, del_torrent
from .modules.utilities import check_download_statuses, get_filename, compress_folder, move_file


@app.route('/')
@login_required
def home():
    """
    Главный путь для отображения библиотеки ползователя
    """
    check_download_statuses()
    form = SearchForm()
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', books=books, form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Registration route for new users.

    Methods:
        GET: Render the registration form.
        POST: Process the registration form submission.

    Returns:
        Response: The rendered template for the registration page or redirect to login.
    """
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
    """
    Login route for existing users.

    Methods:
        GET: Render the login form.
        POST: Process the login form submission.

    Returns:
        Response: The rendered template for the login page or redirect to home.
    """
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
    """
    Logout route to log out the current user.

    Returns:
        Response: Redirect to the login page.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/search', methods=['POST'])
@login_required
def search():
    """
    Страница поиска книг.

    Methods:
        POST: Поиск книг.
    """
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        book_name = form.query.data
        search_type = form.search_type.data
        if search_type == 'rutracker':
            results = jackett_search(book_name)
        else:
            results = (Book.query.filter_by(user_id=current_user.id)
                       .filter(or_(Book.title.ilike(f'%{book_name}%'),
                                   Book.description.ilike(f'%{book_name}%'))).all())
    return render_template('search_results.html', form=form, results=results)


@app.route('/download', methods=['POST'])
@login_required
def download():
    """
    Путь добавления книги в библиотеку пользователя и загрузки торрента.

    Methods:
        POST: Начало загрузки и добавления книги в библиотеку.
    """
    title = request.form.get('title')
    description = request.form.get('description')
    link = request.form.get('link')
    source_page = request.form.get('source_page')
    filetype = request.form.get('filetype')

    book = BookDTO(title=title, description=description, link=link, source_page=source_page, filetype=filetype)
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
    """
    Скачивание файла книги.

    Args:
        book_id (int): ID книги.

    Methods:
        GET: Скачивание.
    """
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
    """
    Удаление книги из библиотеки пользователя и торрента.

    Args:
        book_id (int): ID книги для удаления.

    Methods:
        GET: Удаление.
    """
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    db.session.delete(book)
    db.session.commit()
    del_torrent(book_id)
    return redirect(url_for('home'))


@app.route('/rename/<int:book_id>', methods=['POST'])
def rename_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    new_title = request.form['new_title']
    if new_title:
        book.rename(new_title)
        flash('Book renamed successfully!', 'success')
    else:
        flash('New title cannot be empty.', 'danger')
    return redirect(url_for('home'))


@app.route('/audiobook/<int:chapter_id>')
def play_audiobook(chapter_id):
    book_id = request.args.get('book_id')

    chapter = Chapter.query.get_or_404(chapter_id)
    book = Book.query.get_or_404(book_id)
    return send_from_directory(f'../downloads/complete/{book.filepath}', chapter.filename, as_attachment=False)
