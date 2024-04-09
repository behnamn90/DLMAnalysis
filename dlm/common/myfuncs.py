import os
import shutil
import errno
import pandas as pd


def pickled_df(path):
    df = pd.read_pickle(path)
    return df
'''
def pickled_df(path):
    successful = False
    df = None
    while not successful:
        try:
            df = pd.read_pickle(path)
            successful = True
        except:
            successful = False
    return df
'''
def load_temp_file(key):
    filepath = 'TempFiles/' + key + '.p'
    exists = False
    df = None
    if os.path.exists(filepath):
        df = pickled_df(filepath)
        exists = True
    return exists, df
def save_temp_file(df,key):
    filepath = 'TempFiles/' + key + '.p'
    df.to_pickle(filepath)

class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
        
    def __enter__(self):
        self.savedPath = os.getcwd()
        if not os.path.exists(self.newPath):
            os.makedirs(self.newPath)
        os.chdir(self.newPath)
        
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def copy_dir(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def hill_func(x, n, K):
    return 1 / (1 + pow((x / K), n))


def linear_func(x, m, c):
    return (m * x) + c

def linear_func1(x, m, x0):
    return 1 + (m * (x-x0))

def circ_subtract(a,b,high):
    if (a>high):
        print("ERROR: circular substraction with a>max!")
    if (b>high):
        print("ERROR: circular substraction with b>max")
    result = ( (a % high) - (b % high) ) % high;
    if result < 0: result+=high
    return result


def circ_dist(p1,p2,high):
    if (p1>high):
        print("ERROR: circular substraction with a>max!")
    if (p2>high):
        print("ERROR: circular substraction with b>max")
    a1 = ((high + p1 - p2) % high) +1
    a2 = ((high + p2 - p1) % high) +1
    if a1<a2: result = a1
    else: result = a2
    return result


def circ_add(p1, p2, high):
    if p1>high or p2>high: print('Error: circ_add() with a or b > max!')
    return (p1+p2) % high