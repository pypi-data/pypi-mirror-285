"""



"""
#%load_ext cudf.pandas
result_list = []
path = '/content/drive/MyDrive/data3-final/'

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
  dump(preprocessor, path + 'pre_pipeline.joblib')

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

def runExperiment01(label, setup = 0, gpu = False):
  import pandas as pd
  from sklearn.utils import shuffle
  import seaborn as sns
  import plotly.express as px
  import matplotlib.pyplot as plt
  import gc
  import numpy as np
  from datetime import datetime
  from sklearn.model_selection import StratifiedKFold, KFold
  from sklearn.metrics import f1_score
  from lightgbm import LGBMClassifier
  import category_encoders as ce
  from sklearn.model_selection import train_test_split
  from sklearn.pipeline import make_pipeline
  from sklearn.preprocessing import StandardScaler, FunctionTransformer
  from sklearn.compose import ColumnTransformer
  from sklearn.feature_selection import VarianceThreshold, SelectFromModel, SelectKBest, mutual_info_classif
  from sklearn.ensemble import HistGradientBoostingClassifier
  #from sktools import GradientBoostingFeatureGenerator
  from sklearn.impute import SimpleImputer
  #import optuna
  import xam
  import lightgbm as lgb
  import holidays
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.compose import make_column_transformer
  #from autogluon.features.generators import AutoMLPipelineFeatureGenerator
  from IPython.display import clear_output
  from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    Normalizer,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
    minmax_scale,
  )
  from dirty_cat import (
    SimilarityEncoder,
    TargetEncoder,
    MinHashEncoder,
    GapEncoder,
  )
  from joblib import load

  ### Load Data

  RANDOM_STATE = 42
  #result_list = [] # Create it outside

  best_params = {
    'objective': "binary",
    "random_state": RANDOM_STATE,
    'n_estimators': 1000,
    'learning_rate': 0.05,
    'num_leaves': 100,
    'max_depth': -1,
    'min_data_in_leaf': 100,
    'max_bin': 255,
    'lambda_l1': 0.1,
    'early_stopping_rounds': 300
  }

  if gpu:
    best_params = {
      'objective': "binary",
      "random_state": RANDOM_STATE,
      'n_estimators': 1000,
      'learning_rate': 0.05,
      'num_leaves': 100,
      'max_depth': -1,
      'min_data_in_leaf': 100,
      'max_bin': 255,
      'lambda_l1': 0.1,
      'early_stopping_rounds': 300,

      'boosting_type': 'gbdt',
      'device': 'gpu',
      'gpu_platform_id': 0,
      'gpu_device_id': 0
    }

  ### Functions
  def reduce_mem_usage(df):
    start_mem = df.memory_usage().sum() / 1024**2
    print(f'Memory usage of dataframe is {start_mem:.2f} MB')

    for col in df.columns:
        col_type = df[col].dtype

        if pd.api.types.is_numeric_dtype(col_type):
            df[col] = pd.to_numeric(df[col], downcast='integer', errors='coerce')
            if col_type != 'int' and col_type != 'float':
                df[col] = pd.to_numeric(df[col], downcast='float', errors='coerce')
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif pd.api.types.is_categorical_dtype(col_type):
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024**2
    print(f'Memory usage after optimization is: {end_mem:.2f} MB')
    print(f'Decreased by {100 * (start_mem - end_mem) / start_mem:.1f}%')

    return df

  def plotExperiments():
    result_df = pd.DataFrame(result_list, columns=['f1_score', 'label', 'time'])
    result_df['time'] = result_df['time'].dt.seconds
    result_df['model'] = result_df['label'].str.split().str[0]
    result_df = result_df.loc[result_df.groupby('label')['f1_score'].idxmax()]

    result_df = result_df.sort_values('f1_score', ascending=False)
    result_df = result_df.drop_duplicates()

    plt.figure(figsize=(6, len(result_df) * 0.4))

    def color_map(row):
      if row['label'].startswith('*'):
        return 'green'
      if row['f1_score'] > 0.8:
        return 'lightgreen'
      return 'yellow'

    colors = result_df.apply(color_map, axis=1)
    bars = plt.barh(range(len(result_df)), result_df['f1_score'], color=colors)

    for bar, f1 in zip(bars, result_df['f1_score']):
      plt.text(min(bar.get_width() + 0.01, 0.895), bar.get_y() + bar.get_height()/2, f'{f1:.4f}', ha='center', va='center')

    plt.yticks(range(len(result_df)), result_df['label'])
    plt.gca().invert_yaxis()
    plt.xlim(0.6, 1)
    plt.xticks([0.6, 0.65, 0.7, 0.75, 0.80, 0.85, 0.9, 0.95, 1.0])
    plt.xlabel('f1 score (higher is better)')
    plt.show()

  def featureSelection(X_train, y_train, X_test, y_test):
    # Feature Selection with 15% of data sampled.
    threshold = 0.15

    # Train Sample ~1M * 0.15 = 150k
    X_train_sampled = X_train.sample(frac=threshold, random_state=RANDOM_STATE)
    sampled_indices = X_train_sampled.index
    y_train_sampled = y_train.loc[sampled_indices]

    # Test Sample ~500k * 0.15 = 75k
    X_test_sampled = X_test.sample(frac=threshold, random_state=RANDOM_STATE)
    sampled_indices = X_test_sampled.index
    y_test_sampled = y_test.loc[sampled_indices]

    # Create Random Variable
    X_train_sampled['Random'] = np.random.uniform(0, 1, len(X_train_sampled))
    X_test_sampled['Random'] = np.random.uniform(0, 1, len(X_test_sampled))

    # Train
    model = LGBMClassifier(**best_params, verbose=-1)
    model.fit(X_train_sampled, y_train_sampled, eval_set=[(X_test_sampled, y_test_sampled)])

    # Importance Filter
    importance_df = pd.DataFrame({'Feature': X_train_sampled.columns, 'Importance': model.feature_importances_})
    threshold_importance = importance_df.loc[importance_df['Feature'] == 'Random', 'Importance'].item()
    selected_features = importance_df[importance_df['Importance'] > threshold_importance]['Feature'].to_list()

    return X_train[selected_features], X_test[selected_features]

  ### Training & Test
  start_time = datetime.now()

  parquet_train = path + "dftrain.parquet"
  parquet_eval = path + "dfeval.parquet"

  dftrain = pd.read_parquet(parquet_train)
  dfeval = pd.read_parquet(parquet_eval)
  dftrain = dftrain[ dftrain.ymd < 20230819 ]

  dftrain = reduce_mem_usage(dftrain)
  dfeval = reduce_mem_usage(dfeval)

  # Pipeline Usage
  X_train, y_train = features_prepro_fit_transform(dftrain)
  preprocessor = load(path + 'pre_pipeline.joblib')
  X_test, y_test = features_prepro_transform_only(dfeval, preprocessor)

  X_train, X_test = featureSelection(X_train, y_train, X_test, y_test)

  # Training
  model = LGBMClassifier(**best_params, verbose=-1)
  model.fit(X_train, y_train, eval_set=[(X_test, y_test)])

  yval_pred = model.predict(X_test)
  score     = f1_score(y_test, yval_pred )

  execution_time = datetime.now() - start_time

  clear_output()

  print('F1 Score:', score)
  result_list.append((score, label, execution_time))
  plotExperiments()

  return model, X_train.columns

### Run
runExperiment01('Test')


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


