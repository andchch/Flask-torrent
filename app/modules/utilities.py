import shutil

from app import db
from app.models import Book
from app.modules.transmission_integration import transmission_client


def check_download_statuses() -> None:
    """
    Проверка и обновление статуса загрузки книг.

    Returns:
        None
    """
    print('Checking download statuses')
    books = Book.query.filter(Book.status.like('Downloading%')).all()
    for book in books:
        torrent = transmission_client.get_torrent(book.id)
        if torrent.progress == 100.0:
            book.status = 'Completed'
        else:
            book.status = f'Downloading ({torrent.progress}%\nPeers: {torrent.peers_sending_to_us})'
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
