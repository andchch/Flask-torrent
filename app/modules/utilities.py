import os
import shutil

from app import db
from app.models import Book, Chapter
from app.modules.transmission_integration import transmission_client


def check_download_statuses() -> None:
    """
    Проверка и обновление статуса загрузки книг.

    Returns:
        None
    """
    print('Checking download statuses')
    down_books = Book.query.filter(Book.status.like('Downloading%')).all()
    comp_books = Book.query.filter_by(status='Completed', parsed=False).all()
    for book in down_books:
        torrent = transmission_client.get_torrent(book.id)
        if torrent.progress == 100.0:
            book.status = 'Completed'
            filepath = os.path.join('downloads', 'complete', torrent.name)
            if os.path.isfile(filepath):
                book.is_folder = False
            else:
                book.is_folder = True
        else:
            book.status = f'Downloading ({torrent.progress})'
        db.session.commit()
    for book in comp_books:
        torrent = transmission_client.get_torrent(book.id)
        book_dir = torrent.name
        chapters = sorted(os.listdir(os.path.join('downloads', 'complete', book_dir)))

        for chapter in chapters:
            db_chapter = Chapter(title=chapter[:chapter.rindex('.')], filename=chapter, book_id=book.id)
            db.session.add(db_chapter)
        book.parsed = True
        db.session.commit()


def get_filename(book_id: int) -> str:
    """
    Получение имени файла по ID книги.

    Args:
        book_id (int): ID книги.

    Returns:
        str: Имя файла торрента.
    """
    book = Book.query.filter_by(id=book_id).first()
    torrent = transmission_client.get_torrent(book.id)
    filename = torrent.name
    return filename


def move_file(path: str) -> None:
    """
    Перемещение файла в 'app/files'.

    Args:
        path (str): Путь к файлу для перемещения.

    Returns:
        None
    """
    shutil.move(path, 'app/files')


def compress_folder(a: str) -> None:
    """
    Сжатие папки в архив.

    Args:
        a (str): Путь к папке.

    Returns:
        None
    """
    shutil.make_archive(a, 'zip', a)
