import pandas as pd

def my_max(x):
    try:
        return max(x)
    except:
        return x
def my_min(x):
    try:
        return min(x)
    except:
        return x
def my_sum(x):
    try:
        return sum(x)
    except:
        return x
def my_len(x):
    try:
        return len(x)
    except:
        return 1

from random import choice
def my_mode(self):
    return choice(list(pd.Series.mode(self)))