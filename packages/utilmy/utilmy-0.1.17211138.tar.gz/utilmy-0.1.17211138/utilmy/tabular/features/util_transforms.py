# drop_transformer.py
from numpy import ndarray
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_drop):
        self.columns_to_drop = columns_to_drop

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.columns_to_drop, axis=1)

    def get_feature_names_out(self, input_features=None):
        # Return the feature names after dropping specified columns
        print(self.columns_to_drop, input_features)
        return [col for col in input_features if col not in self.columns_to_drop]







# groupby_transformer.py
from numpy import ndarray
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

class GroupByTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, group_cols, cols_D, window, min_periods=1, label=''):
        self.group_cols = group_cols
        self.cols_D = cols_D
        self.window = window
        self.min_periods = min_periods
        self.new_column_names = []
        self.label = label

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        new_cols = [col + self.label for col in self.cols_D]
        self.new_column_names = new_cols
        X[new_cols] = X.groupby(self.group_cols)[self.cols_D].transform(lambda x: x.rolling(window=self.window, min_periods=self.min_periods).mean())
        return X

    def get_feature_names_out(self, input_features=None):
        return self.new_column_names





# groupby_transformer.py
from numpy import ndarray
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

class LagTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, leak_cols, lags):
        self.leak_cols = leak_cols
        self.lags = lags
        self.new_column_names = []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for column in self.leak_cols:
            X[column + '_lags'] = X[column].shift(self.lags)
            self.new_column_names.append(column + '_lags')
        return X

    def get_feature_names_out(self, input_features=None):
        return self.new_column_names




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()










