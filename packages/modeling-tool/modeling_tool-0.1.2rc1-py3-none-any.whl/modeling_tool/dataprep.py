import inspect
from typing import *
import pandas as pd
def upsampling(X_df:Union[pd.DataFrame], y_df:Union[pd.DataFrame], verbose = 1):
    
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


# prevent showing many objects from import when importing this module
# from typing import *
__all__ = [name for name, obj in globals().items() 
           if inspect.isfunction(obj) and not name.startswith('_')]
