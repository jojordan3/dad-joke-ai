'''Uses pushshift to pull data from farther back than Reddit allows us to go'''
import json
import os
import requests
import sys
from write_joke import write_joke
from datetime import datetime as dt
from dateutil import tz


joke_file = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-subreddit-\
archive/pushshift.csv'
record_file = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-\
subreddit-archive/pushshift.txt'
base_URL = 'https://api.pushshift.io/reddit/search/submission/?q=&size=500&\
subreddit=dadjokes&'
data_cols = ['title', 'selftext', 'author', 'score', 'over_18', 'num_comments']
dadjokes_created_utc = 1319375605


def get_list(how, UTC):
    '''Get list of submissions'''
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
            print(URL)
            print(response)
            raise
        else:
            orig = os.path.getsize(joke_file)
            i = 0
            with open(joke_file, 'a') as jk, open(record_file, 'a') as rec:
                for submission in data:
                    try:
                        sub_id = "t3_" + submission['id']
                    except:
                        print(submission)
                        raise
                    try:
                        created_utc = submission['created_utc']
                    except KeyError:
                        try:
                            created_utc = submission['created']
                        except:
                            raise
                    except:
                        print('Error processing timestamp for t3_' +
                              str(submission['id']))
                        print(submission)
                        raise
                    try:
                        jk.write(','.join([sub_id, str(created_utc)]) + ',')
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
    if how == "after":
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
            UTC = get_cutoff(arg1)
        except:
            UTC = int(dt.utcnow().timestamp())
    finally:
        while UTC > dadjokes_created_utc:
            UTC, num = get_list(how, UTC)
            last_datetime = dt.fromtimestamp(UTC, tz=tz.tzutc())
            time_str = last_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print(f'Wrote {num} jokes, ending at {time_str} (UTC: {str(UTC)})')
