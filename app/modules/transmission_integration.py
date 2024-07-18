import requests
import transmission_rpc
from config import TRANSMISSION_HOST, TRANSMISSION_PASSWORD, TRANSMISSION_PORT, TRANSMISSION_USER


transmission_client = transmission_rpc.Client(
    host=TRANSMISSION_HOST,
    port=TRANSMISSION_PORT,
    username=TRANSMISSION_USER,
    password=TRANSMISSION_PASSWORD)


def add_torrent(link: str) -> None:
    resp = requests.get(link)
    content = resp.content
    transmission_client.add_torrent(content)


def del_torrent(book_id: int) -> None:
    torrent = transmission_client.get_torrent(book_id)
    transmission_client.remove_torrent(torrent.id, delete_data=True)