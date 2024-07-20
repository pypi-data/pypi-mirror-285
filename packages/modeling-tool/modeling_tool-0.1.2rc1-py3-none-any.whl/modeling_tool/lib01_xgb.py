# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 10:52:52 2023

@author: Heng2020
"""

# v02 => Import old functions


import xgboost as xgb
import time
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.model_selection import cross_val_score
from playsound import playsound
import seaborn as sns

import sys
import modeling_tool.utils_ml as ml


def output_time(t_in_sec,replay ="Time spend:"):
    
    if t_in_sec >= 60:
        print(f"{replay} {t_in_sec/60:.2f} minutes")
    else:
        print(f"{replay} {int(t_in_sec)} seconds")


def tune_param_name(param_dict):
    for key in param_dict.keys():
        if isinstance(param_dict[key], np.ndarray):
            return(key)

   
def xgb_predict(xgb_pipeline,X):
    y_model = xgb_pipeline.predict(X.to_dict("records"))
    return y_model

def xgb_tune(X_train, y_train, X_dev, y_dev, X_test, y_test, params):
    # global X_dev,X_test,y_dev,y_test
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_squared_error
    import numpy as np

    steps = [("ohe_onestep", DictVectorizer(sparse=False)),
              ("xgb_model", xgb.XGBRegressor(**params))]
    xgb_pipe = Pipeline(steps)
    xgb_pipe.fit(X_train.to_dict("records"),y_train)
    
    y_train_pred = xgb_predict(xgb_pipe, X_train)
    y_dev_pred = xgb_predict(xgb_pipe, X_dev)
    y_test_pred = xgb_predict(xgb_pipe, X_test)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))
    rmse_dev = np.sqrt(mean_squared_error(y_dev, y_dev_pred))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
    
    rmse_train_format = '{:,.3f}'.format(rmse_train)
    rmse_dev_format = '{:,.0f}'.format(rmse_dev)
    rmse_test_format = '{:,.0f}'.format(rmse_test)
    
    print("train: " + rmse_train_format)
    print("dev: " + rmse_dev_format)
    print("test: " + rmse_test_format)
    
    return xgb_pipe


def xgb_tune02(X_train, y_train, params,cv=10):
    # global X_dev,X_test,y_dev,y_test
    steps = [("ohe_onestep", DictVectorizer(sparse=False)),
              ("xgb_model", xgb.XGBRegressor(**params))]
    xgb_pipe = Pipeline(steps)
    # cross_val_scores has no random state 
    # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_score.html
    cross_val_scores = cross_val_score(
                            xgb_pipe,
                            X_train.to_dict("records"),
                            y_train,
                            scoring = "neg_mean_squared_error",
                            cv=cv,
                            )
    xgb_pipe.fit(X_train.to_dict("records"),y_train)
    cross_val_RMSE = np.sqrt(np.abs(cross_val_scores))

    RMSE_cross = np.mean(np.sqrt(np.abs(cross_val_scores)))
    RMSE_int = cross_val_RMSE.astype(int)
    #print(RMSE_int)
    
    for num in RMSE_int:
        print('{:,}'.format(num), end='  ')
    print()
    print("RMSE_cross: " + str(RMSE_cross))
    
    return xgb_pipe

def _xgb_RMSE_H1(X_train, y_train,single_param,cv=10):
    # _xgb_RMSE_H1 helps convert cat columns
    # not tested
    steps = [("ohe_onestep", DictVectorizer(sparse=False)),
              ("xgb_model", xgb.XGBRegressor(**single_param))]
    xgb_pipe = Pipeline(steps)
    # cross_val_scores has no random state 
    # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_score.html
    # bottle neck is below
    cross_val_scores = cross_val_score(
                            xgb_pipe,
                            X_train.to_dict("records"),
                            y_train,
                            scoring = "neg_mean_squared_error",
                            cv=cv,
                            )
    # bottle neck is below
    xgb_pipe.fit(X_train.to_dict("records"),y_train)
    RMSE_cross = np.mean(np.sqrt(np.abs(cross_val_scores)))

    return RMSE_cross

def xgb_RMSE(X_train, y_train,param_df,cv=10,print_time=True):
    # not tested
    # single param as dictionary
    t01 = time.time()
    if isinstance(param_df, dict):
        rmse = _xgb_RMSE_H1(X_train, y_train,param_df,cv)
        out_df = param_df.copy()
        out_df.loc[0,'RMSE'] = rmse
    # param_df from f.param_combination
    else:
        
        out_df = param_df.copy()

        for i in out_df.index:
            # each_row should be df
            each_row = param_df.loc[[i]].to_dict('records')[0]
            # below is the bottle neck
            rmse = _xgb_RMSE_H1(X_train, y_train,each_row,cv)
            out_df.loc[i,'RMSE'] = rmse
    t02 = time.time()
    t01_02 = t02-t01
    if print_time:
        output_time(t01_02)
    return out_df

def time_xgb_rmse(X_train,y_train,all_param,n_param,increment=1,cv=10):
    # not tested 
    
    # cv = cross-validation
    # can generalize this to any function
    # in seconds
    #time_list = []
    # to improve: if the time t01_02 is more than 1 min then 
    # just return back 
    import pandas as pd
    time_data = pd.DataFrame(columns=['n','time'])
    for n in range(1,n_param+1,increment):
        param_test = all_param.iloc[:n] 
        t01 = time.time()
        rmse_df = xgb_RMSE(X_train,y_train,param_test,cv)
        t02 = time.time()
        t01_02 = int(t02 - t01)
        # time_list.append(t01_02)
        new_row = pd.DataFrame({'n': [n], 'time': [t01_02]})
        time_data = pd.concat([time_data,new_row])
    return time_data

def xbg_GridSearch(X_train,y_train,param_grid,random_state=1,print_time=True,cv=10):
    # tested
    
    # example of how param_grid should look like
    
    # param_grid = {
    #     # np.arange(0, 10, 1)
    #     # from 0 to 9 step 1
    #     'learning_rate': np.arange(0.16, 0.26, 0.02), 
    #     'n_estimators': np.arange(15,23,1), 
    #     'max_depth': np.arange(2, 5, 1),
    #     'subsample': np.arange(0.6, 1, 0.2)
    #     }
    

    param_df = ml.param_combination(param_grid)
    print(f"Total combination: {param_df.shape[0]} ")
    
    t01 = time.time()
    rmse_df = xgb_RMSE(X_train,y_train,param_df,cv)
    
    ans = dict()
    ans['best_RMSE'] = min(rmse_df['RMSE'])
    best_row = rmse_df[rmse_df['RMSE']==ans['best_RMSE']]
    best_row = best_row.drop('RMSE',axis=1)

    ans['best_param'] = best_row.to_dict("records")[0]
    ans['RMSE_df'] = rmse_df
    
    t02 = time.time()
    t01_02 = t02-t01
    if print_time:
        if t01_02 >= 60:
            print(f"Time spend: {t01_02/60:.2f} minutes")
        else:
            print(f"Time spend: {int(t01_02)} seconds")
    
    return ans

def xgb_ParamSearch(X_train,y_train,param_grid,n_limit=300,random_state=1,print_time=True,cv=10):
    # tested
    
    # example of how param_grid should look like
    
    # param_grid = {
    #     # np.arange(0, 10, 1)
    #     # from 0 to 9 step 1
    #     'learning_rate': np.arange(0.16, 0.26, 0.02), 
    #     'n_estimators': np.arange(15,23,1), 
    #     'max_depth': np.arange(2, 5, 1),
    #     'subsample': np.arange(0.6, 1, 0.2)
    #     }
    
    
    # if param_grid has more combinations than n_limit
    # it will start to use RandomSearch
    param_df = ml.param_combination(param_grid)
    print(f"Total combination: {param_df.shape[0]} ")
    
    if param_df.shape[0] > n_limit:
        param_limit = param_df.sample(n=n_limit,random_state=random_state)
        print(f"Process limit to {n_limit} combinations.")
    else:
        param_limit = param_df
    
    t01 = time.time()
    rmse_df = xgb_RMSE(X_train,y_train,param_limit,cv)
    
    
    ans = dict()
    ans['best_RMSE'] = min(rmse_df['RMSE'])
    best_row = rmse_df[rmse_df['RMSE']==ans['best_RMSE']]
    best_row = best_row.drop('RMSE',axis=1)

    ans['best_param'] = best_row.to_dict("records")[0]
    ans['RMSE_df'] = rmse_df
    
    t02 = time.time()
    t01_02 = t02-t01
    if print_time:
        if t01_02 >= 60:
            print(f"Time spend: {t01_02/60:.2f} minutes")
        else:
            print(f"Time spend: {int(t01_02)} seconds")
    
    return ans


def xgb_DTrain_Tune(
        X_train,
        y_train,
        param_dict,
        print_time=True,
        draw_graph=True,
        alarm=True,
        cv=10,
        seed=1,
        num_boost_round=1000,
        early_stopping_rounds=10):
    import xgboost as xgb
    import time
    t01 = time.time()
    data_DMatrix = xgb.DMatrix(data=X_train,label=y_train)      

    param_df = ml.param_combination(param_dict)
    print(f"Total test: {param_df.shape[0]} ")
    param_test_name = tune_param_name(param_dict)
    print(param_test_name)

    out_df = param_df.copy()

    for i in out_df.index:
        # each_row should be df
        each_row = param_df.loc[[i]].to_dict('records')[0]
        # below is the bottle neck
        cv_results = xgb.cv(dtrain=data_DMatrix,
                            params=each_row,
                            nfold=cv,
                            num_boost_round=num_boost_round,
                            early_stopping_rounds=early_stopping_rounds,
                            metrics="rmse",
                            seed=seed,
                            as_pandas=True
                            )
        rmse = (cv_results["test-rmse-mean"]).tail(1).iloc[0]
        out_df.loc[i,'RMSE'] = rmse
    t02 = time.time()
    t01_02 = t02-t01
    if print_time:
        output_time(t01_02)
    if alarm:
        playsound(sound_path)
    if draw_graph:
        sns.lineplot(x=param_test_name, y='RMSE',data=out_df)
    return out_df


def xgb_predict(xgb_pipeline,X):
    y_model = xgb_pipeline.predict(X.to_dict("records"))
    return y_model

def xgb_predict_append(xgb_pipeline,X):
    y_model = xgb_predict(xgb_pipeline,X)
    X["y_model"] = y_model
    return X