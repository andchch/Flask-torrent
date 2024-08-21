import requests
from bs4 import BeautifulSoup
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


DEFAULT_IMAGE = 'https://cdn.icon-icons.com/icons2/567/PNG/512/bookshelf_icon-icons.com_54414.png'


@login_manager.user_loader
def load_user(user_id: int):
    """
        Load a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The user object.
    """
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    """
    Модель User.

    Attributes:
        id (int): The primary key of the user.
        username (str): The username of the user.
        pwd_hash (str): The hashed password of the user.
        books (relationship): The relationship to the Book model.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    pwd_hash = db.Column(db.String(255), nullable=False)
    books = db.relationship('Book', backref='user', lazy=True)

    @property
    def password(self):
        """
        Prevent reading the password attribute.

        Raises:
            AttributeError: When trying to read the password attribute.
        """
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password: str):
        """
        Set the password, hashing it before storing.

        Args:
            password (str): The plaintext password.
        """
        self.pwd_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify the password against the stored hash.

        Args:
            password (str): The plaintext password.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return check_password_hash(self.pwd_hash, password)


class Book(db.Model):
    """
    Модель Book.

    Attributes:
        id (int): The primary key of the book.
        title (str): The title of the book.
        description (str): The description of the book.
        image (str): The URL of the book's image.
        link (str): The unique link to the book's torrent.
        source_page (str): The source page of the book.
        user_id (int): The ID of the user who added the book.
        status (str): The download status of the book.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(1024), nullable=False, unique=True)
    source_page = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(255), nullable=False, default='Downloading')
    filetype = db.Column(db.String(255), nullable=False)


class BookDTO:
    """
    Модель BookDTO для передачи объекта

    Attributes:
        title (str): The title of the book.
        description (str): The description of the book.
        link (str): The unique link to the book's torrent.
        source_page (str): The source page of the book.
        image (str): The URL of the book's image.
    """
    def __init__(self, title: str, description: str, link: str, source_page: str, filetype: str):
        self.title = title
        self.description = description
        self.source_page = source_page
        self.image = self.get_image(source_page)
        self.link = link
        self.filetype = filetype

    @staticmethod
    def get_image(page_url) -> str:
        """
        Получение изображения книги по URL.

        Args:
            page_url (str): URL страницы книги.

        Returns:
            str: URL изображения.
        """
        try:
            response = requests.get(page_url)
            if response.status_code == 200:
                bs = BeautifulSoup(response.text, 'html.parser')
                image = bs.find(class_='postImg postImgAligned img-right').attrs['title']
                return image
            else:
                return DEFAULT_IMAGE
        except Exception:
            return DEFAULT_IMAGE

    def to_db_model(self) -> Book:
        """
        Преобразование BookDTO в Book..

        Returns:
            Book: Модель Book.
        """
        return Book(title=self.title, description=self.description, image=self.image, link=self.link,
                    source_page=self.source_page, filetype=self.filetype)
