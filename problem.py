import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import pandas as pd
import numpy as np
import rampwf as rw
from data_cleaning import fix_categorical_features_dtype
from itertools import combinations_with_replacement
from sklearn.model_selection import ShuffleSplit
from rampwf.score_types.base import BaseScoreType
from sklearn.metrics import balanced_accuracy_score

split_factor = 0.2

problem_title = 'Covid Vaccince Prediction'

_target_names = ['Vaccine', 'Business']

_prediction_label_ = combinations_with_replacement(
                                ['Completely disagree', 
                                'Somewhat disagree', 
                                'No opinion', 
                                'Completely agree', 
                                'Somewhat agree'],2)

Predictions = rw.prediction_types.make_regression(label_names=_target_names)
workflow = rw.workflows.Regressor()


class BAS(BaseScoreType):
    is_lower_the_better = True
    minimum = 0.0
    maximum = float("inf")

    def __init__(self, name="BAS", precision=4):
        self.name = name
        self.precision = precision

    def __call__(self, y_true, y_pred):
        BAS_1 = np.mean(y_true[0] == y_pred[0])
        BAS_2 = np.mean(y_true[1] == y_pred[1])
        return (BAS_1+BAS_2)/2



score_types = [
    BAS(name="BAS"),
]

def get_cv(X, y):
    cv = ShuffleSplit(n_splits=10, test_size=0.25, random_state=57)
    return cv.split(X, y)

def _get_data(path, split='train'):
    data_path = os.path.join(path, "data", "data.csv")

    data = pd.read_csv(data_path, encoding='iso-8859-1', index_col=0, na_values=' ')  # XXX rmv index_col=0 if ever needed
    
    if split == 'train':
        idx = np.random.permutation(data.shape[0])
        train_split = int(data.shape[0]*(1-split_factor))
        idx = idx[:train_split]
        data = data.iloc[idx].reset_index(drop=True)

    if split == 'test':
        idx = np.random.permutation(data.shape[0])
        train_split = int(data.shape[0]*(1-split_factor))
        idx = idx[train_split:]
        data = data.iloc[idx].reset_index(drop=True)


    X = data.drop(['Vaccine','Business2'], axis=1)
    Y = data[['Vaccine','Business2']]
    return X.to_numpy(), Y.to_numpy()

def get_train_data(path):
    return _get_data(path, 'train')

def get_test_data(path):
    return _get_data(path, 'test')




