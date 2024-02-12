import argparse
import glob
import json
import logging
import os
from os import path
from urllib.parse import urljoin

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

INDEX_PAGES_FOLDER_NAME = 'pages'
BOOKS_ON_THE_PAGE = 8


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Генератор страниц сайта из библиотеки www.tululu.org"
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


def remove_html():
    html = glob.glob(f'{INDEX_PAGES_FOLDER_NAME}/*.html', recursive=False)
    for file_name in html:
        os.remove(file_name)


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
        books = json.load(json_file)

    for item_path in books:
        item_path['img_path'] = urljoin(general_folder + os.sep, str(item_path['img_path']))
        item_path['book_path'] = urljoin(general_folder + os.sep, str(item_path['book_path']))

    os.makedirs(os.path.join(os.getcwd(), INDEX_PAGES_FOLDER_NAME), mode=0o777, exist_ok=True)
    books_by_group = list(chunked(books, BOOKS_ON_THE_PAGE))
    for num_page, books in enumerate(books_by_group, 1):
        rendered_page = template.render(books=chunked(books, 2), number_pages=len(books_by_group), current_page=num_page)
        index_file_name = os.path.join(INDEX_PAGES_FOLDER_NAME, f'index{num_page}.html')
        with open(index_file_name, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d - %(levelname)-8s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    base_dir = path.dirname(path.abspath(__file__))
    remove_html()
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
