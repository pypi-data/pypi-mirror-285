import pandas as pd
from .classification_abcxyz import generate_classification_abcxyz
from .classification_lifecycle import generate_classification_lifecycle
from source.logger import create_logger
from source.forecast_engine.custom_estimator.cs_utils import CrossProductLearning
from source.forecast_engine.custom_estimator.cs_ml_models import AverageEarlySales
from source.forecast_engine.feature import FeatureConfigV4

logger = create_logger(__name__)

def create_product_classifications(
        df_train: pd.DataFrame, cs_configs, target_skus, feat_config: FeatureConfigV4
    ):
    df_train['id'] = df_train[feat_config.looper_cols[0]] + ';' + df_train[feat_config.looper_cols[1]]
    result_table = pd.DataFrame([id for id in df_train['id'].unique()], columns=['id'])

    for cs_config in cs_configs:
        if isinstance(cs_config.model, CrossProductLearning):
            temp_table = generate_classification_abcxyz(
                df=df_train, skus=target_skus, target_col=feat_config.target,date_col=feat_config.date, sku_col='id', price_col=feat_config.price_col)
            result_table = result_table.merge(temp_table, how='left', on='id')
            logger.info("Created ABC-XYZ Classifications")
        elif isinstance(cs_config.model, AverageEarlySales):
            temp_table =generate_classification_lifecycle(
                df=df_train,date_col=feat_config.date, today=df_train[feat_config.date].max(),
                n_clusters=3
            )
            result_table = result_table.merge(temp_table, how='left', on='id')
            logger.info("Created Lifecycle Classifications")

    result_table.set_index('id', inplace=True)

    return result_table

    