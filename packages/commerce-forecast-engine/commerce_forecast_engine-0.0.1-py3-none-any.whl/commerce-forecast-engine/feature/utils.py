from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from multiprocessing import cpu_count
from joblib import Parallel
from joblib import delayed
import pandas as pd
from functools import reduce
import time

class InitDatetime(TransformerMixin, BaseEstimator):
    def __init__(self, *, date=None):
        self.date = date
    def fit(self, X):
        return self
    def transform(self, df):
        if self.date in df.columns:
            df[self.date] = pd.to_datetime(df[self.date])
            df.set_index(self.date, inplace=True)
        return df
    
class ResampleWeekly(BaseEstimator, TransformerMixin):
    def __init__(self, target=None, date=None, resample="W-SUN", looper_cols=[]):
        self.target = target
        self.date = date
        self.resample = resample
        self.looper_cols = looper_cols

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        df = X.reset_index()

        df['id'] = df[self.looper_cols].astype(str).agg(';'.join, axis=1)
        grouped = df.groupby('id').resample(self.resample, on=self.date)[self.target].sum().reset_index()

        for col in self.looper_cols:
            grouped[col] = grouped['id'].str.split(';').str[self.looper_cols.index(col)]

        grouped.set_index('id', inplace=True)

        return grouped

class CustomFeatureUnion(BaseEstimator, TransformerMixin):
    """
    Run several transformers and merge using custom index
    """
    def __init__(self, transformer_list, n_jobs=cpu_count(), merge_index=[]):
        self.transformer_list = transformer_list
        self.n_jobs = min(n_jobs, len(transformer_list))
        self.merge_index = merge_index

    def one_fit(self, transformer, X, y):
        return transformer.fit(X, y)

    def one_transform(self, transformer, X):
        return transformer.transform(X)

    def fit(self, X, y=None):
        Parallel(n_jobs=self.n_jobs)(
            delayed(self.one_fit)(trans, X, y)
            for _, trans in self.transformer_list)
        return self

    def transform(self, X):
        start = time.time()
        Xts = Parallel(n_jobs=self.n_jobs)(
            delayed(self.one_transform)(trans, X)
            for _, trans in self.transformer_list)
        print(f"elapsed: {time.time() - start}")

        Xunion = Xts[0]
        for df in Xts[1:]:
            Xunion = pd.merge(Xunion, df, on=self.merge_index)

        Xunion.reset_index(inplace=True)
        return Xunion

