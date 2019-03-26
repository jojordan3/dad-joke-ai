'''Write jokes to csv'''
import praw

data_col_PRAW = ['id', 'created_utc', 'title', 'selftext', 'score',
                 'upvote_ratio', 'gilded', 'over_18', 'num_comments']
data_col_req = ['name', 'created_utc', 'title', 'selftext', 'author',
                'score', 'downs', 'ups', 'over_18', 'num_comments']
gild = ['gid_1', 'gid_2', 'gid_3']


def write_joke(submission, jokes, how, data_col=None):
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
                    print(submission)
        finally:
            raise
