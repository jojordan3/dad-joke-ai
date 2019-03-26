import praw
import time
import sys
import os

data_col_PRAW = ['id', 'created_utc', 'title', 'selftext', 'score',
                 'upvote_ratio', 'gilded', 'over_18', 'num_comments']
data_col_req = ['name', 'created_utc', 'title', 'selftext', 'author',
                'score', 'downs', 'ups', 'over_18', 'num_comments']
gild = ['gid_1', 'gid_2', 'gid_3']
r = praw.Reddit('')


def write_joke(submission, jokes, how, data_col=None):
    if how == 'PRAW':
        data_col = data_col_PRAW
    elif how == 'requests':
        if not data_col:
            data_col = data_col_req
    else:
        raise ValueError('how must be either "PRAW" or "requests"')
    try:
        if how == "PRAW":
            medals = submission.gildings
            author = submission.author
            s_vars = vars(submission)
            data = [s_vars[i] if i in s_vars else '' for i in data_col]
            try:
                data.append(author.name)
            except AttributeError:
                data.append('')
        elif how == "requests":
            try:
                medals = submission['gildings']
            except:
                medals = {}
                for g in gild:
                    medals[g] = 0
            finally:
                data = []
                for col in data_col:
                    try:
                        data.append(submission[col])
                    except KeyError:
                        data.append('')
        data.extend([medals[g] for g in gild])
        jokes.write(str(data)[1:-1] + '\n')
    except:
        try:
            print(f'\nError processing t3_{submission.id}\n')
        except:
            try:
                print(f'\nError processing {submission["name"]}\n')
            except:
                try:
                    print(f'\nError processing t3_{submission["id"]}\n')
                except:
                    raise
        finally:
            raise


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
