import pandas as pd
import re
import psycopg2
import sys

from subreddits.pushshift import *
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

joke_file_base = 'data_%%%%.csv'
record_file_base = 'data_%%%%.txt'
base_URL = 'https://api.pushshift.io/reddit/submission/search/?q=&size=1000&\
subreddit=%%%%&'

score_cats = [1, 5, 20, 100]
comment_cats = [1, 3, 10, 50]
newlines = re.compile(r'(\\n)+')


def _gettext(s):
    s = s.replace('&amp;#x200B;', '')
    s = s.replace('&amp;', 'and')
    s = newlines.sub(' ', s)
    return s


def prepare_text(data):
    data.title.fillna('', inplace=True)
    data.selftext.fillna('', inplace=True)
    data['title_clean'] = data.title.apply(_gettext)
    data['selftext_clean'] = data.selftext.apply(_gettext)
    data['score_cat'] = data.score.apply(lambda _: _categorize(_, score_cats))
    data['comment_cat'] = data.comments.apply(
        lambda _: _categorize(_, comment_cats))
    data['createdUTC'] = data.createdUTC.apply(
        lambda x: dt.fromtimestamp(x, tz.utc))
    return data


def _categorize(val, cutoffs):
    for level, upper_bound in enumerate(cutoffs):
        if val < upper_bound:
            return level
    return len(cutoffs)


def _create_table(cur, sr):
    cur.execute(f"""CREATE TABLE {sr} (
        postid          varchar(8) PRIMARY KEY,
        created         timestamptz,
        prev_created    varchar(20),
        author          varchar(40),
        title           text,
        selftext        text,
        score           int,
        comments        int,
        scorecat        smallint,
        commentcat      smallint);""")


def _add_rows(conn, sr, ordered_vals):
    with conn.cursor() as cur:
        data_str = b','.join([cur.mogrify(
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            v) for v in ordered_vals]).decode()
        cur.execute(f"""INSERT INTO {sr}
            (postid, created, prev_created, author, title, selftext, score,
            comments, scorecat, commentcat) VALUES """ + data_str + ';')
    conn.commit()


def _update_rows(conn, sr, ordered_vals):
    with conn.cursor() as cur:
        cur.execute("""CREATE TEMP TABLE tempvals(
            postid          varchar(8),
            score           int,
            comments        int,
            scorecat        smallint,
            commentcat      smallint);""")
        data_str = b','.join(cur.mogrify(
            "(%s, %s, %s, %s, %s)", v) for v in ordered_vals).decode()
        cur.execute(f"""INSERT INTO tempvals (
            postid, score, comments, scorecat, commentcat)
            VALUES """ + data_str +';')
        cur.execute(f"""UPDATE {sr} j
            SET (score, comments, scorecat, commentcat) =
            (SELECT score, comments, scorecat, commentcat
            FROM tempvals t WHERE t.postid = j.postid);""")
    conn.commit()


def read_or_create_table(sr):
    with psycopg2.connect('dbname=postgres user=postgres') as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"SELECT MAX(created) FROM {sr};")
            except psycopg2.Error:
                conn.rollback()
                _create_table(cur, sr)
                conn.commit()
                last_post_time = None
            else:
                last_post_time = cur.fetchone()[0]
    conn.close()
    return last_post_time


def update_db(sr, start=None):
    try:
        ago = (start - td(days=100))
        UTC = int(ago.replace(tzinfo=tz.utc).timestamp())
    except:
        UTC = int(1319397000)
    num_subs = 1000
    while num_subs == 1000:
        data = get_list(base_URL, 'after', UTC, sr)
        UTC, parsed, num_subs = parse_joke(data, 'sql', sr)
        df = pd.DataFrame(data=parsed, index=None, columns=[
            'id', 'createdUTC', 'parent_createdUTC', 'author',
            'title', 'selftext', 'score', 'comments'
            ])
        df = prepare_text(df)
        with psycopg2.connect("dbname=postgres user=postgres") as conn:
            with conn.cursor() as cur:
                q = cur.mogrify(f"""SELECT postid, score, comments, scorecat,
                            commentcat FROM {sr} WHERE  postid IN %s;""",
                            (tuple(df.id.values),))
                cur.execute(q)
                to_update = []
                try:
                    overlap = cur.fetchall()
                except:
                    pass
                else:
                    repeat_rows = df.id.isin([i[0] for i in overlap])
                    sec = [tuple(x) for x in df[repeat_rows][[
                            'id', 'score', 'comments', 'score_cat', 'comment_cat']].values]
                    if len(sec) > 0:
                        to_update = []
                        for i, row in enumerate(sec):
                            if list(overlap[i]) != row:
                                to_update.append(row)
                        if len(to_update) > 0:
                            _update_rows(conn, sr, to_update)
                    df = df.drop(index=df[repeat_rows].index)
                finally:
                    ordered_vals = df.apply(lambda row: tuple(
                        row[['id', 'createdUTC', 'parent_createdUTC', 'author',
                             'title_clean', 'selftext_clean', 'score', 'comments',
                             'score_cat', 'comment_cat']]), axis=1)
                    if len(df) > 0:
                        _add_rows(conn, sr, ordered_vals)
        conn.commit()
        conn.close()
        last_datetime = dt.fromtimestamp(UTC, tz.utc)
        time_str = last_datetime.strftime('%Y-%m-%d %H:%M:%S')
        print(f'Updated {len(to_update)}, Added {len(df)}, End {time_str} (UTC: {str(UTC)})')


if __name__ == "__main__":
    try:
        subreddit = sys.argv[1]
    except:
        while True:
            subreddit = input(f'Which subreddit would you like to search? ')
    finally:
        time_s = read_or_create_table(subreddit)
        update_db(subreddit, start=time_s)
