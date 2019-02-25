import re
import pandas as pd
import json
import os
import time
import sys


# def progressbar(obj_length, i, current, step):
#    width = 55
#    if i == 0:
#        sys.stdout.write(f"Step {step} Progress: [>{' ' * (width - 1)}] 0.0%")
#        sys.stdout.flush()
#        sys.stdout.write('\b' * 4)
#        progress = 0
#    else:
#        progress = int(width * i / obj_length)
#        percent = i * 100 / obj_length
#        if progress > current:
#            sys.stdout.write('\r')
#            sys.stdout.write(f"Step {step} Progress: \
# [{'=' * progress}>{' ' * (width - progress - 1)}] {percent:.1f}%")
#            sys.stdout.flush()
#        else:
#            sys.stdout.write(f'{percent:.1f}%')
#            sys.stdout.flush()
#        sys.stdout.write('\b' * len(f'{percent:.1f}%'))
#    i += 1
#    return i, progress


def filter_jokes(data):
    r_dadjokes = []

    tracker_l = len(data)
    i = 0
    progress = 0
    width = 55

    sys.stdout.write(f"Step {step} Progress: [>{' ' * (width - 1)}] 0.0%")
    sys.stdout.flush()
    sys.stdout.write('\b' * 4)

    while data:
        current = int(width * i / tracker_l)
        percent = i * 100 / tracker_l
        if progress < current:
            sys.stdout.write('\r')
            sys.stdout.write(f"Step {step} Progress: \
[{'=' * progress}>{' ' * (width - progress - 1)}] {percent:.1f}%")
            sys.stdout.flush()
            progress = current
        else:
            sys.stdout.write(f'{percent:.1f}%')
            sys.stdout.flush()
        sys.stdout.write('\b' * len(f'{percent:.1f}%'))
        i += 1

        submission = data.pop(0)

        if 't5_2t0no' in submission:
            joke = json.loads(submission)
            if joke['selftext']:
                if 'https://' in joke['selftext']:
                    continue
                else:
                    a = re.sub(r'\w* edit.*', '', joke['selftext'],
                               flags=re.I | re.M)
                    submission = f'Q: {joke["title"]}\nA: {a}'
            else:
                submission = str(joke['title'])
            r_dadjokes.append([joke['id'], submission, joke['score'],
                               joke['num_comments'], joke['created_utc']])

    del data

    return r_dadjokes


if __name__ == "__main__":
    filename = input('filename: ')
    dadjokes = 'dadjokes.csv'
    with open(filename, 'r') as f:
        data = f.readlines()

    print("""
Step 1: Read File -- Completed
----------------------------------------""")
    os.remove(filename)

    r_dadjokes = filter_jokes(data)
    n_jokes = len(r_dadjokes)

    print(f"""\nStep 2: Filter Jokes -- Completed
    with {n_jokes} found
----------------------------------------\n""")
    sys.stdout.flush()

    dadjoke_df = pd.DataFrame(data=r_dadjokes,
                              columns=['id', 'joke', 'score', 'num_comments',
                                       'created']).set_index('id')

    del r_dadjokes

    print("""\n   Configure Dad Jokes -- Completed
----------------------------------------""")

    before = os.path.getsize(dadjokes)

    with open(dadjokes, 'a') as archive:
        archive.write(dadjoke_df.to_csv(header=False))

    after = os.path.getsize(dadjokes)

    print(f"""{len(dadjoke_df)} lines added
----------------------------------------
{dadjoke_df.iloc[:3]}
...
{dadjoke_df.iloc[-3:]}
----------------------------------------
dadjokes increased by {after-before} bytes with the following data
dadjokes total size: {after}
data added from {filename}""")
    print("----------------Success!----------------")

del dadjoke_df
