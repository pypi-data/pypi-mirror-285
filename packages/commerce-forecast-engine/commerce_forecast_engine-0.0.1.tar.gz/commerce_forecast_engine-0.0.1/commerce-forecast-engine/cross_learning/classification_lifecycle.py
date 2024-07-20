"""
    Lifecycle Product Clustering
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime

def generate_classification_lifecycle(
    df: pd.DataFrame, date_col: str, today,
    n_clusters
):
    today = pd.to_datetime(today)
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    sku_details = df.groupby('id')[date_col].min().reset_index()
    sku_details.rename(columns={date_col: f'min_{date_col}'}, inplace=True)

    sku_details['days_since_today'] = (today - sku_details['min_sales_date']).dt.days

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    sku_details['lifecycle_classification'] = kmeans.fit_predict(sku_details[['days_since_today']])
    sku_details.drop(columns=['days_since_today'], axis=1, inplace=True)
    return sku_details
    