'''Write jokes to csv'''
import praw
import string

data_col_PRAW = ['id', 'created_utc', 'title', 'selftext', 'score',
                 'upvote_ratio', 'gilded', 'over_18', 'num_comments']
data_col_req = ['name', 'created_utc', 'title', 'selftext', 'author',
                'score', 'downs', 'ups', 'over_18', 'num_comments']


def write_joke(submission, jokes, how, data_col=None, parent=None):
    '''
    Write jokes to csv

    parameters
    -------------------------------
    submission : object
        either a JSON object --> dictionary if how is "requests" or
        a reddit/praw submission object if how is "PRAW"
    jokes : str
        filepath to csv file to append data
    how : str
        either "PRAW" or "requests"
    data_col : list
        list of strings designating the features to be taken from the
        submission object - varies depending on usage
    '''
    if how == 'PRAW':
        data_col = data_col_PRAW
    elif how == 'requests':
        if not data_col:
            data_col = data_col_req
    else:
        raise ValueError('how must be either "PRAW" or "requests"')
    try:
        if how == "PRAW":
            author = submission.author
            s_vars = vars(submission)
            data = [s_vars[i] if i in s_vars else 'N/A' for i in data_col]
            try:
                data.append(author.name)
            except AttributeError:
                data.append('')
        else:
            data = []
            for col in data_col:
                try:
                    if col in ['title', 'selftext']:
                        if parent:
                            data.append(_clean_str(parent[col]))
                        else:
                            data.append(_clean_str(submission[col]))
                    else:
                        data.append(str(submission[col]))
                except:
                    data.append('')
            jokes.write('|'.join(data) + '\n')
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
                    pass
        finally:
            print(submission)
            raise


def _clean_str(val):
    val = val.replace('"', "'")
    new_val = val.replace('|', '^')
    return _make_repr(new_val)


def _make_repr(val):
    rep = repr(val)[1:-1]
    return '"' + rep + '"'
