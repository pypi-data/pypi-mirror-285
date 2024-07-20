import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def get_categorical_data(df: pd.DataFrame):
    """
    This function is responsable for the identification of categorical and date features.

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :return: DataFrame with only categorical and date data types
    :rtype: DataFrame
    """

    return df.select_dtypes(include=['object'])


def get_numerical_data(df: pd.DataFrame):
    """
    This function is responsable for the identification of numerical features.

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :return: DataFrame with only numerical data types
    :rtype: DataFrame
    """

    return df.select_dtypes(include=['number', 'float64', 'int64'])


def handle_missing_data(df: pd.DataFrame, strategy_numerical='mean', strategy_categorical='most_frequent'):
    """
    This function is responsable for fill missings in dataFrame for numerical and categorical features with the substitution value passed by the user.

    Args:
        df: Pandas DataFrame
        strategy_numerical (str): Estratégia para lidar com valores ausentes em colunas numéricas.
                                   Opções são 'mean' (média), 'median' (mediana), 'most_frequent' (valor mais frequente).
        strategy_categorical (str): Estratégia para lidar com valores ausentes em colunas categóricas.
                                     Opções são 'most_frequent' (valor mais frequente) ou 'constant' (valor constante).

    Returns:
        tuple: Dados de treinamento e teste com valores ausentes tratados.
    """
    categorical_data = get_categorical_data(df)
    numerical_data = get_numerical_data(df)

    if len(categorical_data.columns) == 0:
        imputer_numerical = SimpleImputer(strategy=strategy_numerical)
        df_imputed_numerical = imputer_numerical.fit_transform(numerical_data)
        df_imputed = pd.DataFrame(df_imputed_numerical, columns=numerical_data.columns)

    else:
        # Cria um SimpleImputer para tratar valores ausentes em colunas numéricas
        imputer_numerical = SimpleImputer(strategy=strategy_numerical)
        df_imputed_numerical = imputer_numerical.fit_transform(numerical_data)

        # Cria um SimpleImputer para tratar valores ausentes em colunas categóricas
        imputer_categorical = SimpleImputer(strategy=strategy_categorical)
        df_imputed_categorical = imputer_categorical.fit_transform(categorical_data)

        # Concatena os dados imputados com as outras colunas
        df_imputed = pd.concat([pd.DataFrame(df_imputed_numerical, columns=numerical_data.columns),
                                pd.DataFrame(df_imputed_categorical, columns=categorical_data.columns)], axis=1)

    return df


def normalize_numerical_data(df: pd.DataFrame):
    """
    This function is responsable for normilize numerical data

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :return: DataFrame with numerical data normilized
    :rtype: DataFrame
    """

    numeric_columns = df.select_dtypes(include=['number', 'float64', 'int64']).columns
    scaler = StandardScaler(with_mean=True)
    df_normalized = scaler.fit_transform(df[numeric_columns])

    return pd.DataFrame(df_normalized, columns=numeric_columns)


def encode_nominal_categorical_data(df: pd.DataFrame, nominal_categorical_columns: list = None):
    """
    This function is responsable for encode nominal categorical data.

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :param nominal_categorical_columns: List of nominal categorical columns
    :type: List
    :return: DataFrame with nominal data encoded
    :rtype: DataFrame
    """

    # Encontra as colunas categóricas
    if nominal_categorical_columns is None:
        categorical_data = get_categorical_data(df)
        categorical_columns = categorical_data.columns
    else:
        categorical_columns = nominal_categorical_columns
        categorical_data = df[[categorical_columns]]

    # Codifica os dados categóricos usando one-hot encoding
    if len(categorical_data.columns) != 0:
        encoder = OneHotEncoder()
        df_encoded = encoder.fit_transform(df.iloc[:, categorical_columns])

        # Concatena os dados codificados com as outras colunas
        df_normalized = np.hstack([df_encoded, df.drop(df.columns[categorical_columns], axis=1)])

        return df_normalized
    else:
        return df


def encode_ordinal_categorical_data(df: pd.DataFrame, ordinal_categorical_columns: list = None):
    """
    This function is responsable for encode ordinal categorical data.

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :param ordinal_categorical_columns: List of ordinal categorical columns
    :type: List
    :return: DataFrame with ordinal data encoded
    :rtype: DataFrame
    """

    # Encontra as colunas categóricas
    if ordinal_categorical_columns is None:
        categorical_data = get_categorical_data(df)
        categorical_columns = categorical_data.columns
    else:
        categorical_columns = ordinal_categorical_columns
        categorical_data = df[[categorical_columns]]
    if len(categorical_data.columns) != 0:
        # Codifica os dados categóricos usando codificação ordinal
        encoder = OrdinalEncoder()
        df_encoded = encoder.fit_transform(df.iloc[:, categorical_columns])

        # Concatena os dados codificados com as outras colunas
        df_normalized = np.hstack([df_encoded, df.drop(df.columns[categorical_columns], axis=1)])

        return df_normalized
    else:
        return df


def regression_pipeline(df: pd.DataFrame, target_column, algorithm='random_forest',
                        ordinal_categorical_columns: list = None, nominal_categorical_columns: list = None,
                        strategy_numerical='mean', strategy_categorical='most_frequent', metrics: list = None):
    """
    Executes regression pipeline.

    :param df: Pandas DataFrame
    :type: pd.DataFrame
    :param target_column: data to predict
    :type: str
    :param algorithm: algorithm ('random_forest', 'gradient_boosting', 'mlp', 'svm', 'xgboost')
    :type: str
    :param ordinal_categorical_columns: List of ordinal categorical columns
    :type: List
    :param nominal_categorical_columns: List of nominal categorical columns
    :type: List
    :param strategy_numerical: Strategy to deal with nan values on numerical columns
    :type: str
    :param strategy_categorical: Strategy to deal with nan values on categorical columns
    :type: str
    :param metrics: list of metrics to return
    :type: List
    :return: y_pred with predicted target values
    :rtype: pd.Series
    :return: metrics_dict, dictionary of evaluation metrics
    :rtype: Dictionary

    Returns:
        model: Modelo treinado
        mse: Mean Squared Error do modelo
    """
    df = handle_missing_data(df, strategy_numerical, strategy_categorical)
    df = normalize_numerical_data(df)
    df = encode_nominal_categorical_data(df)
    df = encode_ordinal_categorical_data(df)

    # Dividir os dados em conjuntos de treinamento e teste
    y = df[target_column]
    X = df.drop(columns=[target_column])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinar modelo de regressão
    models = {
        'random_forest': RandomForestRegressor(),
        'gradient_boosting': GradientBoostingRegressor(),
        'mlp': MLPRegressor(),
        'svm': SVR(),
        'xgboost': XGBRegressor()
    }
    if algorithm not in models:
        raise ValueError("Algoritmo de regressão não reconhecido.")

    model = models[algorithm]
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics_dict = {}
    if metrics:
        if 'mse' in metrics:
            metrics_dict['mse'] = mean_squared_error(y_test, y_pred)
        if 'r2' in metrics:
            metrics_dict['r2'] = r2_score(y_test, y_pred)
        if 'mae' in metrics:
            metrics_dict['mae'] = mean_absolute_error(y_test, y_pred)
        if 'rmse' in metrics:
            metrics_dict['rmse'] = mean_squared_error(y_test, y_pred, squared=False)

    return y_pred, metrics_dict
