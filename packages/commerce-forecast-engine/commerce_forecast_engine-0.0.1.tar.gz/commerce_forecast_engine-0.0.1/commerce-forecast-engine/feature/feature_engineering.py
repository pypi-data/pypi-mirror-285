import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import holidays
from joblib import Parallel
from joblib import delayed


"""
    Transactions Features
"""
class FEPriceMapping(BaseEstimator, TransformerMixin):
    def __init__(
        self, price_range: dict, target="qty", date="sales_date", looper_cols = [],
        menu_col='package_head', price_col='package_price'
    ):
        self.price_range = price_range
        self.target = target
        self.date = date
        self.looper_cols = looper_cols
        self.menu_col = menu_col
        self.price_col = price_col

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        def count_packages_in_price_ranges(group):
            counts = {}
            for category, bounds in self.price_range.items():
                min_price = bounds['min']
                max_price = bounds['max']
                mask = (group[self.price_col] > min_price) & (group[self.price_col] <= max_price)
                count = group.loc[mask, self.menu_col].nunique()
                counts[f'{category}_count'] = count
            return pd.Series(counts)
        
        df = X.reset_index(drop=True)

        df['id'] = df[self.looper_cols].astype(str).agg(';'.join, axis=1)
        grouped = df.groupby('id').resample('W-SUN', on=self.date).apply(count_packages_in_price_ranges).reset_index()

        grouped.set_index('id', inplace=True)

        return grouped

class FEPackageCount(BaseEstimator, TransformerMixin):
    def __init__(self, package_col, looper_cols, date, target, resample='W-SUN'):
        self.date = date
        self.target = target
        self.package_col = package_col
        self.looper_cols = looper_cols
        self.resample = resample

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        df = X.reset_index(drop=True)

        aggregation = {
            self.package_col : 'nunique',
        }

        df['id'] = df[self.looper_cols].astype(str).agg(';'.join, axis=1)
        grouped = df.groupby('id').resample(self.resample, on=self.date).agg(aggregation).reset_index()

        grouped.set_index('id', inplace=True)

        return grouped

"""
    Weekly Features
"""
class FEHolidayCount(BaseEstimator, TransformerMixin):
    def __init__(self, date_col="", country='ID'):
        self.date_col = date_col
        self.country = country

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        def check_holidays_in_week(start_date, end_date):
            week_dates = pd.date_range(start=start_date, end=end_date, freq='D')
            return {date: (date in holidays_in_week) for date in week_dates}

        df = X.copy()
        holidays_in_week = holidays.country_holidays(self.country)

        # build calendar
        calendar = pd.DataFrame({
            self.date_col: pd.date_range(start=df[self.date_col].min(), end=df[self.date_col].max(), freq='W-SUN')
        })
        calendar.set_index(self.date_col, inplace=True)
        days_of_week = range(7)
        for day in days_of_week:
            calendar[f'holiday_{day}'] = False
        for idx in calendar.index:
            start_date = idx - pd.Timedelta(days=6)
            end_date = idx
            holidays_in_week = check_holidays_in_week(start_date, end_date)
            for date, is_holiday in holidays_in_week.items():
                calendar.at[idx, f'holiday_{date.weekday()}'] = is_holiday

        # Left Join
        df = df.merge(calendar, how='left', on=self.date_col)

        return df

class FELagging(BaseEstimator, TransformerMixin):
    def __init__(self, n_lags=1, target="", id_column="id", n_jobs=1, date=""):
        self.n_lags = n_lags
        self.target = target
        self.id_column = id_column 
        self.n_jobs = n_jobs
        self.date = date

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame):
        def single_transform(id_value, X):
            if id_value:
                X_temp = X[X[self.id_column] == id_value].copy()
            else:
                X_temp = X.copy()
            X_temp = X_temp.sort_values(by=self.date) 
            
            if f'{self.target}_t' in X_temp:
                # TODO: check this
                X_temp.reset_index(drop=False, inplace=True)
                changes = X_temp[X_temp[f'{self.target}_t'].notna()]
                index = changes.index[0] 
                value = changes[f'{self.target}_t'].iloc[0]
                X_temp.loc[index, f'{self.target}_1'] = value

                # Set lagged quantities
                for lag in range(1, self.n_lags ):
                    if index + lag < len(X_temp):
                        X_temp.loc[index + lag, f'qty_{lag+1}'] = value

                # Set index and drop unnecessary column
                X_temp.set_index(self.date, drop=True, inplace=True)
                X_temp.drop(columns=[f'{self.target}_t'], inplace=True)
            else:
                for lag in range(1, self.n_lags + 1):
                    X_temp[f'{self.target}_{lag}'] = X_temp[self.target].shift(lag)
            return X_temp
        
        if self.id_column not in X: 
            return single_transform(None,X)
        else:
            Xts = Parallel(n_jobs=self.n_jobs)(
                delayed(single_transform)(id_value, X)
                for id_value in X[self.id_column].unique()
            )
            return pd.concat(Xts).fillna(0).reset_index(drop=True)


class FEMovingAverage(BaseEstimator, TransformerMixin):
    def __init__(self, window=1, target="", id_column="id", n_jobs=1, date=""):
        self.window = window
        self.target = target
        self.id_column = id_column 
        self.n_jobs = n_jobs
        self.date = date

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        def single_transform(id_value, X):
            if id_value:
                X_temp = X[X[self.id_column] == id_value].copy()
            else:
                X_temp = X.copy()
            X_temp = X_temp.sort_values(by=self.date) 
            try:
                X_temp[f'{self.target}_ma_{self.window}'] = X_temp[self.target].shift(1).rolling(window=self.window).mean()
            except:
                X_temp[f'{self.target}_ma_{self.window}'] = X_temp.loc[:, [f'{self.target}_{i}' for i in range(1, self.window+1)]].sum(axis=1) / self.window
                
            return X_temp

        if self.id_column not in X:
            return single_transform(None, X)
        else:
            Xts = Parallel(n_jobs=self.n_jobs)(
                delayed(single_transform)(id_value, X)
                for id_value in X[self.id_column].unique()
            )
            return pd.concat(Xts).fillna(0).reset_index(drop=True)
    
"""
    Template
"""
class FETemplate(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X