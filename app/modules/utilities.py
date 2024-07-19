import shutil

from app import db
from app.models import Book
from app.modules.transmission_integration import transmission_client


def check_download_statuses():
    print('Checking download statuses')
    books = Book.query.filter(Book.status.like('Downloading%')).all()
    for book in books:
        torrent = transmission_client.get_torrent(book.id)
        if torrent.progress == 100.0:
            book.status = 'Completed'
        else:
            book.status = f'Downloading ({torrent.progress}%)'
        db.session.commit()


def get_filename(book_id):
    book = Book.query.filter_by(id=book_id).first()
    torrent = transmission_client.get_torrent(book.id)
    filename = torrent.name
    return filename


def move_file(path: str):
    shutil.move(path, 'app/files')


def compress_folder(a: str):
    shutil.make_archive(a, 'zip', a)
