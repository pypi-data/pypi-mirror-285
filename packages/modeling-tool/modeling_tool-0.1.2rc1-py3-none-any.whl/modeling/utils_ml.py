# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 15:48:46 2023
Mod01: on Sun Sep 3,


@author: Heng2020
"""
# v02 => import param_combination, train_dev_test_split
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.cluster import MiniBatchKMeans
from sklearn.datasets import make_blobs
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import warnings

def create_result_df(X,y_actual,y_predict):
    df_result = X.copy()
    df_result['y_actual'] = y_actual
    df_result['y_model'] = y_predict
    
    df_result['y_diff'] = abs(df_result['y_model']-df_result['y_actual'])

    df_result['y_diff%1'] = df_result['y_diff']/((df_result['y_model']+df_result['y_actual'])/2)
    df_result['y_diff%2'] = df_result['xgb_RMSE']/df_result['y_actual']
    df_result['y_diff%3'] = df_result['y_diff']/df_result['y_model']
    return df_result

def train_dev_test_split(X,y,seed=0):
    from sklearn.model_selection import train_test_split
    X_train, X_dev_test, y_train, y_dev_test = train_test_split(
                                                    X, 
                                                    y, 
                                                    test_size=0.3,
                                                    random_state=seed
                                                    )
    
    X_dev,X_test,y_dev,y_test = train_test_split(
                                    X_dev_test,
                                    y_dev_test,
                                    test_size=1/3,
                                    random_state=seed
                                        )
    return [X_train,X_dev,X_test,y_train,y_dev,y_test]

def param_combination(param_grid):
    # param_grid should look like this
    
    # param_grid = {
    #     'learning_rate': np.arange(0.05,1.05,0.05), 
    #     'n_estimators': np.arange(10,200,10), 
    #     'max_depth': np.arange(2,8),
    #     "num_boost_round": [100] 
    #     }
    
    # Added feature01: 
    param_grid_in = {}

    # convert 1 int or float to list
    for hyper_param, values in param_grid.items():
        if isinstance(values,(int,float,str)):
            param_grid_in[hyper_param] = [values]
        else:
            param_grid_in[hyper_param] = values


    from sklearn.model_selection import ParameterGrid
    import pandas as pd
    param_list = list(ParameterGrid(param_grid_in))
    out_df = pd.DataFrame(param_list)
    return out_df


def confusion_matrix_adj(y_true, y_accept, y_pred, labels=None):
        # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 05_UsefulSenLabel\sen_useful_GPT01.py"
    from sklearn.metrics import confusion_matrix
    """
    Compute a confusion matrix with adjustments.

    Parameters:
    y_true: Array-like of true class labels.
    y_accept: Array-like of acceptable class labels.
    y_pred: Array-like of predicted class labels.
    labels: List of label names corresponding to the classes (optional).

    Returns:
    Confusion matrix as a 2D array.
    """
    # Adjust predictions
    adjusted_pred = []
    for true, accept, pred in zip(y_true, y_accept, y_pred):
        if pred == true or pred == accept:
            adjusted_pred.append(pred)
        else:
            adjusted_pred.append(true)  # Considered as predicted 'true', actual 'true'

    # Compute confusion matrix
    return confusion_matrix(y_true, adjusted_pred, labels=labels)


def ml_upsampling(X_df, y_df, verbose = 1):
    
    import pandas as pd
    import numpy as np
    
    """
    Perform manual upsampling on a dataset to balance class distribution.

    This function upsamples the minority classes in a dataset to match the 
    number of instances in the majority class. It operates by randomly 
    duplicating instances of the minority classes.

    Parameters:
    X_df (pd.DataFrame): DataFrame containing the feature set.
    y_df (pd.Series): Series containing the target variable with class labels.
    verbose: 
        0 print nothing
        1 print out before & after upsampling
    

    Returns:
    list: Contains two elements:
        - pd.DataFrame: The upsampled feature DataFrame.
        - pd.Series: The upsampled target Series.

    Note:
    The function does not modify the input DataFrames directly. Instead, it 
    returns new DataFrames with the upsampled data. The indices of the 
    returned DataFrames are reset to maintain uniqueness.
    """
    
    
    # Determine the majority class and its count
    majority_class = y_df.value_counts().idxmax()
    majority_count = y_df.value_counts().max()
    
    if verbose == 0:
        pass
    elif verbose == 1:
        print("Before upsampling: ")
        print()
        print(y_df.value_counts())
        print()
    
    
    # Initialize the upsampled DataFrames
    X_train_oversampled = X_df.copy()
    y_train_oversampled = y_df.copy()

    # Perform manual oversampling for minority classes
    for label in y_df.unique():
        if label != majority_class:
            samples_to_add = majority_count - y_df.value_counts()[label]
            indices = y_df[y_df == label].index
            random_indices = np.random.choice(indices, samples_to_add, replace=True)
            X_train_oversampled = pd.concat([X_train_oversampled, X_df.loc[random_indices]], axis=0)
            y_train_oversampled = pd.concat([y_train_oversampled, y_df.loc[random_indices]])

    # Reset index to avoid duplicate indices
    X_train_oversampled.reset_index(drop=True, inplace=True)
    y_train_oversampled.reset_index(drop=True, inplace=True)
    
    if verbose == 0:
        pass
    elif verbose == 1:
        print("After upsampling: ")
        print()
        print(y_train_oversampled.value_counts())
        print()
    
    return [X_train_oversampled, y_train_oversampled]


# finish all of this: plot_importance, pd_regroup,
# list_dim
# (auto_cluster,auto_cluster_model,auto_n_cluster) kind of the same with diff return bc it runs very slow
# drop_feature,top_feature
# within 1 day: about 5 hrs

### !!!
def plot_importance(df,
                    feature_name = 'feature_name',
                    importance_score='importance_score',
                    group = 'group'
                    ):
    """Create a horizontal bar chart from a dataframe using seaborn.

    Args:
        df (pandas.DataFrame): The dataframe that contains three columns: 'feature_name', 'importance_score', and 'group'.

    Returns:
        None
    """
    # Create a horizontal bar plot using seaborn.barplot
    sns.barplot(x=importance_score, y=feature_name, hue=group, data=df, orient='h')

    # Set the title and labels of the plot
    plt.title('Feature Importance by Score')
    plt.xlabel('Importance Score')
    plt.ylabel('')

    # Show the plot
    plt.show(block = False)

def pd_regroup(df,value_col = "value",group_col = "group",agg="mean",ascending=False):

    # little tested
    
    """
    Regroup a dataframe by changing the group labels based on the aggregated value of each group.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to regroup.
    value_col : str, optional
        The name of the column that contains the values to aggregate. Default is "value".
    group_col : str, optional
        The name of the column that contains the original group labels. Default is "group".
    agg : {"mean", "median"}, optional
        The aggregation method to use. Default is "mean".
    ascending : bool, optional
        Whether to sort the groups in ascending order by the aggregated value. Default is False.

    Returns
    -------
    pandas.DataFrame
        A new dataframe with two columns: 'value' and 'group'. The 'value' column contains
        the values from df[value_col]. The 'group' column contains the new group labels based on the sorted
        order of the aggregated value of each group.
    """
    
    if agg == "mean":
        avg = df.groupby(group_col)[value_col].mean()
    elif agg in ["med","median"]:
        avg = df.groupby(group_col)[value_col].median()
        
    
    # Sort the average values in descending order using the sort_values method
    avg = avg.sort_values(ascending=ascending)
    
    # Create a dictionary that maps the original group labels to the new group labels based on the sorted order
    # You can use the enumerate function to assign an index to each value in avg
    dic = {k: v for v, k in enumerate(avg.index)}
    
    # Create a new dataframe called out_df that contains the 'value' and 'group' columns from temp_df
    # and assigns a new column called 'new_group' with the new group labels using the replace method and the dictionary
    out_df = df.assign(new_group=df[group_col].replace(dic))
    
    # drop old group
    out_df = out_df.drop(group_col,axis=1)
    
    #rename new_group to just group

    out_df = out_df.rename(columns={'new_group': 'group'})
    
    return out_df


def list_dim(lst):
    # Base case: empty list
    if not lst:
        return 0
    # Base case: no nested lists
    if not any(isinstance(x, list) for x in lst):
        return 1
    # Recursive case: one or more nested lists
    else:
        return 1 + max(list_dim(x) for x in lst if isinstance(x, list))

def auto_cluster(data,
                 min_cluster = 2,
                 max_cluster = 10, 
                 n_cluster = None,
                 random_state = 0, 
                 method="silhouette",
                 algorithm = "elkan",
                 mini_batch = False,
                 plot_graph = True,
                 inspect = False,
                 
                 col_name = None,
                 inplace = True,
                 graph_title = ""
                 ):
    # inplace still doesn't work seems like because pd.df is immutable
    import warnings
    import pandas as pd
    import seaborn as sns
    import numpy as np
    # tested little
    # Done
    # still slow
    # like this
    # {'MaxEStateIndex': 1.0, 'MinEStateIndex': 18.0, 'MaxPartialCharge': 12.0, 'BCUT2D_MWHI': 12.0, 'BertzCT': 10.0, 'PEOE_VSA2': 11.0, 'PEOE_VSA8': 22.0, 'SMR_VSA3': 3.0, 'NHOHCount': 17.0, 'MolLogP': 36.0}
    
    # change their fonts color by group
    # This is only 1 link that helps 
    # https://stackoverflow.com/questions/72660993/change-seaborn-heatmap-y-ticklabels-font-color-for-alternate-labels#:~:text=you%20can%20achieve%20this%20using%20ax.ticklabel.font%20%28%29.%20You,the%20neighbors.%20A%20sample%20code%20is%20given%20here.
    # test = sns.color_palette()
    
    # work with pandas 1.1.3
    # seaborn with seaborn 0.11.0
    # sklearn  with seaborn 0.23.2
    
    """
    Determine the optimal number of clusters using the Silhouette Score or Davies-Bouldin Index.

    Parameters:
    - data: The dataset for clustering.
        # data can be np.array, pd.df or list
    - random_state: Random seed for reproducibility.
    - method: Method for cluster evaluation ("silhouette" or "davies_bouldin").
    # method: 0 => silhouette, 1 => davies_bouldin
    # algorithm of clustering- to make it faster
    - min_cluster
    - max_cluster
    - n_cluster => when want to specify just 1 specific number of cluster
    - col_name => when data is df
    
    Recommend using default Silhouette for now
    
    # Silhouette Score (Higher is Better):
    # Good when: have dense, well-defined clusters.
    # Tends to produce less # of groups
    #  best 1, worst -1

    # Davies-Bouldin Index (Lower is Better):
    # Good when: irregularly shaped or overlapping clusters.
    # Tends to produce more # of groups
    # best 0, worst can be more than 1

    # right now I will normalize every score both Silhouette & Davies-Bouldin to [0,1]
    # where best is 0, worst is 0
    # using the similar scoring system as classification tasks
    
    # Example:
        
        dGeo_DriverCity_Freq = [0.912513241278375, 0.897465529502848, 0.880887540808181, 0.601136927109159, 1.01673398993431, 1.08957538723996, 0.95950964591685, 0.951814799719867, 0.824827168552231, 0.781841099023411, 0.745088310006104, 0.948326537027655, 0.926827086781722, 0.593251327148666, 1.12734771832064, 0.953953312075493, 0.794424172063922, 0.547858214986722, 0.827829286758625, 0.839784432531035, 0.731914197744046, 0.253599046491667, 0.796163971417826, 0.842343323931671, 0.92133698005692, 1.06977641274454, 0.951137647685386, 1.01706485357526, 0.814421775621783, 0.543516344907326, 1.68960297103551, 0.967838727671031, 0.906515255281029, 0.844051649794939, 0.642817054053531, 0.526315789473684, 1.06297974484912, 0.55537586711222, 0.581191681793573, 0.803961054848841, 0.752339306002181, 0.768946079826909, 1.06736414245987, 0.619895601788256, 0.860625765206219, 0.646765395461182, 0.805057421228308, 1.03220978794235, 1.18312057305214, 1.13321891541892, 0.735230757162448, 1.4072161198807, 0.844674921508448, 0.328613521034539, 0.898111702214247, 0.794269635112839, 0.995821725837276, 0.839628122246065, 0.79632330798415, 0.690795630421596, 0.417860875433496, 0.824241301011974, 0.85162757997155, 0.654840814494721]
        dGeo_DriverCity_Freq_group = f.auto_cluster(dGeo_DriverCity_Freq,plot_graph=True)
        
    Returns:
    - optimal_clusters: The optimal number of clusters.
    """
    # to suppress warning I got from fitting Kmean
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
    
    if method not in ["silhouette", "davies_bouldin",0,1,"0","1"]:
        raise ValueError("Method must be 'silhouette' or 'davies_bouldin'.")
    
    if n_cluster is not None:
        min_cluster_in = n_cluster
        max_cluster_in = n_cluster
    else:
        min_cluster_in = min_cluster
        max_cluster_in = min(len(data)-1 , max_cluster)

    # Range of cluster numbers to consider
    cluster_range = range(min_cluster_in, max_cluster_in + 1)

    # Initialize variables to store the best metric and corresponding number of clusters
    best_metric = float("-inf") if method in ["silhouette",0,"0"] else float("inf")
    optimal_clusters = None
    best_model = None
    
    if isinstance(data, np.ndarray):
        pass
        if data.ndim == 2:
            data_ = data
        elif data.ndim == 1:
            # -1 means as many rows as it needs, with 1 column
            data_ = data.reshape(-1,1)
    elif isinstance(data, list):
        data_ = np.array(data).reshape(-1,1)
    elif isinstance(data, dict):
        # in importance score style
        data_ = np.array(list(data.values())).reshape(-1,1)
        col_name = list(data.keys())
        
    elif isinstance(data, pd.DataFrame):
        data_ = np.array(data[col_name].tolist()).reshape(-1,1)
        
    
    metric_list = []
    model_list = []




    for n_clusters in cluster_range:
        # Create and fit KMeans model
        if mini_batch:
            kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=random_state,algorithm=algorithm)
        kmeans.fit(data_)

        # Calculate the chosen metric
        if method in ["silhouette",0,"0"] :
            metric = silhouette_score(data_, kmeans.labels_)
            normalize = (metric+1)/0.5
        else:  # method == "davies_bouldin"
            metric = davies_bouldin_score(data_, kmeans.labels_)
            normalize = min(metric,1)
            normalize = 1 - normalize
        
        metric_list.append(metric)
        model_list.append(kmeans)
    


    # Update the best metric and optimal number of clusters
    # if (method in ["silhouette",0,"0"] and metric > best_metric) or \
    #     (method in ["davies_bouldin",1,"1"]  and metric < best_metric):
    #     best_metric = metric
    #     optimal_clusters = n_clusters
    #     best_model = kmeans
    #     label_best = kmeans.labels_
    #     label_best = [x+1 for x in label_best]


    best_metric = max(metric_list)
    best_index = metric_list.index(best_metric)
    best_model = model_list[best_index]
    ranking = [metric_list.index(i) + 1 for i in sorted(list(metric_list),reverse=True)]

    inspect_df = pd.DataFrame({'n_cluster':cluster_range,
                                'score(Higher the better)': metric_list,
                                'rank': ranking
                                })

    if inspect:
        if plot_graph:
            sns.lineplot(x='n_cluster', y='score(Higher the better)', data=inspect_df)
        return inspect_df

    label_best = best_model.labels_
    label_best = [x+1 for x in label_best]
    

    
    if isinstance(data,dict):
        temp_df = pd.DataFrame(data=
                               {'feature_name': col_name,
                                'importance_score': data_.flatten(), 
                                'group': label_best}, 
                               
                               columns=['feature_name','importance_score', 'group'])
        out_df = pd_regroup(temp_df,value_col='importance_score')
        out_df = out_df.sort_values(by = 'importance_score',ascending = False)
        out_df.reset_index(drop=True,inplace=True)
        if plot_graph:
            plot_importance(out_df)
        
    else:
        temp_df = pd.DataFrame(data={'value': data_.flatten(), 'group': label_best}, columns=['value', 'group'])
        # reorder the group according the their values
        
        # lowest group corresponded to lowest values 
        forplot_df = pd_regroup(temp_df,ascending = True)
        forplot_df = forplot_df.sort_values(by = 'value',ascending = True)
        forplot_df.reset_index(drop=True,inplace=True)
        
        forplot_df['group'] = forplot_df['group'] + 1
        
        forplot_df['group'] = forplot_df['group'].astype('category')

        
        x_num = list(range(forplot_df.shape[0]))
        
        if plot_graph:
            plt.figure(figsize=(8,6))
            sns.scatterplot(data = forplot_df,x=x_num,y="value",hue="group").set_title(graph_title)
            plt.xlabel('number of data')
            plt.show(block = False)

        forplot_df['group'] = forplot_df['group'].astype('int')
        regroup = forplot_df.drop_duplicates(subset=['value'])
        
        out_df = temp_df.drop(columns="group").merge(regroup,on = "value", how="left")
        
        
        if isinstance(data, pd.DataFrame):
            if inplace:
                data = data.merge(out_df, left_on = col_name, right_on = 'value')
                data = data.drop(columns = ['value'])
                data = data.rename(columns = {'group': col_name + '_group'})
                return data

    return out_df

def auto_cluster_model(data,
                 min_cluster = 2,
                 max_cluster = 10, 
                 random_state = 0, 
                 method="silhouette",
                 algorithm = "elkan",
                 mini_batch = True,
                 
                 ):
    # still slow
    
    """
    Determine the optimal number of clusters using the Silhouette Score or Davies-Bouldin Index.

    Parameters:
    - data: The dataset for clustering.
    - random_state: Random seed for reproducibility.
    - method: Method for cluster evaluation ("silhouette" or "davies_bouldin").
    # method: 0 => silhouette, 1 => davies_bouldin
    # algorithm of clustering- to make it faster
    - min_cluster
    - max_cluster
    
    
    # Silhouette Score (Higher is Better):
    # Good when: have dense, well-defined clusters.

    # Davies-Bouldin Index (Lower is Better):
    # Good when: irregularly shaped or overlapping clusters.

    Returns:
    - best_model: Best model from auto_clustering
    """
    # to suppress warning I got from fitting Kmean
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
    
    if method not in ["silhouette", "davies_bouldin",0,1,"0","1"]:
        raise ValueError("Method must be 'silhouette' or 'davies_bouldin'.")

    # Range of cluster numbers to consider
    cluster_range = range(min_cluster, max_cluster + 1)

    # Initialize variables to store the best metric and corresponding number of clusters
    best_metric = float("-inf") if method in ["silhouette",0,"0"] else float("inf")
    optimal_clusters = None
    best_model = None
    
    if isinstance(data, np.ndarray):
        pass
        if data.ndim == 2:
            data_ = data
        elif data.ndim == 1:
            # -1 means as many rows as it needs, with 1 column
            data_ = data.reshape(-1,1)
    elif isinstance(data, list):
        data_ = np.array(data).reshape(-1,1)
    elif isinstance(data, dict):
        pass
    

    for n_clusters in cluster_range:
        # Create and fit KMeans model
        if mini_batch:
            kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=random_state,algorithm=algorithm)
        kmeans.fit(data_)

        # Calculate the chosen metric
        if method in ["silhouette",0,"0"] :
            metric = silhouette_score(data_, kmeans.labels_)
        else:  # method == "davies_bouldin"
            metric = davies_bouldin_score(data_, kmeans.labels_)

        # Update the best metric and optimal number of clusters
        if (method in ["silhouette",0,"0"] and metric > best_metric) or \
           (method in ["davies_bouldin",1,"1"]  and metric < best_metric):
            best_metric = metric
            optimal_clusters = n_clusters
            best_model = kmeans
            label_best = kmeans.labels_

    return best_model

def auto_n_cluster(data,
                 min_cluster = 2,
                 max_cluster = 10, 
                 random_state = 0, 
                 method="silhouette",
                 algorithm = "elkan",
                 mini_batch = True,
                 
                 ):
    # still slow
    
    """
    Determine the optimal number of clusters using the Silhouette Score or Davies-Bouldin Index.

    Parameters:
    - data: The dataset for clustering.
    - random_state: Random seed for reproducibility.
    - method: Method for cluster evaluation ("silhouette" or "davies_bouldin").
    -  algorithm of clustering- to make it faster
    - min_cluster
    - max_cluster


    # Silhouette Score (Higher is Better):
    # Good when: have dense, well-defined clusters.

    # Davies-Bouldin Index (Lower is Better):
    # Good when: irregularly shaped or overlapping clusters.
    

    Returns:
    - optimal_clusters: The optimal number of clusters.
    """
    # to suppress warning I got from fitting Kmean
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
    
    if method not in ["silhouette", "davies_bouldin",0,1,"0","1"]:
        raise ValueError("Method must be 'silhouette' or 'davies_bouldin'.")

    # Range of cluster numbers to consider
    cluster_range = range(min_cluster, max_cluster + 1)

    # Initialize variables to store the best metric and corresponding number of clusters
    best_metric = float("-inf") if method in ["silhouette",0,"0"] else float("inf")
    optimal_clusters = None
    
    

    for n_clusters in cluster_range:
        # Create and fit KMeans model
        if mini_batch:
            kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=random_state,algorithm=algorithm)
        kmeans.fit(data)

        # Calculate the chosen metric
        if method in ["silhouette",0,"0"] :
            metric = silhouette_score(data, kmeans.labels_)
        else:  # method == "davies_bouldin"
            metric = davies_bouldin_score(data, kmeans.labels_)

        # Update the best metric and optimal number of clusters
        if (method in ["silhouette",0,"0"] and metric > best_metric) or \
           (method in ["davies_bouldin",1,"1"]  and metric < best_metric):
            best_metric = metric
            optimal_clusters = n_clusters

    return optimal_clusters

def drop_feature(score_dict,
                     n_drop = 1,
                     return_as_list = False,
                     plot_graph = True,
                     min_cluster = 2,
                     max_cluster = 10, 
                     random_state = 0, 
                     method="silhouette",
                     algorithm = "elkan",
                     mini_batch = False,
                ):
    # medium tested
    rank_df = auto_cluster(score_dict,min_cluster,max_cluster,random_state,method,algorithm,mini_batch,plot_graph)
    
    n_group = rank_df['group'].max()
    
    condition = (rank_df['group'] < n_group - n_drop + 1)
    
    out_df = rank_df.loc[condition,:]
    col_list = out_df['feature_name'].tolist()
    
    if return_as_list:
        return col_list
    else:
        return out_df

def top_feature(score_dict,
                     n_top = 1,
                     return_as_list = False,
                     plot_graph = True,
                     min_cluster = 2,
                     max_cluster = 10, 
                     random_state = 0, 
                     method="silhouette",
                     algorithm = "elkan",
                     mini_batch = False,
                ):
    # medium tested
    """
    

    Parameters
    ----------
    score_dict : TYPE
        DESCRIPTION.
    n_top : TYPE, optional
        n_top used cluster group not top_n columns but top_n group
        The default is 1.
        
    return_as_list : TYPE, optional
        DESCRIPTION. The default is False.
    plot_graph : TYPE, optional
        DESCRIPTION. The default is True.
    min_cluster : TYPE, optional
        DESCRIPTION. The default is 2.
    max_cluster : TYPE, optional
        DESCRIPTION. The default is 10.
    random_state : TYPE, optional
        DESCRIPTION. The default is 0.
    method : TYPE, optional
        DESCRIPTION. The default is "silhouette".
    algorithm : TYPE, optional
        DESCRIPTION. The default is "elkan".
    mini_batch : TYPE, optional
        DESCRIPTION. The default is False.
     : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    rank_df = auto_cluster(score_dict,min_cluster,max_cluster,random_state,method,algorithm,mini_batch,plot_graph)
    
    condition = (rank_df['group'] < n_top)
    
    out_df = rank_df.loc[condition,:]
    col_list = out_df['feature_name'].tolist()
    
    if return_as_list:
        return col_list
    else:
        return out_df

def archive():
    # Example usage
    random_state = 15
    # random_state = 15: distinct
    # Generate some sample data (replace with your dataset)
    np_2d, label, center  = make_blobs(n_samples=40, 
                                    centers=5, 
                                    random_state=random_state,
                                    n_features=1,
                                    return_centers=True,
                                    center_box = (-100,100))
    center = -np.sort(-center,axis=0)

    sns.scatterplot(np_2d)  # Replace with your dataset
    plt.show(block = False)

    np_1d = np_2d.flatten()

    lst01 = np_2d.flatten().tolist()

    dict01 = {'MaxEStateIndex': 1.0, 'MinEStateIndex': 18.0, 'MaxPartialCharge': 12.0, 'BCUT2D_MWHI': 12.0, 'BertzCT': 10.0, 'PEOE_VSA2': 11.0, 'PEOE_VSA8': 22.0, 'SMR_VSA3': 3.0, 'NHOHCount': 17.0, 'MolLogP': 36.0}


    ans_list_01 = auto_cluster(lst01, random_state=random_state,plot_graph = False)


    # davies_bouldin = auto_cluster(lst01, method=1,mini_batch=False,random_state=random_state)
    # print("Optimal clusters (Davies-Bouldin Index):", davies_bouldin)

    # Find the optimal number of clusters using Silhouette Score
    # plot_graph = False to make it run faster
    ans_dict_01 = auto_cluster(dict01, random_state=random_state,plot_graph = False)

    # Find the optimal number of clusters using Davies-Bouldin Index
    # davies_bouldin = auto_cluster(dict01, method=1,mini_batch=False,random_state=random_state)
    # print("Optimal clusters (Davies-Bouldin Index):", davies_bouldin)

    ans01 = drop_feature(dict01,2)
    ans02 = drop_feature(dict01,return_as_list=True)
    ans03 = top_feature(dict01,n_top=3)
    print("Yeah")
    
def main():
    pass

if __name__ == '__main__':
    main()




