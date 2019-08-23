'''Analyzing reddit jokes for likes, comments'''
import numpy as np
import pandas as pd
# from sklearn import


csv_path = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-subreddit-\
archive/data_redditdadjokes.csv'

dj = pd.read_csv(csv_path, na_values='[deleted]')
