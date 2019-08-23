'''Uses pushshift to pull data from farther back than Reddit allows us to go'''
import json
import os
import requests
import sys
from write_joke import write_joke
from datetime import datetime as dt
from dateutil import tz


joke_file = '/Users/joannejordan/Desktop/dad-joke-ai/dadjokes-subreddit-\
archive/data_redditdadjokes.csv'
record_file = '/Users/joannejordan/Desktop/dad-joke-ai/dadjokes-subreddit-\
archive/data_redditdadjokes.txt'
base_URL = 'https://api.pushshift.io/reddit/submission/search/?q=&size=500&\
subreddit=dadjokes&'
data_cols = ['author', 'author_fullname', 'title', 'selftext', 'score',
             'num_comments']
dadjokes_created_utc = 1319375605


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


def get_list(how, UTC):
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
        response = requests.get(base_URL + how + '=' + str(UTC))
        try:
            data = response.json()['data']
        except:
            print(UTC)
            print(response)
            raise
        else:
            orig = os.path.getsize(joke_file)
            i = 0
            with open(joke_file, 'a') as jk, open(record_file, 'a') as rec:
                for submission in data:
                    try:
                        sub_id = submission['id']
                    except:
                        print(submission)
                        raise
                    created_utc = _get_created_time(submission)
                    try:
                        parents = submission['crosspost_parent_list']
                    except KeyError:
                        parent_UTC = 'N/A'
                    else:
                        parent_post = parents[0]
                        parent_UTC = _get_created_time(parent_post)
                    try:
                        jk.write(','.join([sub_id, str(created_utc),
                                           str(parent_UTC)]) + ',')
                        write_joke(submission, jk, 'requests',
                                   data_col=data_cols)
                    except:
                        print(submission)
                        raise
                    else:
                        rec.write(str(created_utc) + '\n')
                        i += 1
            new = os.path.getsize(joke_file)
            if new == orig:
                raise ValueError('Nothing Added')
            return created_utc, i


def get_cutoff(how):
    if how not in ['before', 'after']:
        while True:
            which = input('Please select [b]before or [a]after: ')
        if 'a' in which:
            how = 'after'
        elif 'b' in which:
            how = 'before'
    utcs = []
    with open(record_file, 'r') as rec_file:
        for line in rec_file:
            utcs.append(int(line))
    utcs.sort()
    if how == "before":
        cutoff = utcs[0]
    elif how == "after":
        cutoff = utcs[-1]
    return cutoff


if __name__ == "__main__":
    try:
        how = sys.argv[1]
    except:
        how = 'before'
    try:
        UTC = sys.argv[2]
    except:
        try:
            UTC = get_cutoff(how)
        except:
            UTC = int(dt.utcnow().timestamp())
    finally:
        while UTC > dadjokes_created_utc:
            UTC, num = get_list(how, UTC)
            last_datetime = dt.fromtimestamp(UTC, tz=tz.tzutc())
            time_str = last_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print(f'Wrote {num} jokes, ending at {time_str} (UTC: {str(UTC)})')
