import praw
import time
import sys


data_col = ['id', 'created_utc', 'title', 'selftext', 'score', 'upvote_ratio',
            'gilded', 'over_18', 'num_comments']
gildings = ['gid_1', 'gid_2', 'gid_3']
r = praw.Reddit()


def write_joke(submission, jokes):
    medals = submission.gildings
    author = submission.author
    sub_vars = vars(submission)
    data = [sub_vars[i] if i in sub_vars else '' for i in data_col]
    data.append(author.name)
    data.extend([medals[g] for g in gildings])
    jokes.write(str(data)[1:-1] + '\n')


def next_batch(how='after', last=None):
    batch = r.subreddit('dadjokes').new(params={how: last})
    with open('rdadjokes.csv', 'a') as jokes, open('records.txt',
                                                   'a') as records:
        i = 0
        width = 55
        progress = 0
        sys.stdout.write(f"Progress: [>{' ' * (width - 1)}] 0%")
        sys.stdout.flush()
        sys.stdout.write('\b' * 2)

        for submission in batch:
            current = int(width * i / 100)
            if progress < current:
                sys.stdout.write('\r')
                sys.stdout.write(f"Progress: \
[{'=' * progress}>{' ' * (width - progress - 1)}] {i}%")
                sys.stdout.flush()
                progress = current
            else:
                sys.stdout.write(f'{i}%')
                sys.stdout.flush()
            sys.stdout.write('\b' * len(f'{i}%'))

            if i == 0:
                records.write(submission.id + ' to ')
            elif i == 99:
                last = submission.id
                records.write(last + '\n')
            write_joke(submission, jokes)
            i += 1
    return last

# LIMIT TO 1 TODO

if __name__ == "__main__":
    if len(sys.argv) > 1:
        last = next_batch(how=sys.argv[1], last=sys.argv[2])
    else:
        last = next_batch()
    print(f'Recorded up to {last}')
