"""
    ABC-XYZ Product Clustering
"""

import pandas as pd
from typing import List

def generate_classification_abcxyz(
        df: pd.DataFrame, skus, target_col: str, date_col: str,
        price_col: str, sku_col,  freq='M'
    ):
    def split_datetime_info(df):
        df['dt_year'] = df[date_col].dt.year
        if freq == 'M':
            df['dt_subset'] = df[date_col].dt.month
        elif freq == 'W':
            df['dt_subset'] =  df[date_col].dt.isocalendar().week

        return df
    
    def calculate_sku_revenue(df):
        df['revenue'] = df[target_col] * df[price_col]
        df_grouped = df_.groupby(
            [sku_col, 'dt_year', 'dt_subset']
        )['revenue'].sum().to_frame().reset_index()
        df_grouped['dt_category'] = df_grouped['dt_year'].map(str)+'-'+df_grouped['dt_subset'].map("{:03}".format)

        df_pivot_sku = df_grouped.pivot(
            index=sku_col, columns='dt_category', values='revenue'
        ).reset_index().fillna(0)

        df_pivot_sku['total_sales'] = df_pivot_sku.iloc[:,1:].sum(axis=1,numeric_only=True)

        non_zero_counts = (df_pivot_sku.iloc[:, 1:] != 0).sum(axis=1)
        df_pivot_sku['average_sales'] = df_pivot_sku['total_sales'] / non_zero_counts

        df_pivot_sku['std_dev_sales'] = df_pivot_sku.iloc[:, 1:].apply(lambda x: x[x != 0].std(), axis=1)

        return df_grouped, df_pivot_sku
    
    # Filter Input 
    df[date_col] = pd.to_datetime(df[date_col])
    df = df[df[sku_col].isin(skus)].copy()

    # Datetime processing
    df_ = split_datetime_info(df)

    # Count Revenue / skus
    df_grouped, df_pivot_sku = calculate_sku_revenue(df_)

    # Classification
    # XYZ
    df_pivot_sku['CoV'] = df_pivot_sku['std_dev_sales']/df_pivot_sku['average_sales']
    df_pivot_sku['XYZ'] = df_pivot_sku['CoV'].apply(xyz_classifcation)
    df_pivot_sku.set_index(sku_col, inplace=True)
    xyz_mapper = df_pivot_sku['XYZ'].to_dict()

    # ABC
    df_rev = df_pivot_sku.groupby(sku_col).agg(
        total_revenue=('total_sales', 'sum')
    ).sort_values(by='total_revenue', ascending=False).reset_index()
    df_rev['revenue_cum_sum'] = df_rev['total_revenue'].cumsum()
    df_rev['revenue_sum'] = df_rev['total_revenue'].sum()
    df_rev['sku_rev_percent'] = df_rev['revenue_cum_sum']/ df_rev['revenue_sum']
    df_rev['ABC'] = df_rev['sku_rev_percent'].apply(abc_classification)
    df_rev.set_index(sku_col, inplace= True)
    abc_mapper = df_rev['ABC'].to_dict()

    classification = pd.DataFrame([i for i in skus], columns=[sku_col])
    classification['ABC'] = classification[sku_col].map(abc_mapper)
    classification['XYZ'] = classification[sku_col].map(xyz_mapper)
    classification['ABC-XYZ'] = classification['ABC'] + classification['XYZ']

    return classification

# Utils
def xyz_classifcation(cov):
    if cov <= 0.5:
        return "X"
    elif cov>=0.5 and cov<=1:
        return "Y"
    else:
        return "Z"
    
def abc_classification(rp):
    if rp>0 and rp<=0.80:
        return "A"
    elif rp>0.80 and rp<=0.90:
        return "B"
    else:
        return 'C'