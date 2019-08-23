'''Analyzing reddit jokes for likes, comments, medals'''
import numpy as np
import pandas as pd
# from sklearn import


csv_path = '/Users/joannejordan/Desktop/GitHub/dad-joke-ai/dadjokes-subreddit-\
archive/pushshift.csv'

dj = pd.read_csv(csv_path)
dj.drop(columns=['NA'], inplace=True)
dj.apply()
