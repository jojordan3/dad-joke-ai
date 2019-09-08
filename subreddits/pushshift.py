'''Uses pushshift to pull data from farther back than Reddit allows us to go'''

import sys
import requests
import numpy as np
from datetime import datetime as dt
from dateutil import tz


joke_file_base = 'data_%%%%.csv'
record_file_base = 'data_%%%%.txt'
base_URL = 'https://api.pushshift.io/reddit/submission/search/?q=&size=1000&\
subreddit=%%%%&'


def _get_created_time(submission):
    try:
        created_utc = submission['created_utc']
    except KeyError:
        try:
            created_utc = submission['created']
        except:
            print(f'Error processing timestamp for\n{submission}')
            raise
    return int(created_utc)


def _retrieve_item(submission, key):
    try:
        return submission[key]
    except KeyError:
        return ''


def get_list(base_URL, how, UTC, sr):
    '''Get list of submissions, before or after previously recorded
    submissions.'''
    if how not in ['before', 'after']:
        while True:
            which = input('Please select [b] before or [a] after: ')
        if 'a' in which:
            how = 'after'
        elif 'b' in which:
            how = 'before'
        get_list(how, UTC)
    try:
        int(UTC)
    except ValueError:
        while True:
            UTC = input(f'Enter a valid UTC timestamp to search {how}: ')
    finally:
        response = requests.get(base_URL.replace('%%%%', sr) + f'{how}={int(UTC)}')
        try:
            data = response.json()['data']
        except:
            print(UTC)
            print(response)
            raise
        else:
            return data


def parse_joke(data, target, sr, parsed=None, num_subs=0):
    if not parsed:
        parsed = []
    for submission in data:
        try:
            subID = submission['id']
        except:
            print(submission)
            raise
        created = _get_created_time(submission)
        try:
            parents = submission['crosspost_parent_list']
        except KeyError:
            parent = None
            title = _clean_str(_retrieve_item(submission, 'title'))
            selftext = _clean_str(_retrieve_item(submission, 'selftext'))
        else:
            parent_post = parents[0]
            parent = _get_created_time(parent_post)
            title = _clean_str(_retrieve_item(parent_post, 'title'))
            selftext = _clean_str(_retrieve_item(parent_post, 'selftext'))
        finally:
            num_subs += 1
            author = _retrieve_item(submission, 'author')
            if target == 'sql':
                score = _retrieve_item(submission, 'score')
                comments = _retrieve_item(submission, 'num_comments')
                parsed.append([subID, created, parent, author, title, selftext,
                              score, comments])
            else:
                score = str(_retrieve_item(submission, 'score'))
                comments = str(_retrieve_item(submission, 'num_comments'))
                with open(joke_file_base.replace('%%%%', sr), 'a') as jk, open(
                        record_file_base.replace('%%%%', sr), 'a') as rec:
                    jk.write('|'.join([subID, str(created), str(parent),
                                       author, title, selftext, score,
                                       comments]) + '\n')
                    rec.write(str(created) + '\n')
    return created, parsed, num_subs


def get_cutoff(how):
    if how not in ['before', 'after']:
        while True:
            which = input('Please select [b]before or [a]after: ')
        if 'a' in which:
            how = 'after'
        elif 'b' in which:
            how = 'before'
    utcs = []
    with open(record_file_base, 'r') as rec_file:
        for line in rec_file:
            utcs.append(int(line))
    utcs.sort()
    if how == "before":
        cutoff = utcs[0]
    elif how == "after":
        cutoff = utcs[-1]
    return cutoff


def _clean_str(val):
    val = val.replace('"', "'")
    new_val = val.replace('|', '^')
    return _make_repr(new_val)


def _make_repr(val):
    rep = repr(val)[1:-1]
    return '"' + rep + '"'


if __name__ == "__main__":
    try:
        subreddit = sys.argv[1]
    except:
        while True:
            subreddit = input(f'Which subreddit would you like to search? ')
    finally:
        UTC = int(dt.utcnow().timestamp())
        num_subs = 1000
        while num_subs == 1000:
            data = get_list(base_URL, 'before', UTC, subreddit)
            UTC, parsed, num_subs = parse_joke(data, 'csv', subreddit)
            last_datetime = dt.fromtimestamp(UTC, tz=tz.tzutc())
            time_str = last_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print(f'{num_subs} jokes, ending at {time_str} (UTC: {str(UTC)})')
