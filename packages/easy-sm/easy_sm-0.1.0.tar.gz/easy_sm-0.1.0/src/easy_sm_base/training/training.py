import statsmodels.api as sm
from patsy import dmatrices
import pandas as pd
import joblib
import os

def train(input_data_path, model_save_path, hyperparams_path=None):
    """
    The function to execute the training.

    :param input_data_path: [str], input directory path where all the training file(s) reside in
    :param model_save_path: [str], directory path to save your model(s)
    :param hyperparams_path: [optional[str], default=None], input path to hyperparams json file.
    Example:
        {
            "max_leaf_nodes": 10,
            "n_estimators": 200
        }
    """
    # TODO: If exists, read in hyperparams file JSON content

    # TODO: Write your modeling logic
    mpg = pd.read_csv(os.path.join(input_data_path, 'mpg.csv'))
    y, X = dmatrices('mpg ~ weight + horsepower', mpg, return_type="dataframe")
    ols = sm.OLS(y.values.ravel(), X.values).fit()
    print(ols.summary())

    # TODO: save the model(s) under 'model_save_path'
    joblib.dump(ols, os.path.join(model_save_path, 'model.mdl'))
