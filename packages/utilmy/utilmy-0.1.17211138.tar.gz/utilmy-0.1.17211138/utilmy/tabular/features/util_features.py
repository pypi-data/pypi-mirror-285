"""


"""


def features_prepro_fit_transform(dftrain):
  import numpy as np
  import pandas as pd
  from sklearn.compose import ColumnTransformer
  from sklearn.pipeline import Pipeline
  from sklearn.model_selection import train_test_split
  from category_encoders import CountEncoder, OrdinalEncoder
  from sklearn.base import BaseEstimator, TransformerMixin
  from sklearn.preprocessing import StandardScaler, QuantileTransformer
  from sklearn.impute import SimpleImputer
  from joblib import dump

  # Custom Transformers
  from lag_transformer import LagTransformer
  from groupby_transformer import GroupByTransformer
  from drop_transformer import DropColumns

  cols_drop = ["ymd", "y", "dt", "dt-month"]

  cols_leak = [
      *[f"fe-{field}" for field in ["n_clk", "n_imp", "n_cta"]],
      *[f"com-{field}" for field in ["n_clk", "n_imp", "n_cta"]],
      *[f"qkey-{field}" for field in ["n_clk", "n_imp", "n_cta"]],
      *[f"comcat1_hash-{field}" for field in ["n_clk", "n_imp", "n_cta"]],
  ]

  cols_targetenc = [
      'dt-day',
      'dt-hour',
      'dt-weekday',
      'dt-islunch',
      'dt-isevening',
      'dt-isweekend',
      "hh",
      "qkey",
      'qkey-zoom',
      'qkey-qhash', 'qkey-a', 'qkey-b', 'qkey-c', 'qkey-1',
      "fe",
  ]

  cols_ordinalenc = [
      "com",
      "comcat1_hash"
  ]

  ytrain = dftrain['y']
  cols_D = [col for col in dftrain.columns if '10D' in col or '30D' in col]

  # Lags
  lag_window = 1

  preprocessing_steps = [
      # Lags
      ('lags', LagTransformer(leak_cols=cols_leak, lags=lag_window)),

      # Drop
      ('drop_cols', DropColumns(cols_drop + cols_leak)),

      # Rolling Mean
      ('groupby_4H', GroupByTransformer(
          ['dt-day', 'dt-hour', 'dt-weekday'], cols_D, window=4, min_periods=1, label='4H')),
      ('groupby_8H', GroupByTransformer(
          ['dt-day', 'dt-hour', 'dt-weekday'], cols_D, window=8, min_periods=1, label='8H')),
      ('groupby_3D', GroupByTransformer(
          ['dt-day', 'dt-weekday'], cols_D, window=3, min_periods=1, label='3D')),
      ('groupby_7D', GroupByTransformer(
          ['dt-day', 'dt-weekday'], cols_D, window=7, min_periods=1, label='7D')),

      ('groupby_fe_3D', GroupByTransformer(
          ['fe'], cols_D, window=3, min_periods=1, label='fe_3D')),
      ('groupby_fe_7D', GroupByTransformer(
          ['fe'], cols_D, window=7, min_periods=1, label='fe_7D')),

      ('groupby_com_3D', GroupByTransformer(
          ['com'], cols_D, window=3, min_periods=1, label='com_3D')),
      ('groupby_com_7D', GroupByTransformer(
          ['com'], cols_D, window=7, min_periods=1, label='com_7D')),

      ('groupby_qkey_3D', GroupByTransformer(
          ['qkey'], cols_D, window=3, min_periods=1, label='qkey_3D')),
      ('groupby_qkey_7D', GroupByTransformer(
          ['qkey'], cols_D, window=7, min_periods=1, label='qkey_7D')),

      # Encoding
      ('cat_encoders', ColumnTransformer([
          ('count_encoder', CountEncoder(), cols_targetenc),
          ('ordinal_encoder', OrdinalEncoder(), cols_ordinalenc)
      ], remainder='passthrough')),

      # Scaling
      ('quantile', QuantileTransformer(n_quantiles=1000,
        output_distribution="normal", random_state=42))
  ]

  # Define Preprocessor
  preprocessor = Pipeline(preprocessing_steps)

  # Preprocess train data
  preprocessor.fit(dftrain, ytrain)
  Xtrain = preprocessor.transform(dftrain)

  #print(Xtrain.shape, ytrain.shape)

  def getFeatureNamesOut():
      feature_names = preprocessor.named_steps['cat_encoders'].get_feature_names_out()

      for i in range(len(feature_names)):
          feature_names[i] = feature_names[i].split('__')[1]

      return feature_names

  feature_names = getFeatureNamesOut()
  #print(feature_names)

  # Save pipeline
  dump(preprocessor, 'pre_pipeline.joblib')

  Xtrain = pd.DataFrame(Xtrain, columns=feature_names)
  #If using lags
  Xtrain.dropna(axis=0, inplace=True)
  ytrain = ytrain.iloc[:-lag_window]

  Xtrain.reset_index(drop=True, inplace=True)
  ytrain.reset_index(drop=True, inplace=True)

  return Xtrain, ytrain

def features_prepro_transform_only(dfeval, preprocessor):
  import pandas as pd

  # Preprocess test data using the loaded pipeline
  y_test = dfeval['y']
  X_test_transformed = preprocessor.transform(dfeval)

  def getFeatureNamesOut():
      feature_names = preprocessor.named_steps['cat_encoders'].get_feature_names_out()

      for i in range(len(feature_names)):
          feature_names[i] = feature_names[i].split('__')[1]

      return feature_names
  
  feature_names_after_preprocessing = getFeatureNamesOut()

  X_test_transformed = pd.DataFrame(X_test_transformed, columns=feature_names_after_preprocessing)

  # If using lags
  X_test_transformed.dropna(axis=0, inplace=True)
  y_test = y_test.iloc[:-(y_test.shape[0] - X_test_transformed.shape[0])]

  X_test_transformed.reset_index(drop=True, inplace=True)
  y_test.reset_index(drop=True, inplace=True)

  #print("Feature names after preprocessing:", feature_names_after_preprocessing)
  #print("Shape of X_test_transformed:", X_test_transformed.shape)

  return X_test_transformed, y_test

import numpy as np
import pandas as pd
from joblib import load

# Train -> dump 
parquet_train = "../dftrain.parquet"
dftrain = pd.read_parquet(parquet_train)
dftrain = dftrain[dftrain.ymd < 20230819]
dftrain = dftrain[:10000]
X_train, y_train = features_prepro_fit_transform(dftrain)
print(X_train.shape, y_train.shape)

# Load -> Test
preprocessor = load('pre_pipeline.joblib')
parquet_test = "../dfeval.parquet"
dfeval = pd.read_parquet(parquet_test)
dfeval = dfeval[:10000]
X_test, y_test = features_prepro_transform_only(dfeval, preprocessor)
print(X_test.shape, y_test.shape)



###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
