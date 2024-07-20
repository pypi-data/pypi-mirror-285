## TECHNICAL ANALISYS INDICATORS: ta_indicators

# Description:
"""
ta_indicators is a powerful and user-friendly Python library designed by the team of Trading com Dados Organization.
With ta_indicators, you can effortlessly calculate and visualize popular technical indicators, which are crucial for analyzing price trends, momentum,
volatility, and other key aspects of stock market behavior. The library includes a comprehensive collection of indicators, ranging from simple moving averages
to complex oscillators, allowing you to choose the ones that suit your analysis requirements.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date, time

## 1. TREND INDICATORS


class Trend:
    def sma(data_series: pd.core.series.Series, window: int, fill_na: bool = False):
        """
        Calculate Simple moving average (SMA) values.
        SMA is the arithmetic average of an data series over a specified number of periods,
        where all data points are equally weighted.

        :param data_series: a pandas series (usually stocks close price column of a OHLC dataframe)
        :type: pd.series
        :param window: n period (include actual period in the window)
        :type: int
        :param fill_na: if True, fill NaN values of the first n-1 period considering a lower window. Default is False
        :ype: bool

        :return: Series containing the SMA values
        :rtype: pd.series
        """
        if fill_na == False:
            sma = data_series.rolling(window).mean()
        else:
            sma = data_series.rolling(window, min_periods=1).mean()

        sma.name = "SMA"

        return sma

    def ema(data_series: pd.core.series.Series, window: int, fill_na: bool = False):
        """
        Calculate Exponential Moving Average (EMA) values.
        EMA is a weighted average that gives greater importance to the most recent points (newests)
        over a specified number of periods. The multiplier (alpha) used in the formula is 2/(window+1).

        :param data_series: a pandas series (usually stocks close price column of a OHLC dataframe)
        :type: pd.series
        :param window: n period (include actual period in the window)
        :type: int
        :param fill_na: if True, fill NaN values of the first n-1 period considering a lower window. Default is False
        :type: bool

        :return: Series containing the EMA values
        :rtype: pd.series
        """

        if fill_na == False:
            ema = data_series.ewm(span=window, adjust=False, min_periods=window).mean()
        else:
            ema = data_series.ewm(span=window, adjust=False, min_periods=1).mean()
        ema.name = "EMA"

        return ema

    def wma(data_series: pd.core.series.Series, window: int):
        """
        Calculate Weighted Moving Average (WMA) values.
        WMA is a weighted average that gives greater importance to most recent points. Different
        from exponencial moving average (EMA), each data point is assigned a multiplier, with the largest multiplier assigned
        to the newest data point and descending in order thereafter. The last point (newest) is multiplied by the
        window value, the second point by window - 1, the third by window - 2, and so on.

        :param data_series: a pandas series (usually stocks close price column of a OHLC dataframe)
        :type: pd.series
        :param window: the time period for calculating the ADX, +DI and -DI
        :type: int

        :return (pd.core.series.Series): Series containing the WMA values
        """

        wma = np.repeat(np.nan, window - 1).tolist()
        for i in range(window - 1, len(data_series)):
            weights = np.arange(1, window + 1, 1)
            wma.append(
                np.average(data_series.iloc[(i - window + 1) : i + 1], weights=weights)
            )
        wma = pd.Series(wma, index=data_series.index)
        wma.name = "WMA"

        return pd.Series(wma, index=data_series.index)

    def welles_wilder_avg(
        data_series: pd.core.series.Series, window: int, fill_na=False
    ):
        """
        Calculate Welles Wilder average values.
        The Welles Wilder average is similar to the exponential moving average ebut with a difference in how much weight it
        assigns to the most recent value. In the welles_wilder_avg function, the weight (alpha) is calculated as 1/window,
        whereas in the EMA, it is traditionally calculated as 2/(window+1).

        :param data_series: usually stocks close price column of a OHLC dataframe
        :type: pd.series
        :param window: n period (include actual period in the window)
        :type: int
        :param fill_na: if True, fill NaN values of the first n-1 period considering a lower window. Default is False
        :type: bool

        :return: Series containing the Welles Wilder average values
        :rtype: pd.series
        """

        if fill_na == False:
            welles_wilder_avg = data_series.ewm(
                alpha=1 / window, min_periods=window
            ).mean()
        else:
            welles_wilder_avg = data_series.ewm(alpha=1 / window, min_periods=1).mean()

        welles_wilder_avg.name = "Welles_Wilder_Avg"

        return welles_wilder_avg

    def macd(
        data_series: pd.Series,
        window_fast: int = 12,
        window_slow: int = 26,
        window_signal: int = 9,
    ):
        """
        Calculate Moving Average Convergence Divergence (MACD)indicator values.

        The MACD indicator is a trend-following indicator that helps identify potential buy and sell signals in
        financial markets by evaluating the relationship between two moving averages of prices: the slow moving average and
        the fast moving average.

        :param data_series: usually stocks close price column of a OHLC dataframe
        :type: pd.series
        :param window_fast: The time period for the fast moving average. Default is 12
        :type: int
        :param window_slow: The time period for the slow moving average. Default is 26
        :type: int
        :param window_signal: for the signal line moving average. Default is 9
        :type: int
        :return: A tuple containing three pd.core.series.Series:
                         1) macd_line: The MACD line values
                         2) macd_signal: The signal line values
                         3) macd_hist: The MACD histogram values
        :rtype: tuple

        """

        ema_fast = data_series.ewm(
            span=window_fast, adjust=False, min_periods=window_fast
        ).mean()
        ema_slow = data_series.ewm(
            span=window_slow, adjust=False, min_periods=window_slow
        ).mean()

        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(
            span=window_signal, adjust=False, min_periods=window_signal
        ).mean()
        macd_hist = macd_line - macd_signal

        macd_line.name = "macd_line"
        macd_signal.name = "macd_signal"
        macd_hist.name = "macd_hist"

        return (macd_line, macd_signal, macd_hist)

    def adx(df: pd.DataFrame, window: int = 14):
        """
        Calculate Average Directional Index (ADX) values.

        The Average Directional Index (ADX) is a technical indicator used to measure the strength of a trend in
        financial markets. It provides insights into the presence and magnitude of a trend, regardless of its direction.

        The ADX is calculated based on the price movement of an asset over a specific period. It involves several steps,
        including calculating the True Range (TR), which measures the volatility of the price, and the Directional Movement (DM),
        which quantifies the upward and downward price movement. From the smoothed DM values, the Positive Directional Index (+DI)
        and Negative Directional Index (-DI) are derived. These values indicate the upward and downward movement, respectively,
        and help assess the strength of the trend.

        The ADX is then calculated as the average of the Directional Movement Index (DX), which measures the strength of the trend
        based on the absolute difference between +DI and -DI, divided by the sum of +DI and -DI. The ADX is typically plotted as a
        single line, ranging from 0 to 100.

        :param df: a dataframe containing open, high, low, close (OHLC) data
        :type: pd.DataFrame
        :param window: the time period for calculating the ADX, +DI and -DI. Default is 14
        :type: int
        :return: A tuple containing three pd.core.series.Series:
                         1) adx_smooth: Average Directional Index (ADX) as a Wilder's smoothed average of Directional Movement
                         Index (DX) over the specified window
                         2) plus_di: Positive Directional Index (+DI) based on the Wilder's smoothed Directional Movement (DM) values
                         3) minus_di: Negative Directional Index (-DI) based on the Wilder's smoothed Directional Movement (DM) values
        :rtype: tuple
        """

        high_low = df.high - df.low
        high_prev_close = np.abs(df.high - df.close.shift(1))
        low_prev_close = np.abs(df.low - df.close.shift(1))
        ranges = pd.concat([high_low, high_prev_close, low_prev_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.ewm(alpha=1 / window, min_periods=window).mean()

        plus_dm = df.high - df.high.shift(1)
        minus_dm = df.low - df.low.shift(1)
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        plus_di = 100 * (plus_dm.ewm(alpha=1 / window).mean() / atr)
        minus_di = abs(100 * (minus_dm.ewm(alpha=1 / window).mean() / atr))

        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (window - 1)) + dx) / window
        adx_smooth = adx.ewm(alpha=1 / window).mean()

        adx_smooth.name = "adx_smooth"
        plus_di.name = "plus_di"
        minus_di.name = "minus_di"

        return (adx_smooth, plus_di, minus_di)


## 2. VOLATILITY INDICATORS


class Volatility:
    def bollinger_bands(data_series: pd.Series, window: int = 20, window_std: int = 2):
        """
        Calculate Bollinger Bands (BBolfor a given data series.

        Bollinger Bands are a technical analysis tool used to identify potential
        overbought or oversold conditions in financial markets. The bands consist of three
        lines: the middle band (typically a Simple Moving Average), and an upper and lower
        band that are plotted a specified number of standard deviations away from the middle
        band. Additionally, the Bollinger Channel Band Width is provided, which represents
        the distance between the upper and lower bands.

        :param data_series: usually stocks close price column of a OHLC dataframe
        :type: pd.series
        :param window: the time period for calculating the three bands. Default is 20
        :type: int
        :param window_std: the number of standard deviations to be plotted from the moving average. Default is 2
        :type: int
        :return: A tuple containing four pd.core.series.Series:
                         1) boll_higher: the upper Bollinger Band values
                         2) boll_middle: the middle (moving average) values
                         3) boll_lower: the lower Bollinger Band values
                         4) boll_wband: the width (upper minus lower) of Bollinger Band values
        :rtype: tuple

        """
        boll_middle = data_series.rolling(window).mean()
        boll_higher = boll_middle + data_series.rolling(window).std(ddof=0) * window_std
        boll_lower = boll_middle - data_series.rolling(window).std(ddof=0) * window_std
        boll_wband = (boll_higher - boll_lower) / boll_middle * 100

        boll_higher.name = "boll_higher"
        boll_middle.name = "boll_middle"
        boll_lower.name = "boll_lower"
        boll_wband.name = "boll_wband"

        return (boll_higher, boll_lower, boll_middle, boll_wband)

    def true_range(df: pd.DataFrame):
        """
        Calculate True Range (TR) values.

        The True Range (TR) is a technical indicator used to measure the volatility of an asset.
        It provides insights into the range of price movement, regardless of the direction of
        the price change, during a given period.

        :param df: a dataframe containing open, high, low, close (OHLC) data
        :type: pd.DataFrame
        :param window: the time period for calculating the TR values
        :type: int
        :return: Series containing the TR values
        :rtype: pd.series
        """

        high_low = df.high - df.low
        high_prev_close = np.abs(df.high - df.close.shift(1))
        low_prev_close = np.abs(df.low - df.close.shift(1))
        ranges = pd.concat([high_low, high_prev_close, low_prev_close], axis=1)
        true_range = np.max(ranges, axis=1)

        true_range.name = "true_range"

        return true_range

    def average_true_range(df: pd.DataFrame, window: int = 14):
        """
        Calculate Average True Range (ATR) values.

        The Average True Range (ATR) is a technical indicator used to measure the volatility of an asset.
        It provides insights into the average range of price movement, regardless of the direction, during a given period.

        :param df: a dataframe containing open, high, low, close (OHLC) data
        :type: pd.DataFrame
        :param window: the time period for calculating the TR values
        :type: int
        :return: Series containing the TR values
        :rtype: pd.series
        """

        high_low = df.high - df.low
        high_prev_close = np.abs(df.high - df.close.shift(1))
        low_prev_close = np.abs(df.low - df.close.shift(1))
        ranges = pd.concat([high_low, high_prev_close, low_prev_close], axis=1)
        true_range = np.max(ranges, axis=1)

        atr = true_range.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
        atr.name = "atr"

        return atr

    def stop_atr(df: pd.DataFrame, window: int = 14, multiplier: int = 2):
        """
        Calculates the Stop ATR (Average True Range) indicator for the given data.

        The Stop ATR indicator is a volatility-based trailing stop indicator that adjusts the stop price based on the
        Average True Range (ATR) of the asset. It is commonly used in trend-following trading strategies to set dynamic
        stop-loss levels that adapt to market volatility.

        :param df: a dataframe containing open, high, low, close (OHLC) data
        :type: pd.DataFrame
        :param window: the time period for calculating the ATR values. Default is 14
        :type: int
        :param multiplier: the multiplier value to determine the distance of the stop from the entry price. Default is 2
        :type: int
        :return: Series containing the TR values
        :rtype: pd.series

        """
        high_low = df.high - df.low
        high_prev_close = np.abs(df.high - df.close.shift(1))
        low_prev_close = np.abs(df.low - df.close.shift(1))
        ranges = pd.concat([high_low, high_prev_close, low_prev_close], axis=1)
        true_range = np.max(ranges, axis=1)

        df["atr"] = true_range.ewm(
            alpha=1 / window, adjust=False, min_periods=window
        ).mean()
        df["stop_atr_upper"] = np.NaN
        df["stop_atr_lower"] = np.NaN
        df["stop_atr"] = np.NaN
        df["position_atr"] = np.NaN

        df["stop_atr_upper"].iloc[window] = (
            df.open.iloc[window] + multiplier * df["atr"].shift(1).iloc[window]
        )
        df["stop_atr_lower"].iloc[window] = (
            df.open.iloc[window] - multiplier * df["atr"].shift(1).iloc[window]
        )
        df["stop_atr"].iloc[window] = df["stop_atr_lower"].iloc[window]
        df["position_atr"].iloc[window] = "lo"

        for row in range(window + 1, len(df)):
            df["stop_atr_upper"].iloc[row] = (
                df.open.iloc[row] + multiplier * df["atr"].shift(1).iloc[row]
            )
            df["stop_atr_lower"].iloc[row] = (
                df.open.iloc[row] - multiplier * df["atr"].shift(1).iloc[row]
            )

            if (df["position_atr"].iloc[row - 1] == "lo") and (
                df.close.iloc[row] > df["stop_atr"].iloc[row - 1]
            ):
                df["stop_atr"].iloc[row] = max(
                    df.stop_atr_lower.iloc[row], df["stop_atr"].iloc[row - 1]
                )
                df["position_atr"].iloc[row] = "lo"

            if (df["position_atr"].iloc[row - 1] == "lo") and (
                df.close.iloc[row] < df["stop_atr"].iloc[row - 1]
            ):
                df["stop_atr"].iloc[row] = df["stop_atr"].iloc[row - 1]
                df["position_atr"].iloc[row] = "lo_hi"

            if df["position_atr"].iloc[row - 1] == "lo_hi":
                df["stop_atr"].iloc[row] = df["stop_atr_upper"].iloc[row]
                if df.close.iloc[row] < df.stop_atr.iloc[row]:
                    df["position_atr"].iloc[row] = "hi"
                else:
                    df["position_atr"].iloc[row] = "hi_lo"

            if (df["position_atr"].iloc[row - 1] == "hi") and (
                df.close.iloc[row] < df["stop_atr"].iloc[row - 1]
            ):
                df["stop_atr"].iloc[row] = min(
                    df.stop_atr_upper.iloc[row], df["stop_atr"].iloc[row - 1]
                )
                df["position_atr"].iloc[row] = "hi"

            if (df["position_atr"].iloc[row - 1] == "hi") and (
                df.close.iloc[row] > df["stop_atr"].iloc[row - 1]
            ):
                df["stop_atr"].iloc[row] = df["stop_atr"].iloc[row - 1]
                df["position_atr"].iloc[row] = "hi_lo"

            if df["position_atr"].iloc[row - 1] == "hi_lo":
                df["stop_atr"].iloc[row] = df["stop_atr_lower"].iloc[row]
                if df.close.iloc[row] > df.stop_atr.iloc[row]:
                    df["position_atr"].iloc[row] = "lo"
                else:
                    df["position_atr"].iloc[row] = "lo_hi"

        stop_atr = df["stop_atr"]

        return stop_atr


#####------------------------------------------------
## 3. MOMENTUM INDICATORS


class Momentum:
    def rsi(data_series: pd.Series, window: int = 14):
        """
        Calculate Relative Strength Index (RSI) values.

        The Relative Strength Index (RSI) is a popular technical indicator used to measure the
        strength and speed of price movements. It helps identify potential overbought and
        oversold conditions in the market.

        :param data_series: usually stocks close price column of a OHLC dataframe
        :type: pd.Series
        :window_fast: The time period for calculating the RSI. Default is 14
        :type: int
        :return: Series containing the RSI values
        :rtype: pd.Series
        """

        close_diff = data_series.diff()
        up_values = close_diff.clip(lower=0)
        down_values = close_diff.clip(upper=0) * (-1)
        up_ewm = up_values.ewm(alpha=1 / window, min_periods=window).mean()
        down_ewm = down_values.ewm(alpha=1 / window, min_periods=window).mean()

        rs_ewm = up_ewm / down_ewm
        rsi = 100 - (100 / (1 + rs_ewm))

        rsi.name = "rsi"

        return rsi

    def stochastic_oscillator(
        df: pd.DataFrame, window: int = 14, smooth_window: int = 3
    ):
        """
        Calculate Stochastic Oscillator values.

        The Stochastic Oscillator is a popular technical indicator used to measure the
        momentum of price movements. It helps identify potential overbought and oversold
        conditions in the market.

        Percent K line (%K) is the ratio of the difference between the closing price and the lowest low price
        to the difference between the highest high price and the lowest low price, multiplied by 100
        The percent D line (%D) represents the smoothed %K line achieved through a moving average calculation
        over the designated smoothing window.

        :param df: a dataframe containing open, high, low, close (OHLC) data
        :type: pd.DataFrame
        :window: The time period for calculating the %K line. Default is 14
        :type: int
        :smooth_window: The time period for smoothing the %K line to calculate the %D line. Default is 3
        :type: int
        :return: A tuple containing two pd.core.series.Series:
                         1) percent_K: %K line values, which were named stoch
                         2) percent_D: %D line values, which were named stoch_signal
        :rtype: tuple
        """

        highest_high = df.high.rolling(window).max()
        lowest_low = df.low.rolling(window).min()
        percent_K = (df.close - lowest_low) / (highest_high - lowest_low) * 100
        percent_D = percent_K.rolling(smooth_window).mean()

        percent_K.name = "stoch"
        percent_D.name = "stoch_signal"

        return (percent_K, percent_D)


#####------------------------------------------------
## 4. VOLUME INDICATORS


class Volume:
    def obv(df: pd.DataFrame):
        """
        Calculates the On-Balance Volume (OBV) indicator for the given data.

        The On-Balance Volume (OBV) is a technical analysis indicator that measures buying and selling
        pressure in the market by keeping track of cumulative volume based on price movements.
        It is used to confirm price trends and identify potential trend reversals.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :return: Series containing the OBV values
        :rtype: pd.Series
        """

        first_diff = df.open[0] - df.close[0]
        close_diff = df.close.diff().fillna(first_diff)
        close_sign = np.sign(close_diff)
        obv = close_sign * df.volume
        obv_cumsum = obv.cumsum()
        obv_cumsum.name = "obv"

        return obv_cumsum

    def vwap(df: pd.DataFrame, window: int = 14):
        """
        Calculates the Volume-Weighted Average Price (VWAP) indicator for the given data.

        The Volume-Weighted Average Price (VWAP) is a technical analysis indicator that calculates the average price of a
        security, taking into account both price and volume. It provides traders with insight into the average price at
        which an asset is being traded over a given period, weighted by the volume traded at each price level.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :window: The time period for calculating the VWAP values. Default is 14
        :type: int
        :return: Series containing the VWAP values
        :rtype: pd.Series
        """

        typical_price = (df.high + df.low + df.close) / 3
        typical_price_x_volume = typical_price * df.volume
        vwap = (
            typical_price_x_volume.rolling(window).sum()
            / df.volume.rolling(window).sum()
        )
        vwap.name = "vwap"
        return vwap

    def vwap_anchored(df: pd.DataFrame, start: datetime):
        """
        Calculates the Volume-Weighted Average Price (VWAP) indicator for the given data by setting the starting date.

        The Volume-Weighted Average Price (VWAP) is a technical analysis indicator that calculates the average price of a
        security, taking into account both price and volume. It provides traders with insight into the average price at
        which an asset is being traded over a given period, weighted by the volume traded at each price level.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :param start:  the first available date
        :type: datetime
        :return: Series containing the Anchored VWAP values
        :rtype: pd.Series
        """

        if start is None:
            df = df.iloc[0]
        else:
            df = df.loc[start:]

        typical_price = (df.high + df.low + df.close) / 3
        typical_price_x_volume = typical_price * df.volume
        vwap_anchored = typical_price_x_volume.cumsum() / df.volume.cumsum()
        vwap_anchored.name = "anchored_vwap"

        return vwap_anchored

    def vwap_daily(df: pd.DataFrame):
        """
        Calculates the Volume-Weighted Average Price (VWAP) indicator, resetting the calculation for each day based on the given data.

        The Volume-Weighted Average Price (VWAP) is a technical analysis indicator that calculates the average price of a
        security, taking into account both price and volume. It provides traders with insight into the average price at
        which an asset is being traded over a given period, weighted by the volume traded at each price level.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :return: Series containing the Daily VWAP values
        :rtype: pd.Series
        """

        typical_price = (df.high + df.low + df.close) / 3
        typical_price_x_volume = typical_price * df.volume
        vwap_daily = (
            typical_price_x_volume.groupby("date_col").cumsum()
            / df.volume.groupby("date_col").cumsum()
        )
        vwap_daily.name = "daily_vwap"

        return vwap_daily

    def vwap_weekly(df: pd.DataFrame):
        """
        Calculates the Volume-Weighted Average Price (VWAP) indicator, resetting the calculation for each week based on the given data.

        The Volume-Weighted Average Price (VWAP) is a technical analysis indicator that calculates the average price of a
        security, taking into account both price and volume. It provides traders with insight into the average price at
        which an asset is being traded over a given period, weighted by the volume traded at each price level.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :return: Series containing the weekly VWAP values
        :rtype: pd.Series
        """

        df["week_of_year"] = (
            df.date_col.dt.isocalendar().week.astype("str")
            + "_"
            + df.date_col.dt.isocalendar().year.astype("str")
        )
        df["typical_price"] = (df.high + df.low + df.close) / 3
        df["typical_price_x_volume"] = df.typical_price * df.volume
        vwap_weekly = (
            df.groupby("week_of_year").typical_price_x_volume.cumsum()
            / df.groupby("week_of_year").volume.cumsum()
        )
        df = df.drop(
            ["week_of_year", "typical_price", "typical_price_x_volume"], axis=1
        )
        vwap_weekly.name = "weekly_vwap"
        return vwap_weekly

    def vwap_monthly(df):
        """
        Calculates the Volume-Weighted Average Price (VWAP) indicator, resetting the calculation for each month based on the given data.

        The Volume-Weighted Average Price (VWAP) is a technical analysis indicator that calculates the average price of a
        security, taking into account both price and volume. It provides traders with insight into the average price at
        which an asset is being traded over a given period, weighted by the volume traded at each price level.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :return: Series containing the monthly VWAP values
        :rtype: pd.Series
        """

        df["month_of_year"] = (
            df.date_col.dt.month.astype("str") + "_" + df.date_col.dt.year.astype("str")
        )
        df["typical_price"] = (df.high + df.low + df.close) / 3
        df["typical_price_x_volume"] = df.typical_price * df.volume
        vwap_monthly = (
            df.groupby("month_of_year").typical_price_x_volume.cumsum()
            / df.groupby("month_of_year").volume.cumsum()
        )
        df = df.drop(
            ["month_of_year", "typical_price", "typical_price_x_volume"], axis=1
        )
        vwap_monthly.name = "monthly_vwap"
        return vwap_monthly

    def accumulation_distribution_index(df):
        """
        Calculates the Accumulation/Distribution Index (ADI) indicator for the given data.

        The Accumulation/Distribution Index (ADI) is a volume-based indicator that measures the cumulative flow of money
        into or out of a security. It takes into account both price and volume to determine whether buying or selling
        pressure is dominating the market.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :return: Series containing the monthly ADI values
        :rtype: pd.Series
        """

        money_flow_multiplier = ((df.close - df.low) - (df.high - df.close)) / (
            df.high - df.low
        )
        money_flow_volume = money_flow_multiplier * df.volume
        acc_dist = money_flow_volume.cumsum()
        acc_dist.name = "acc_dist_index"

        return acc_dist

    def money_flow_index(df, window=14):
        """
        Calculates the Money Flow Index (MFI) indicator for the given data and period.

        The Money Flow Index (MFI) is a momentum oscillator that measures the strength and direction of money flow into
        or out of a security, but considering volume. The positive and negative money flow ratio is subsequently utilized
        in an RSI formula to generate an oscillator that fluctuates between 0 and 100. It uses both price and volume
        to determine overbought and oversold conditions in the market and potential trend reversals.

        :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
        :type: pd.DataFrame
        :window: The time period for calculating the MFI values. Default is 14
        :type: int
        :return: Series containing the MFI values
        :rtype: pd.Series
        """

        typical_price = (df.high + df.low + df.close) / 3
        raw_money_flow = typical_price * df.volume
        typical_price_diff = typical_price.diff()
        typical_price_sign = np.sign(typical_price_diff)
        raw_money_flow_signed = raw_money_flow * typical_price_sign
        money_flow_ratio = raw_money_flow_signed.clip(lower=0).rolling(
            window
        ).sum() / abs(raw_money_flow_signed.clip(upper=0).rolling(window).sum())
        mfi = 100 - (100 / (1 + money_flow_ratio))
        mfi.name = "mfi"

        return mfi


def volume_profile(df, range_price_levels):
    """
    Calculates the amount of volume transacted around given price levels.

    :param df: a dataframe containing open, high, low, close, volume (OHLCV) data
    :type: pd.DataFrame
    :param range_price_levels: the price range corresponding to each bin to divide the volume data into
    :type: float
    :return: the sum of volume transacted for each bin of price range. Index refers to the upper threshold of price range
    :rtype: pd.Series
    """

    volume_profile = (
        df["volume"]
        .groupby(
            df["close"].apply(
                lambda x: range_price_levels * round(x / range_price_levels, 0)
            )
        )
        .sum()
    )
    volume_profile.name = "volume_profile"

    return volume_profile


#####------------------------------------------------
## 5. OTHER INDICATORS


def zigzag_indicator(df, upper_bound, lower_bound):
    """
    Computes the ZigZag indicator (top and bottom detector) based on the given OHLC data series and
    predefined upper and lower bounds of price movements. The bounds must be expressed as rates. For example, price movements
    of 10% upper or lower must be expressed as 0.1 and -0.1.

    :param upper_bound: The minimum rate change required to form a peak (top detection)
    :type: float
    :param lower_bound: The minimum rate required to form a valley (bottom detection). Must be a negative value
    :type: float
    :return: a dataframe with index setted as datetime and the columns:
                                            1) pivots (classification into top or bottom)
                                            2) price (high for top and low for bottom)
                                            3) pivot_date_validation (datetime when the pivot was confirmed)
    :rtype: pd.DataFrame
    """

    if lower_bound >= 0:
        raise ValueError("The down_thresh must be negative.")

    dict_zigzag = {
        "pivot": ["0"],
        "date": [df.index[0]],
        "price": [df.open.iloc[0]],
        "pivot_date_validation": [],
    }

    upper_bound = 1 + upper_bound
    lower_bound = 1 + lower_bound

    for i in range(1, len(df)):
        high_i = df.high.iloc[i]
        low_i = df.low.iloc[i]

        if (high_i / dict_zigzag["price"][-1] >= upper_bound) and (
            dict_zigzag["pivot"][-1] != "top"
        ):
            dict_zigzag["pivot"].append("top")
            dict_zigzag["date"].append(df.index[i])
            dict_zigzag["price"].append(high_i)
            dict_zigzag["pivot_date_validation"].append(df.index[i])

        if (low_i / dict_zigzag["price"][-1] <= lower_bound) and (
            dict_zigzag["pivot"][-1] != "bottom"
        ):
            dict_zigzag["pivot"].append("bottom")
            dict_zigzag["date"].append(df.index[i])
            dict_zigzag["price"].append(low_i)
            dict_zigzag["pivot_date_validation"].append(df.index[i])

        if high_i > dict_zigzag["price"][-1] and (dict_zigzag["pivot"][-1] == "top"):
            dict_zigzag["date"][-1] = df.index[i]
            dict_zigzag["price"][-1] = high_i

        if (low_i < dict_zigzag["price"][-1]) and (
            dict_zigzag["pivot"][-1] == "bottom"
        ):
            dict_zigzag["date"][-1] = df.index[i]
            dict_zigzag["price"][-1] = low_i

    if dict_zigzag["pivot"][1] == "top":
        date_range = pd.date_range(
            start=dict_zigzag["date"][0], end=dict_zigzag["date"][1]
        )
        df_initial_pivot = df[df.index.isin(date_range)]
        df_initial_pivot = df_initial_pivot.sort_values("low")
        dict_zigzag["pivot"][0] = "bottom"
        dict_zigzag["date"][0] = df_initial_pivot.index[0]
        dict_zigzag["price"][0] = df_initial_pivot.low.iloc[0]
        dict_zigzag["pivot_date_validation"][0] = np.NaN

    elif dict_zigzag["pivot"][1] == "bottom":
        date_range = pd.date_range(
            start=dict_zigzag["date"][0], end=dict_zigzag["date"][1]
        )
        df_initial_pivot = df[df.index.isin(date_range)]
        df_initial_pivot = df_initial_pivot.sort_values("high", ascending=False)
        dict_zigzag["pivot"][0] = "top"
        dict_zigzag["date"][0] = df_initial_pivot.index[0]
        dict_zigzag["price"][0] = df_initial_pivot.low.iloc[0]
        dict_zigzag["pivot_date_validation"][0] = np.NaN

    zigzag = pd.DataFrame.from_dict(dict_zigzag, orient="index").transpose()
    zigzag = zigzag.set_index("date", drop="True")

    return zigzag


def candles_count(df: pd.DataFrame, intraday_count: bool = True):
    """
    Calculate a candle counting within the daily chart in order to make it easy to
    chat with other analyst to which candle bar you are referencing toCounts the number of candles within based on a given dataset.

    :param df: Dataframe that can be used for the candle counting
    :type: pd.DataFrame
    :param intraday_count: The intraday indicator that is set to True as default
    :type: bool
    :return: the count of candles in pd.Series
    :rtype: pd.Series
    """

    if intraday_count == True:
        ls_count_candles = [1]
        for i in range(1, len(df)):
            current_date = df.index[i].date()
            previous_date = df.index[i - 1].date()

            if current_date != previous_date:
                ls_count_candles.append(1)

            else:
                ls_count_candles.append(ls_count_candles[-1] + 1)

    else:
        ls_count_candles = list(range(len(df)))

    candles_count = pd.Series(ls_count_candles, index=df.index)

    return candles_count
