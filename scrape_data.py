'''
Scrape data from icanhazdadjoke
'''
import requests
from bs4 import BeautifulSoup as bsoup


def get_icanhaz():
    '''
    Get all dadjokes from website
    Returns
    ---------------------------------
    dad_jokes : list
        list of strings
    '''
    base_url = 'https://icanhazdadjoke.com/search'
    r = requests.get(base_url)

    last_page = 0

    soup = bsoup(r.content, 'lxml')
    # Get page numbers in search
    for a in soup.findAll('a', class_='pagination-link '):
        last_page = max(last_page, int(a.text))

    dad_jokes = []

    # Loop through pages to get dadjokes
    for i in list(range(1, last_page + 1)):
        url = base_url + f'?term=&page={i}'
        r = requests.get(url)
        soup = bsoup(r.content, 'lxml')
        for pre in soup.findAll('pre', style=True):
            dad_jokes.append(pre.text)

    return dad_jokes

if __name__ == "__main__":
    DJ = get_icanhaz()

    with open('icanhaz.csv', 'a') as f:
        for line in DJ:
            f.write(' '.join(line.split()))
            f.write('\n')
