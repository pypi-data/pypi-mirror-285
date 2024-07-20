import pandas as pd
import numpy as np
from pydantic import BaseModel
from multiprocessing import cpu_count
from dataclasses import MISSING
from typing import Dict, List, Optional

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from .utils import (
    CustomFeatureUnion,
    ResampleWeekly, 
    InitDatetime
)
from .feature_engineering import (
    FEPriceMapping,
    FEPackageCount,
    FEHolidayCount,
    FELagging,
    FEMovingAverage
)

import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_THREADS=int(os.getenv("MAX_THREADS",2))

class FeatureConfigV4(BaseModel):
    """
    Feature Config Class:
    1. Use to generate Features from clean queries
    2. Use to generate Features from promotions
    """

    date: Optional[str] = None
    target: Optional[str] = None
    looper_cols: Optional[List[str]] = None
    package_col: str = ""
    price_col: str = ""
    pipeline: Pipeline = None

    # Feature Engineering
    fe_pricemapper: bool = False
    fe_pricemapper_dict: dict = {}
    fe_packagecount: bool = False
    fe_holiday: bool = False
    fe_holiday_country: str = 'ID'
    fe_lagging: bool = False
    fe_lagging_n: int = 0
    fe_ma: bool = False
    fe_ma_window: int = 0
    fe_normalize: bool = False
    y_scaler: StandardScaler = StandardScaler()
    X_scaler: StandardScaler = StandardScaler()

    # Parameters
    min_train_weeks: int = -1
    _is_initialized: bool = False
    
    class Config:
        arbitrary_types_allowed = True

    def create_pipeline(self) -> Pipeline:
        if self._is_initialized: return self.pipeline

        steps = []

        # Transactions Features Extraction
        # input: transactions data
        # output: weekly resampled dataframe
        paralel_steps = [
            ('Resample Weekly Target', 
             ResampleWeekly(
                target=self.target, date=self.date, looper_cols=self.looper_cols
            ))
        ]

        if self.fe_pricemapper:
            paralel_steps.append(
                ('FE Price Mapping', FEPriceMapping(
                        price_range=self.fe_pricemapper_dict, 
                        target=self.target, date=self.date, 
                        looper_cols=self.looper_cols, 
                        menu_col=self.package_col, 
                        price_col=self.price_col
                    )
                )
            )

        if self.fe_packagecount:
            paralel_steps.append(
                ('FE Package Count', FEPackageCount(
                        package_col=self.package_col, 
                        looper_cols=self.looper_cols,
                        date=self.date,
                        target=self.target
                    )
                )
            )

        transactions_fe_pipe = CustomFeatureUnion(
            transformer_list=paralel_steps,
            n_jobs=min(len(paralel_steps), MAX_THREADS),
            merge_index=['id', self.date]
        )
        
        steps.append(('Transactions FE', transactions_fe_pipe))

        # Weekly Features Extraction
        # input: weekly features dataframe
        # output: weekly features dataframe
        weekly_steps = []

        if self.fe_holiday:
            weekly_steps.append(
                ('FE Holidays Encoding', FEHolidayCount(
                    date_col=self.date,
                    country=self.fe_holiday_country
                ))
            )
        
        if len(weekly_steps) > 0 :
            steps.extend(weekly_steps)

        # Dynamic Features Extraction
        # input: weekly features dataframe
        # output: weekly features dataframe (drop nan values caused by lagging)
        dynamic_steps = []
        
        if self.fe_lagging:
            dynamic_steps.append(
                ('FE Lagging Features', FELagging(
                    n_lags=self.fe_lagging_n, target=self.target, 
                    n_jobs=min(cpu_count(), MAX_THREADS), date=self.date
                ))
            )

        if self.fe_ma:
            dynamic_steps.append(
                ('FE Moving Average', FEMovingAverage(
                    window=self.fe_ma_window,
                    target=self.target, date=self.date, 
                    n_jobs=min(cpu_count(), MAX_THREADS)
                ))
            )
             
        if len(dynamic_steps) > 0:
            steps.extend(dynamic_steps)
            self._dynamic_steps = dynamic_steps

        self.pipeline = Pipeline(steps=steps)
        self._is_initialized = True

        self._min_train_weeks()

        return self.pipeline
    
    def _min_train_weeks(self) -> int:
        self.min_train_weeks = max(self.fe_lagging_n, self.fe_ma_window)
        return self.min_train_weeks

    def get_X_y(self, df): 
        if not self._is_initialized:
            self.create_pipeline()

        # Normal forecasting
        X = self.pipeline.transform(df).drop(self.looper_cols, axis=1)
        X.set_index('id', inplace=True)
        y = X[[self.date,self.target]].copy()
        _ = X.pop(self.target)

        return X, y
    
    def update_dynamic_features(self, X: pd.DataFrame, y:pd.Series) -> pd.DataFrame:
        dyna_pipeline = Pipeline(steps=self._dynamic_steps)

        X = X.reset_index(drop=False)
        X.set_index(self.date, drop=True, inplace=True)
        X.loc[y.index, f"{self.target}_t"] = y.values

        X_updated = dyna_pipeline.transform(X)

        return X_updated

