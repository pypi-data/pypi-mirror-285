import pandas as pd
import numpy as np
import plotly.graph_objects as go


class Portfolio:
    def cagr_assets(
        date_start: pd.to_datetime, date_end: pd.to_datetime, df_prices: pd.DataFrame
    ):

        """
    This function calculates the compound annual growth rate of the portfolio assets
    individually passsed in the df parameter
    :param date_start: start date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param date_end: end date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    """
        n_months = (date_end.year - date_start.year) * 12 + (
            date_end.month - date_start.month
        )
        cagr_asset = (df_prices.iloc[-1] - df_prices.iloc[0]) / df_prices.iloc[0]
        cagr_asset = ((1 + cagr_asset) ** (12 / n_months)) - 1
        return cagr_asset

    def cagr_portfolio(
        date_start: pd.to_datetime,
        date_end: pd.to_datetime,
        df_prices: pd.DataFrame,
        weights: np.array,
    ):

        """
    This function calculates the compound annual growth rate of the portfolio assets
    passsed in the df_prices parameter
    :param date_start: start date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param date_end: end date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    :param weights numpy array of float weights - must sum 100%
    :type np.array
    """
        n_months = (date_start.year - date_end.year) * 12 + (
            date_end.month - date_start.month
        )
        cagrportfolio = (df_prices.iloc[-1] - df_prices.iloc[0]) / df_prices.iloc[0]
        cagrportfolio = ((1 + cagrportfolio) ** (12 / n_months)) - 1
        cagrportfolio = cagrportfolio.dot(weights)
        return cagrportfolio

    def vol_carteira(df_prices: pd.DataFrame, weights: np.array, cov: pd.DataFrame):

        """
    This function calculates the portfolio standard deviation
    
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    :param pesos numpy array of assets weights (float)
    :type np.array
    :param cov: covariance matrix of portfolio returns
    :type pd.DataFrame 
    """

        daily_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
        yearly_vol = daily_vol * np.sqrt(252)
        return yearly_vol

    def marginal_risk_contribution(
        assets: np.array, cov_matrix: pd.DataFrame, weights: np.array
    ):
        """
    This function calculates the marginal risk contribution of each asset in the portfolio
    
    :param assets list of asset names str
    :type np.array
    :param cov_matrix covariance matrix of assets returns
    :type pd.DataFrame
    :param weights array of float weights of portfolio allocation,  must sum 100%
    :type np.array
    """

        # Calcular o risco total da carteira
        portfolio_var = np.dot(pesos.T, np.dot(cov_matrix.values, weights))

        # Calcular a contribuição de risco de cada ativo
        contribuicao_risco = []
        for i, symbol in enumerate(assets):
            variancia = cov_matrix.iloc[i][i]
            pesos_ativos = pesos[i]
            cm_ativos = pesos_ativos ** 2 * variancia / portfolio_var
            contribuicao_risco.append(cm_ativos)

        return pd.Series(
            contribuicao_risco,
            index=carteira.columns,
            name="Marginal Risk Contribution",
        )

    def benchmark_ibov(
        date_start: pd.to_datetime,
        date_end: pd.to_datetime,
        df_prices: pd.DataFrame,
        index_code: str,
    ):
        """
    This function show a graphic of a benchmark portfolio comparison with an index
    
    :param date_start: start date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param date_end: end date format 'YYYY-MM-DD'
    :type pd.to_datetime
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    :param index_code Yahoo Finance index code. Examples: ^BVSP(Corresponding to Ibovespa), ^GSPC(Corresponding to S&P500)
    :type str
    """

        index = yf.download("^BVSP", start=data_inicio, end=data_fim)["Close"]
        df_prices = carteira
        df_prices = carteira.pct_change()
        df_prices.fillna(0, inplace=True)
        df_prices = (1 + df_prices).cumprod()
        df_prices = pd.Series((df_prices * pesos).sum(axis=1), name="Carteira")
        index_returns = index.pct_change()
        index_returns.fillna(0, inplace=True)
        benchmark_ibov = (1 + index_returns).cumprod()
        benchmark = pd.merge(
            df_prices, benchmark_ibov, how="inner", left_index=True, right_index=True
        )
        benchmark.rename(columns={"Close": "Benchmark"}, inplace=True)

        return benchmark.iloc[-1], benchmark.plot(figsize=(10, 6))

    def janela_volatilidade(df_prices: pd.DataFrame, window: int, weights: np.array):
        """
     This function show volatility window of a portfolio or asset
    
     :param df_prices dataframe of Adjusted close portfolio data
     :type pd.DataFrame
     :param window window days size
     :type str
     :param weights array of weights portfolio allocation
     :type np.array
     
     """
        retornos = df_prices.pct_change()
        retornos = pd.Series((retornos * weights).sum(axis=1), name="Portfolio")
        rolling_vol = retornos.rolling(window=window).std()

        return rolling_vol.plot(figsize=(10, 6))

    def sharpe_ratio(df_prices: pd.Dataframe, rf: float, vol: float, weights: np.array):
        """
    This function calculates the Sharpe Ratio of a portfolio
    
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    :param rf risk free rate
    :type float
    :param vol portfolio volatility
    :type float
    """
        retornos = df_prices.pct_change().dropna()
        retornos = (retornos * weights).sum(axis=1)
        sharpe_ratio = ((retornos.mean() * 252) - rf) / (vol)
        return display(sharpe_ratio)

    def max_drawdown(df_prices, weights):
        """
    This function calculates the Max Drawdown of a portfolio
    
    :param df_prices dataframe of Adjusted close portfolio data
    :type pd.DataFrame
    :param weights array of weights portfolio allocation
    :type np.array
    """
        returns = df_prices.pct_change()
        returns.fillna(0, inplace=True)
        returns = (1 + returns).cumprod()
        returns = pd.Series((returns * weights).sum(axis=1), name="Portfolio")
        peak = returns.expanding(min_periods=1).max()
        dd = (returns / peak) - 1
        drawdown = dd.min()

        return display(drawdown)
