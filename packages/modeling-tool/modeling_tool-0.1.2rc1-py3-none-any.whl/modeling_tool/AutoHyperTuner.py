# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 11:00:20 2024

@author: Heng2020
"""
import inspect
from dataclasses import dataclass, field
from typing import Any, Literal
import numpy as np
import lightgbm as lgb
import pandas as pd
import time

import sys


import modeling_tool.lib01_xgb as xgt
import dataframe_short as ds
import modeling_tool.utils_ml as ml

@dataclass
class AutoHyperTuner():
    train_data: pd.DataFrame
    model: Any = "lightgbm"
    nfold: int = 5
    task: Literal["auto","regression","multi-classification","binary-classification"] = "auto"

    stratified: bool = True
    # task

    def __post_init__(self):
        self.lgb_overfit_param = ['max_depth','num_leaves', 'max_bin', 'feature_fraction', 'boosting_type']
        self.lgb_param_start = \
        {
            # 'objective': 'multiclass',
            # 'metric': 'multi_logloss',
            # auto numclass
            # 'num_class': 2,
            'max_depth':np.arange(2,20,1),
            'num_leaves': 31,
            'max_bin': 260,
            
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            
            
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'bagging_freq': 5,
            'verbosity': -1,
            # 'n_estimators': 100,
            # 'num_boost_round' : 1000,
            
            "min_data_in_leaf":100
        }
        self.auto_tune()
    
    def auto_tune(self):

        if self.model == "lightgbm":
            lgb_param_start = self.lgb_param_start  

            param_df = ml.param_combination(lgb_param_start)
            print(f"Total test: {param_df.shape[0]} ")
            param_test_name = xgt.tune_param_name(lgb_param_start)
            print(param_test_name)

            out_df = param_df.copy()

            for i in out_df.index:
                # each_row should be df
                each_param_combi = param_df.loc[[i]].to_dict('records')[0]
                # below is the bottle neck
                cv_results = lgb.cv(each_param_combi, self.train_data,nfold=self.nfold, stratified=self.stratified)
                metrics = (cv_results["test-rmse-mean"]).tail(1).iloc[0]
                out_df.loc[i,'accuracy'] = metrics
            t02 = time.time()


            print('From auto_tune')


    def get_best_param(self):
        pass
    def get_all_param_metrics(self):
        pass


# prevent showing many objects from import when importing this module
# from typing import *
# will that exclude my class?
__all__ = [name for name, obj in globals().items() 
           if inspect.isfunction(obj) and not name.startswith('_')]
    