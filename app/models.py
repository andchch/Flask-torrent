import requests
from bs4 import BeautifulSoup
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


DEFAULT_IMAGE = 'https://cdn.icon-icons.com/icons2/567/PNG/512/bookshelf_icon-icons.com_54414.png'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    pwd_hash = db.Column(db.String(255), nullable=False)
    books = db.relationship('Book', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pwd_hash, password)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(1024), nullable=False, unique=True)
    source_page = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(255), nullable=True, default='Downloading')


class BookDTO:
    def __init__(self, title: str, description: str, link: str, source_page: str):
        self.title = title
        self.description = description
        self.source_page = source_page
        self.image = self.get_image(source_page)
        self.link = link

    @staticmethod
    def get_image(page_url) -> str:
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
        return Book(title=self.title, description=self.description, image=self.image, link=self.link,
                    source_page=self.source_page)
