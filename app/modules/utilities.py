import shutil

from app import db
from app.models import Book
from app.modules.transmission_integration import transmission_client


def check_download_statuses() -> None:
    """
        Check the download statuses of books marked as downloading and update their statuses.

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
            book.status = f'Downloading ({torrent.progress}%)'
        db.session.commit()


def get_filename(book_id: int) -> str:
    """
        Get the filename of the torrent associated with a book by its ID.

        Args:
            book_id (int): The ID of the book.

        Returns:
            str: The filename of the torrent.
    """
    book = Book.query.filter_by(id=book_id).first()
    torrent = transmission_client.get_torrent(book.id)
    filename = torrent.name
    return filename


def move_file(path: str) -> None:
    """
        Move a file to the 'app/files' directory.

        Args:
            path (str): The path to the file to be moved.

        Returns:
            None
    """
    shutil.move(path, 'app/files')


def compress_folder(a: str) -> None:
    """
        Compress a folder into a zip archive.

        Args:
            a (str): The path to the folder to be compressed.

        Returns:
            None
    """
    shutil.make_archive(a, 'zip', a)
