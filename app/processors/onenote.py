import os
import glob
from bs4 import BeautifulSoup
from constants import SRC_PATH
import pandas as pd

from db.db_client import DBIndex


def read_and_chunk_html_files(root_folder, max_chunk_size):
    root_folder = str(root_folder)
    chunks_list = []
    id_counter = 0

    target = root_folder + '/**/*.html'
    print(target)
    for filepath in glob.glob(target, recursive=True):
        relative_path = os.path.relpath(filepath, root_folder)

        with open(filepath, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
            text = soup.get_text()
            words = text.split()
            chunks = [words[i:i + max_chunk_size] for i in range(0, len(words), max_chunk_size)]

        for i, chunk in enumerate(chunks):
            chunk_id = id_counter
            chunk_location = '/'.join(relative_path.split(os.sep)[:-1]) + ' - Chunk ' + str(i+1)
            chunk_text = ' '.join(chunk)

            chunk_dict = {'id': chunk_id, 'chunk': chunk_location, 'text': chunk_text}
            chunks_list.append(chunk_dict)

            id_counter += 1

    return chunks_list


def upload():
    # specify the root folder to read HTML files
    chunks = read_and_chunk_html_files(SRC_PATH / 'data/output/', 2500)
    df = pd.DataFrame(chunks)
    index = DBIndex(update=True, class_name='Onenote')
    index.init()
    index.add_data(df)
    return


