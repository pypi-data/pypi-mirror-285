from dataclasses import MISSING, dataclass, field
from typing import Dict, List, Union
from types import NoneType
import numpy as np
import pandas as pd
import logging
import copy
from sklearn.utils import shuffle
from ..feature import FeatureConfigV4
from ..models.ml_forecast import MLForecast, ModelConfig
from ...metric_calculation import calculate_metric

from tqdm import tqdm
import uuid
from queue import Queue
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_THREADS=int(os.getenv("MAX_THREADS", 2))
CS_CLASS_NAME = 'GLOBAL_COLD_START'

logger = logging.getLogger(__name__)

@dataclass
class Autoforecast(

):
    """
        Forecasting Engine
    """

    base_feat_config: FeatureConfigV4 = field(
        default=MISSING,
        metadata={"help": "feature configurations"}
    )
    base_model_configs: List = field(
        default=MISSING,
        metadata={"help": "list of Models experiment configuration"}
    )
    base_cs_config: List = field(
        default=MISSING,
        metadata={"help":"List of CS experiments"}
    )
    target_skus: List = field(
        default=MISSING,
        metadata={"help": "Forecasted skus"}
    )
    
    cs_classification: Dict = field(
        default=None,
        metadata={"help": "list of Product Clustering"}
    )

    # Parameter 
    _config_maps = {}
    _cl_config_maps = {}
    _evals_result = {}
    _inference_model = {}
    _no_train_data_id = []

    # Optional CS data
    _early_sales = None

    # Status
    _metric: str = "MAE"
    _is_trained: bool = False
    _is_evaluated: bool = False
    _is_optimized: bool = False

    # CS: Cold Start Detection Utils
    def _cs_detection(self, y_train, id):
        """
        Modify to add more cs condition
        """
        y_train_id = self._get_target_for_id(y_train, id)

        if self.base_feat_config.min_train_weeks <= -1:
            raise ValueError("Feat Config must be initialized: use create_pipeline")

        return y_train_id[
            y_train_id.values>0
        ].shape[0] < self.base_feat_config.min_train_weeks



    # Feat: for data slicing
    def _get_features_for_id(self,X: pd.DataFrame, id: str):
        return X[X.index == id].set_index(self.base_feat_config.date,drop=True)

    def _get_target_for_id(self, y: pd.DataFrame, id):
        return y[y.index == id].set_index(self.base_feat_config.date,drop=True).pop(self.base_feat_config.target)
    
    # Feat: Getting Deployment Variables
    def get_feat_config(self, id) -> FeatureConfigV4:
        try:
            return self._config_maps[id]['feat_config']
        except:
            raise ValueError(f"feat_config for {id} not exist")
        
    def get_ml_model(self, id) -> Union[MLForecast, ModelConfig]:
        try:
            return self._inference_model[id]
        except Exception as err:
            raise ValueError(f"(ml_model, model_config) for {id} not exist. msg={err}")
    

    # Metadata: Evals Table Utils
    def generate_evals_table(self):
        results = []
        for item in self._evals_result.items():
            results.extend(item[1])
        return pd.DataFrame(results)
    


    # Fit: Modeling Utils  
    def _fit_normal_model(
        self,
        X_train, 
        y_train,
        id=None, 
        feat_config_used: FeatureConfigV4 = None,
    ):
        """
        Fitting functions for Regular Model

        Note:
        - if id get passed means X_train will be filtered by using id
        """
        
        model_config_iters = copy.deepcopy(self.base_model_configs)

        if isinstance(feat_config_used, NoneType):
            feat_config_used = copy.deepcopy(self.base_feat_config)

        # Feature selection based on model
        if id:
            try:
                X_in = self._get_features_for_id(X_train, id)
                y_in = self._get_target_for_id(y_train, id)
            except Exception as _:
                X_in = X_train
                y_in = y_train
        else:
            try:
                X_in = X_train.set_index(feat_config_used.date, drop=True)
                y_in = y_train.set_index(feat_config_used.date,drop=True).pop(feat_config_used.target)
            except Exception as _:
                X_in = X_train
                y_in = y_train

        # Fitting
        ml_models = []
        for index, model_config in enumerate(model_config_iters):
            model_config = model_config_iters[index]

            ml_model = MLForecast(model_config)
            ml_model.fit(X_in, y_in)

            ml_models.append((ml_model, model_config))

        return {
            'feat_config': feat_config_used,
            'models': ml_models,
            'method': 'regular',
            'scaled': False
        }

    # Fit: Modeling Utils
    def _fit_cl_model(
        self,
        X_train, 
        y_train,
    ):
        """
        Fitting functions for Cross Learning Model
        """
        def __get_cl_train_data(X_train, y_train, ref_ids):
            X_train_all_list = []
            y_train_all_list = []

            # Aggregate data
            for id in ref_ids:  
                try:
                    X_train_id = self._get_features_for_id(X_train, id)
                    y_train_id = self._get_target_for_id(y_train, id)
                except Exception as err:
                    logger.info(f"Missing ref id={id}, msg={err}")
                    continue

                if X_train_id.empty: 
                    self._no_train_data_id.append(id) 
                    continue

                try:
                   feat_config = self.get_feat_config(id)
                except Exception as err:
                    logger.info(f"Missing feat_config id={id}, msg={err}")
                    continue


                y_train_id_scaled = feat_config.y_scaler.fit_transform(y_train_id.values.reshape(-1, 1)).flatten()
                y_train_id_scaled = pd.Series(y_train_id_scaled, index=y_train_id.index, name=y_train_id.name)
                X_train_id_scaled = feat_config.X_scaler.fit_transform(X_train_id.values)
                X_train_id_scaled = pd.DataFrame(X_train_id_scaled, index=X_train_id.index, columns=X_train_id.columns)

                X_train_all_list.append(X_train_id_scaled)
                y_train_all_list.append(y_train_id_scaled)
            
            X_train_all = pd.concat(X_train_all_list, ignore_index=True)
            y_train_all = pd.concat(y_train_all_list, ignore_index=True)

            # Shuffle data
            X_train_all, y_train_all = shuffle(X_train_all, y_train_all, random_state=42)

            return X_train_all, y_train_all
            

        cl_config_iters = copy.deepcopy(self.base_cs_config)

        for _, model_config in enumerate(cl_config_iters):
            if model_config.model.config_type == 'CROSS_PRODUCT_LEARNING':
                if isinstance(self.cs_classification,NoneType):
                    raise ValueError("for CROSS_PRODUCT_LEARNING, cs_cluster must be provided")
                for cl_class in self.cs_classification[model_config.model.cluster_strategy].dropna().unique():
                    ref_ids = self.cs_classification[
                        self.cs_classification[model_config.model.cluster_strategy] == cl_class
                    ].index.unique()
                    try:
                        X_train_in, y_train_in = __get_cl_train_data(X_train, y_train, ref_ids)
                    except Exception as err:
                        logger.warning(f"Failed to build {cl_class} model: not enough data, msg={err}")

                    self._cl_config_maps[cl_class] = self._fit_normal_model(
                        X_train_in, y_train_in
                    )  
                break
            
        return {
            'method_name':model_config.model.cluster_strategy
        }
    
    # Fit: Modeling Utils
    def _fit_cs_model(
        self,
        X_train, 
        y_train,
    ):
        """
        Fitting functions for Cold Start Global Model
        Part of Cross Learning Model*
        """
        def __get_cs_train_data(X_train, y_train, id_details: pd.DataFrame=None, n_early_sales: int=10):
            date_col = self.base_feat_config.date
            def __get_early_sales(df_weekly, id_details, n_early_sales, is_target=False):
                df_feat = (
                    df_weekly.sort_values(by=['id', date_col])
                        .groupby('id')
                        .head(n_early_sales)
                )

                return df_feat

            X_train_in = __get_early_sales(X_train, id_details, n_early_sales)
            y_train_in = __get_early_sales(y_train, id_details=id_details, n_early_sales=n_early_sales, is_target=True)

            return X_train_in, y_train_in


        cl_config_iters = copy.deepcopy(self.base_cs_config)

        for _, model_config in enumerate(cl_config_iters):
            if model_config.model.config_type == 'AVERAGE_EARLY_SALES':

                X_train_in, y_train_in = __get_cs_train_data(X_train, y_train, self.cs_classification)

                self._cl_config_maps[CS_CLASS_NAME] = self._fit_normal_model(
                    X_train_in, y_train_in
                )  
                break
            
        return {
            'method_name':model_config.model.cluster_strategy
        }


    # Main: Fitting / Training
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame
    ):
        """
        Train Model
        """
        def __single_id_cs_detection(id, log_queue):
            y_train_id = self._get_target_for_id(y, id)
            y_train_id = y_train_id[y_train_id.values>0]
            log = {
                'id': id,
                'is_coldstart': False,
                'train_rows': y_train_id.shape[0],
                'train_min_date': y_train_id.index.min(),
                'train_max_date': y_train_id.index.max(),
                'train_y_sum': y_train_id.sum(),
                'train_y_mean': y_train_id.mean()
            }
            log['is_coldstart'] = self._cs_detection(y, id)
            self._config_maps[id] = {'feat_config':copy.deepcopy(self.base_feat_config)}
            log_queue.put(log)

        def __single_id_cs_cl_model(id, cl_details, cs_details):
            cl_method = cl_details['method_name']
            cs_method = cs_details['method_name']

            # For CS Method
            self._config_maps[id]['models'] = copy.deepcopy(self._cl_config_maps[CS_CLASS_NAME]['models'])
            self._config_maps[id]['method'] = 'crosslearning' + '-' + cs_method 
            self._config_maps[id]['scaled'] = False

            # For CL Method
            if id in self.cs_classification.index.unique():
                id_class = self.cs_classification.loc[id][cl_method]
                if id_class:
                    self._config_maps[id]['models'] = copy.deepcopy(self._cl_config_maps[id_class]['models'])
                    self._config_maps[id]['method'] = 'crosslearning' + '-' + cl_method 
                    self._config_maps[id]['scaled'] = True
            

        logs = []
        tasks = self.target_skus

        log_queue = Queue()

        # Detect Appropiate Learning Method
        with tqdm(total=len(tasks), desc='Finding appropiate forecast method') as pbar:
            with ThreadPoolExecutor(max_workers=min(len(tasks), MAX_THREADS)) as executor:
                futures = [executor.submit(__single_id_cs_detection, id, log_queue) for id in tasks]
                
                for future in futures:
                    future.result() 
                    pbar.update(1)

            while not log_queue.empty():
                logs.append(log_queue.get())

        # Fitting CL-CS Model
        logger.info("Fitting Cross Learning Cold Start Model")
        cs_details = self._fit_cs_model(X, y)

        # Fitting CL-Hybrid Model
        logger.info("Fitting Cross Learning Cluster Model")
        cl_details = self._fit_cl_model(X, y)
        
        # Assign CL Model
        logger.info("Matching CL Model")
        cl_ids = [ log['id'] for log in logs if log['is_coldstart'] ]
        if cl_ids:
            with tqdm(total=len(cl_ids), desc="[Hybrid] Fitting all Configs") as pbar:
                with ThreadPoolExecutor(max_workers=min(len(cl_ids),MAX_THREADS)) as executor:
                    futures = [executor.submit(__single_id_cs_cl_model, id, cl_details, cs_details) for id in cl_ids]
                    for future in futures:
                        future.result()
                        pbar.update(1)

        # Fitting Normal Model
        n_ids = [ log['id'] for log in logs if not log['is_coldstart'] ]
        if n_ids:
            with tqdm(total=len(n_ids), desc="[Normal] Fitting all Configs") as pbar:
                with ThreadPoolExecutor(max_workers=min(len(n_ids),MAX_THREADS)) as executor:
                    futures = [executor.submit(self._fit_normal_model, X, y, id) for id in n_ids]
                    for future in as_completed(futures):
                        id = n_ids[futures.index(future)]
                        self._config_maps[id] = future.result()
                        pbar.update()

        self._is_trained = True

        return pd.DataFrame(logs)

    # Main: Perform Bestfit
    def run_experiments(
        self,
        metric: str,
        X_test: pd.DataFrame,
        y_test: pd.DataFrame,
    ):
        """
        Evaluate Model Performance
        """
        def __single_id_evaluation(id, X_test, y_test):
            try:
                models = self._config_maps[id]['models']
                feat_config = self._config_maps[id]['feat_config']
                is_scaled = self._config_maps[id]['scaled']
                method = self._config_maps[id]['method']
            except Exception as err:
                logger.warning(f"Error on id: {id} >> msg={err}")
                return []

            result = []

            X_in = self._get_features_for_id(X_test, id)
            y_in = self._get_target_for_id(y_test, id)

            if X_in.empty or id in self._no_train_data_id:
                return [
                    {
                        'id': id,
                        'model': CS_CLASS_NAME,
                        'method': method,
                        'is_scaled': is_scaled
                    }
                ]  

            for model in models:
                ml_model = model[0]
                model_config = model[1]
                
                if is_scaled:
                    feat_config = self.get_feat_config(id)
                    X_in = pd.DataFrame(feat_config.X_scaler.transform(X_in.values),index=X_in.index,columns=X_in.columns)
                    preds_scaled = ml_model.predict(X_in, feat_config)
                    preds = feat_config.y_scaler.inverse_transform(preds_scaled.values.reshape(-1, 1))
                    preds = pd.Series(preds.flatten(), index=preds_scaled.index)
                else:
                    preds = ml_model.predict(X_in, feat_config)

                log = calculate_metric(
                    y_test=y_in,
                    y_pred=preds[:len(y_in)]
                )
                log['id'] = id
                log['model'] = model_config.name
                log['method'] = method
                log['is_scaled'] = is_scaled
                result.append(log)
            return result

        def __single_id_bestfit(id):
            experiments = self._evals_result[id]
            models = self._config_maps[id]['models']

            if not experiments:
                return None 

            # Find the experiment with the lowest metric value
            best_log = min(experiments, key=lambda log: log[self._metric])
            lowest_value = best_log[self._metric]

            # Update best_fit for each log
            for log in experiments:
                log['best_fit'] = (log[self._metric] == lowest_value)

            # Update the inference model for the given id
            self._inference_model[id] = next(
                (model_tuple for model_tuple in models if model_tuple[1].name == best_log['model']), None
            )

        self._metric = metric

        # Evaluate all experiments 
        if not self._is_evaluated:
            self._evals_result = {}
            tasks = list(self._config_maps.keys())
            with tqdm(total=len(tasks), desc="Evaluating Models") as pbar:
                with ThreadPoolExecutor(max_workers=min(len(tasks),MAX_THREADS)) as executor:
                    futures = [executor.submit(__single_id_evaluation, id, X_test, y_test) for id in tasks]
                    for future in as_completed(futures):
                        id = tasks[futures.index(future)]
                        self._evals_result[id] = future.result()
                        pbar.update(1)
            self._is_evaluated = True

        # Get bestfit 
        if not self._is_optimized:
            with tqdm(total=len(tasks), desc="Finding Best Fits") as pbar:
                with ThreadPoolExecutor(max_workers=min(len(tasks),MAX_THREADS)) as executor:
                    futures = [executor.submit(__single_id_bestfit, id) for id in tasks]
                    for _ in as_completed(futures):
                        pbar.update(1)
            self._is_optimized = True

        return self.generate_evals_table()

