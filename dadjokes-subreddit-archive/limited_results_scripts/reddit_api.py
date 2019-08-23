'''Initial pull from subreddit'''
import praw
import time
import sys
import os
from ..write_joke import write_joke

r = praw.Reddit('')


def next_batch(how='before', last=None):
    batch = r.subreddit('dadjokes').new(params={how: last})
    orig = os.path.getsize('/Users/joannejordan/Desktop/GitHub/dad-joke-ai/\
dadjokes-subreddit-archive/rdadjokes.csv')
    with open('rdadjokes.csv', 'a') as jokes, open('records.txt',
                                                   'a') as records:
        i = 0
        for submission in batch:
            if i == 0:
                records.write(f't3_{submission.id} to ')
            else:
                last = f't3_{submission.id}'
            write_joke(submission, jokes, 'PRAW')
            i += 1
            time.sleep(1)
        new = os.path.getsize('/Users/joannejordan/Desktop/GitHub/dad-joke-ai/\
dadjokes-subreddit-archive/rdadjokes.csv')
        if new == orig:
            raise ValueError('Nothing added')
        records.write(last + '\n')
    return last


if __name__ == "__main__":
    error = False
    batch_ = 1
    while not error:
        if batch_ == 1:
            try:
                if len(sys.argv) > 1:
                    last = next_batch(how=sys.argv[1], last=sys.argv[2])
                else:
                    last = next_batch(how='before', last=last)
                batch_ += 1
            except:
                print('Error in first batch')
                raise
        else:
            try:
                last = next_batch(how='after', last=last)
                print(
                    f'Recorded batch#{batch_} with last submission: {last}\n')
                batch_ += 1
            except KeyboardInterrupt:
                print(f'\nRecorded up to {last}\n')
                error = True
            except:
                error = True
                print(f'\nError processing batch {batch_}\n')
                raise
