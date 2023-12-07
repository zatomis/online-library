import logging
import os
import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape
from os import path
from livereload import Server
from more_itertools import chunked
import argparse
from urllib.parse import urljoin
import json

INDEX_PAGES_FOLDER_NAME = 'pages'

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Генератор страницы сайта библиотеки www.tululu.org"
    )
    parser.add_argument(
        '--dest_folder',
        default='General',
        type=str,
        help='Путь к каталогу с данными для генерации',
    )
    args = parser.parse_args()
    return args


def find_json_files(directory):
    json_files = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            json_files.append(file)
    return json_files


def on_reload():
    parsed_arguments = parse_arguments()
    general_folder = parsed_arguments.dest_folder
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    data_structures_file = find_json_files(general_folder)[0]
    with open(os.path.join(general_folder, data_structures_file), "r") as json_file:
        book_details = json_file.read()
    books = json.loads(book_details)

    for item_path in books:
        item_path['img_path'] = urljoin(general_folder + os.sep, str(item_path['img_path']))
        # item_path['img_path'] = urljoin(INDEX_PAGES_FOLDER_NAME + os.sep, general_folder + os.sep, str(item_path['img_path']))
        item_path['book_path'] = urljoin(general_folder + os.sep, str(item_path['book_path']))
        # item_path['book_path'] = urljoin(INDEX_PAGES_FOLDER_NAME + os.sep, general_folder + os.sep, str(item_path['book_path']))
        logging.info(item_path['book_path'])


    os.makedirs(os.path.join(os.getcwd(), INDEX_PAGES_FOLDER_NAME), mode=0o777, exist_ok=True)
    books_by_group = list(chunked(books, 10))
    for i, books in enumerate(books_by_group, 1):
        rendered_page = template.render(books=chunked(books, 2))
        index_file_name = os.path.join(INDEX_PAGES_FOLDER_NAME, f'index{i}.html')
        with open(index_file_name, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d - %(levelname)-8s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    base_dir = path.dirname(path.abspath(__file__))
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
