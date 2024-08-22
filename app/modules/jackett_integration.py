import requests
from requests import Response
from typing import List
import xml.etree.ElementTree as ET

from app.models import BookDTO
from config import JACKETT_API_KEY

JACKETT_BASE_URL = 'http://127.0.0.1:9117/api/v2.0/indexers/rutracker/results/torznab/'


def parse_jackett_response(response: Response) -> List[BookDTO]:
    """
    Обработка и преобразование ответа от Jackett в список объектов BookDTO.
    Args:
        response (Response): HTTP ответ от Jackett.

    Returns:
        List[BookDTO]: список объектов BookDTO.
    """
    results = []
    if response.status_code == 200:
        response_xml_doc = ET.fromstring(response.content)

        for item in response_xml_doc.findall('.//item'):
            category = item.find('category').text
            if category == '7000':
                category = 'Book'
            elif category == '3030':
                category = 'Audiobook'

            new_book = BookDTO(
                title=item.find('title').text if item.find('title') is not None else 'No title',
                description=item.find('description').text if item.find('description') is not None else 'No description',
                link=item.find('link').text if item.find('link') is not None else 'No link',
                source_page=item.find('guid').text if item.find('guid') is not None else 'No source page',
                filetype=category if category is not None else 'Unknown category'
            )
            results.append(new_book)

    return results


def jackett_search(book_name: str, search_limit: int = 20) -> List[BookDTO]:
    """
    Поиск книг используя Jackett API
    Args:
        book_name (str): Название книги для поиска.
        search_limit (int, optional): Максимальное количество книг. По умолчанию 10.

    Returns:
        List[BookDTO]: Список объектов BookDTO.
    """
    params = {
        'apikey': JACKETT_API_KEY,
        't': 'search',
        'limit': str(search_limit),
        'q': book_name
    }
    response = requests.get(JACKETT_BASE_URL, params=params)

    results = parse_jackett_response(response)
    return results
