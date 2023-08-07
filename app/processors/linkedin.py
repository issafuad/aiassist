from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd
from db.db_client import DBIndex
from constants import SRC_PATH
from uuid import uuid4

LINKEDIN_FILES = [
    'Saved Posts _ LinkedIn10m.html',
    'Saved Posts _ LinkedIn-may-june-23.html',
    'Saved Posts _ LinkedIn 16June-16July.html'
]


def read_html_file(name):
    # Reading the file
    with open(f"{SRC_PATH}/data/{name}", "r", encoding='utf8') as f:
        contents = f.read()

    # print(contents[:10000])
    # Creating a BeautifulSoup object and specifying the parser
    S = BeautifulSoup(contents, 'html.parser')
    # print(S)

    elements = S.find_all(class_="entity-result__content-summary--3-lines")#class_starts_with_your_prefix)
    text = [e.text for e in elements]
    "t-black--light t-12"
    elements = S.find_all(class_="t-black--light t-12")
    dates = [e.text.strip('\n') for e in elements]

    elements = S.find_all(class_="entity-result__title-text t-16")
    names = [e.text.strip() for e in elements]

    out = list()
    for ind, each in enumerate(text):
        out.append({'date': dates[ind], 'text': each, 'name': names[ind]})
    return out


def get_chunks():
    file_names = LINKEDIN_FILES
    out_all = list()
    for name in file_names:
        for out_dict in read_html_file(name):
            out_dict['id'] = str(uuid4())
            out_dict['file_name'] = name
            out_all.append(out_dict)

    return out_all


def upload():
    out = get_chunks()
    df = pd.DataFrame(out)
    index = DBIndex(update=True, class_name='Linkedin')
    index.init()
    index.add_data(df)

