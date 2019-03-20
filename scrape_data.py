from bs4 import BeautifulSoup as bsoup
import requests
import re
from lxml import html


def get_icanhaz():
    base_url = 'https://icanhazdadjoke.com/search'
    r = requests.get(base_url)

    last_page = 0

    soup = bsoup(r.content, 'lxml')
    # Get page numbers in search
    for a in soup.findAll('a', class_='pagination-link '):
        last_page = max(last_page, int(a.text))

    dad_jokes = []

    for i in list(range(1, last_page + 1)):
        url = base_url + f'?term=&page={i}'
        r = requests.get(url)
        soup = bsoup(r.content, 'lxml')
        for pre in soup.findAll('pre', style=True):
            dad_jokes.append(pre.text)

    return dad_jokes

if __name__ == "__main__":
    dj = get_icanhaz()

    with open('icanhaz.csv', 'a') as f:
        for line in dj:
            f.write(line)
