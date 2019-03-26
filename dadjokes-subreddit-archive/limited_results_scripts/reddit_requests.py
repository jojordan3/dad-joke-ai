'''
Using Reddit's api/v1/
'''
import os
import requests
import requests.auth
import sys
import time
from local_settings import *
from reddit_api import write_joke


# Files to read and write
jokes = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-subreddit-\
archive/otherrjokes.csv'
records = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-subreddit-\
archive/otherrecords.txt'

# Set reddit user agent
user_agent = f"{USER_AGENT} by {USERNAME}"


def get_auth():
    '''Get authorization to use reddit's api
    '''
    # Steps presented in reddit's docs
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "password", "username": USERNAME,
                 "password": PASSWORD}
    headers = {"User-Agent": user_agent}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth, data=post_data, headers=headers)
    text = response.json()
    print(text)
    authorization = text['token_type'] + ' ' + text['access_token']
    # Save authorization to file
    variables = []
    # First, read old file
    with open('local_settings.py', 'r') as local:
        for line in local:
            variables.append(line)
    # Overwrite old file
    with open('local_settings.py', 'w') as local:
        for line in variables[:-1]:
            local.write(line + '\n')
        local.write('AUTH = {authorization}')
    return authorization


def get_jokes_page(after):
    '''Requests jokes through reddit's online API, sidestepping PRAW's limit
    on the history of the instance
    '''
    # See if old authorization works
    headers = {'Authorization': AUTH, 'User-Agent': user_agent}
    page = requests.get(f'https://oauth.reddit.com/r/dadjokes/new.json?\
limit=100&after={after}', headers=headers).json()
    try:
        if page['error'] == 401:
            # Get new authorization
            authorization = get_auth()
            headers = {'Authorization': authorization,
                       'User-Agent': user_agent}
            page = requests.get(f'https://oauth.reddit.com/r/dadjokes/new.json?\
limit=100&after={after}', headers=headers).json()
        elif page['error'] == 429:
            sys.stdout('Too Many Requests. Waiting...\n')
            sys.stdout.flush()
            for t in range(len(75)):
                if t % 5 == 0:
                    sys.stdout('{15 + (t - 75) // 15} seconds')
                    sys.stdout('\r')
                    sys.stdout.flush()
                time.sleep(.2)
            print('Resuming')
            get_jokes_page(after)
    except:
        pass
    return page


def record_jokes(page, last):
    '''Writes joke information to files.
    '''
    # Size of original file with jokes to compare to final and return
    # error if nothing added
    orig = os.path.getsize(jokes)
    # Ensure object is indeed a listing, otherwise, check if 429 error.
    # If 429 error, wait and repeat. Otherwise, raise error
    try:
        listing = page['data']['children']
        after = page['data']['after']
        before = page['data']['before']
    except:
        print(page)
        raise
    else:
        with open(jokes, 'a') as joke_file:
            for submission in listing:
                sub_data = submission['data']
                write_joke(sub_data, joke_file, 'requests')
            new = os.path.getsize(jokes)
            if new == orig:
                raise ValueError('Nothing added')
        with open(records, 'a') as rec:
            rec.write(f'After: {after}\n')
        return after


def get_last():
    final = None
    with open(records, 'r') as rec:
        for line in rec:
            final = line.split()[-1]
    return final


if __name__ == "__main__":
    last = get_last()
    i = 1
    if not last:
        page = get_jokes_page(None)
        prev = record_jokes(page, None)
        print(f'Recorded page {i} with last submission: {prev}')
        last = prev
        i += 1

    while last:
        try:
            page = get_jokes_page(last)
            prev = record_jokes(page, last)
            print(f'Recorded page {i} with last submission: {prev}')
            last = prev
            i += 1
        except:
            error = True
            raise
