import pandas as pd
import requests as req


def _run_request(
    data_type: str,
    request_type: str,
    ticker: str,
    date_begin: str,
    date_end: str,
    api_key: str,
    endpoint: str,
):
    try:

        header = {"X-API-Key": api_key}

        def _ckeck_data_type(data_type):

            report_list = [
                "historical_data_bpa",
                "historical_data_bpp",
                "historical_data_dre",
                "historical_data_dfc",
            ]

            if data_type == "stock" and request_type not in report_list:
                params = {
                    "ticker": ticker,
                    "dataInicio": date_begin,
                    "dataFim": date_end,
                }

            elif data_type == "index":
                params = {
                    "indice": ticker,
                    "dataInicio": date_begin,
                    "dataFim": date_end,
                }

            elif data_type == "treasury":
                params = {"tamanho": "1000"}

            elif data_type == "treasury_historical":
                params = {
                    "tamanho": "1000",
                    "dataInicio": date_begin,
                    "dataFim": date_end,
                }

            return params

        params = _ckeck_data_type(data_type)
        res = req.get(endpoint, headers=header, params=params).json()

        return res

    except:
        print(
            "An error occured during the process of gathering data, please check the ticker and dates used and also remember to use a valid api key"
        )


def _run_request_report(
    data_type: str,
    request_type: str,
    ticker: str,
    date_begin: str,
    trimester: str,
    api_key: str,
    endpoint: str,
):
    try:

        header = {"X-API-Key": api_key}

        def _ckeck_data_type(data_type):

            report_list = [
                "historical_data_bpa",
                "historical_data_bpp",
                "historical_data_dre",
                "historical_data_dfc",
            ]

            if data_type == "stock" and request_type in report_list:
                params = {
                    "ticker": ticker,
                    "ano": date_begin[0:4],
                    "trimestre": trimester,
                }

            return params

        params = _ckeck_data_type(data_type)
        res = req.get(endpoint, headers=header, params=params).json()

        return res

    except:
        print(
            "An error occured during the process of gathering data, please check the ticker and dates used and also remember to use a valid api key"
        )


def _run_request_indicators(
    data_type: str,
    request_type: str,
    ticker: str,
    indicator: str,
    date_begin: str,
    date_end: str,
    api_key: str,
    endpoint: str,
):
    try:

        header = {"X-API-Key": api_key}

        def _ckeck_data_type(data_type):

            if data_type == "stock" and request_type == "historical_data_indicator":
                params = {
                    "ticker": ticker,
                    "indicador": indicator,
                    "dataInicio": date_begin,
                    "dataFim": date_end,
                }

            return params

        params = _ckeck_data_type(data_type)
        res = req.get(endpoint, headers=header, params=params).json()

        return res

    except:
        print(
            "An error occured during the process of gathering data, please check the ticker and dates used and also remember to use a valid api key"
        )

def _run_request_indicators_hist(
    data_type: str,
    request_type: str,
    ticker: str,
    indicator: str,
    api_key: str,
    endpoint: str,
):
    try:

        header = {"X-API-Key": api_key}

        def _ckeck_data_type(data_type):

            if data_type == "stock" and request_type == "historical_data_indicator_full":
                params = {
                    "ticker": ticker,
                    "indicador": indicator
                }

            return params

        params = _ckeck_data_type(data_type)
        res = req.get(endpoint, headers=header, params=params).json()

        return res

    except:
        print(
            "An error occured during the process of gathering data, please check the ticker and dates used and also remember to use a valid api key"
        )

def _run_request_accounting(
    data_type: str,
    request_type: str,
    ticker: str,
    item: str,
    date_begin: str,
    date_end: str,
    api_key: str,
    endpoint: str,
):
    try:

        header = {"X-API-Key": api_key}

        def _ckeck_data_type(data_type):

            if data_type == "stock" and request_type == "historical_data_accounting":
                params = {
                    "ticker": ticker,
                    "item": item,
                    "dataInicio": date_begin,
                    "dataFim": date_end,
                }

            return params

        params = _ckeck_data_type(data_type)
        res = req.get(endpoint, headers=header, params=params).json()

        return res

    except:
        print(
            "An error occured during the process of gathering data, please check the ticker and dates used and also remember to use a valid api key"
        )


def _request_type_validation(data_type, request_type, ticker):

    try:
        url_base = "https://api.fintz.com.br"

        if data_type == "stock":

            def _check_request_type_stock(request_type):

                if request_type == "historical_data_stock":
                    endpoint = url_base + "/bolsa/b3/avista/cotacoes/historico"

                elif request_type == "historical_data_earnings":
                    endpoint = url_base + "/bolsa/b3/avista/proventos"

                elif request_type == "historical_data_bpa":
                    endpoint = url_base + "/bolsa/b3/demonstracoes/bpa"

                elif request_type == "historical_data_bpp":
                    endpoint = url_base + "/bolsa/b3/demonstracoes/bpp"

                elif request_type == "historical_data_dre":
                    endpoint = url_base + "/bolsa/b3/demonstracoes/dre"

                elif request_type == "historical_data_dfc":
                    endpoint = url_base + "/bolsa/b3/demonstracoes/dfc"

                elif request_type == "historical_data_indicator":
                    endpoint = url_base + "/bolsa/b3/tm/indicadores"

                elif request_type == "historical_data_indicator_full":
                    endpoint = url_base + "/bolsa/b3/avista/indicadores/historico"

                elif request_type == "historical_data_accounting":
                    endpoint = url_base + "/bolsa/b3/tm/demonstracoes"

                return endpoint

            endpoint = _check_request_type_stock(request_type)

        elif data_type == "index":

            def _check_request_type_index(request_type):

                if request_type == "historical_data_index":
                    endpoint = url_base + "/indices/historico"

                return endpoint

            endpoint = _check_request_type_index(request_type)

        elif data_type == "treasury":

            def _check_request_type_treasury(request_type, ticker):

                if request_type == "treasury_info":
                    endpoint = (
                        url_base
                        + "/titulos-publicos/tesouro/"
                        + ticker
                        + "/informacoes"
                    )

                elif request_type == "treasury_listing":
                    endpoint = url_base + "/titulos-publicos/tesouro"

                elif request_type == "treasury_coupons":
                    endpoint = (
                        url_base + "/titulos-publicos/tesouro/" + ticker + "/cupons"
                    )

                elif request_type == "treasury_historical":
                    endpoint = (
                        url_base
                        + "/titulos-publicos/tesouro/"
                        + ticker
                        + "/precos/historico"
                    )

                elif request_type == "treasury_current_price":
                    endpoint = (
                        url_base
                        + "/titulos-publicos/tesouro/"
                        + ticker
                        + "/precos/atual"
                    )

                return endpoint

            endpoint = _check_request_type_treasury(request_type, ticker)

        return endpoint

    except:
        return print(
            "Input request_type option not found, take a look at the documentation."
        )


def _transform_to_dataframe(res, request_type):
    try:
        if request_type == "historical_data_indicator":
            df = pd.DataFrame.from_dict(res)
        
        elif request_type == "historical_data_indicator_full":
            df = pd.json_normalize(res)

        elif request_type == "historical_data_index":
            df = pd.DataFrame(res)

        elif request_type != "treasury_historical":
            df = pd.json_normalize(res)

        else:
            df = pd.DataFrame.from_dict(res["dados"])

        return df

    except:
        print("An error occured converting data from JSON to pandas DataFrame.")


def get_data(
    data_type: str,
    request_type: str,
    ticker: str,
    date_begin: str,
    date_end: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for the chosen ticker.

    Use stock or treasury for data_type.
    
    It can be found in stock module the following methods:
    historical_data_stock       -> Historical prices from the stock
    historical_data_earnings    -> earnings from that company

    For treasury results:
    treasury_listing            -> list of trasuries available
    treasury_coupons            -> list of information for the most recent date
    treasury_historical         -> historical of prices and taxes for that bond 
    treasury_current_price      -> current price of the bond

    :param data_type: It can be chosen beetween stock and treasury
    :type: str
    :param request_type: It is the type of data you want to bring
    :type: str
    :param ticker: ticker you want to search for information
    :type: list
    :param date_begin: start date you want to search for information
    :type: str
    :param date_end: end date you want to search for information
    :type: str
    :param api_key: API_KEY used to connect to the endpoint service
    :type: str
    :return: DataFrame that contains the results for the ticker in the date range requested
    :rtype: DataFrame
    """

    endpoint = _request_type_validation(data_type, request_type, ticker)
    res = _run_request(
        data_type, request_type, ticker, date_begin, date_end, api_key, endpoint
    )
    df = _transform_to_dataframe(res, request_type)

    return df


def get_data_tickers(
    data_type: str,
    request_type: str,
    tickers: list,
    date_begin: str,
    date_end: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for a list of tickers. Find more details in the get_data method.

    :param data_type: It can be chosen beetween stock and treasury
    :type: str
    :param request_type: It is the type of data you want to bring
    :type: str
    :param tickers: list of tickers you want to search for information
    :type: list
    :param date_begin: start date you want to search for information
    :type: str
    :param date_end: end date you want to search for information
    type: str
    :param api_key: API_KEY used to connect to the endpoint service
    :type: str
    :return: DataFrame that contains the results for all tickers in the date range requested
    :rtype: DataFrame
    """

    df = pd.DataFrame()

    for i in tickers:
        temp = get_data(data_type, request_type, i, date_begin, date_end, api_key)
        df = pd.concat([df, temp], ignore_index=True)

    return df


def get_data_report(
    data_type: str,
    request_type: str,
    ticker: str,
    date_begin: str,
    trimester: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for the chosen ticker.

    Use stock or treasury for data_type.
    
    In order to use reports, the API can bring the following types:
    historical_data_bpa         -> bpa report
    historical_data_bpp         -> bpp report
    historical_data_dre         -> dre report
    historical_data_dfc         -> dfc report

    :param data_type: It can be chosen beetween stock and treasury
    :type: str
    :param request_type: It is the type of data you want to bring
    :type: str
    :param ticker: ticker you want to search for information
    :type: list
    :param date_begin: start date you want to search for information
    :type: str
    :param trimester: The number of which trimester you want to retrieve
    :type: str
    :param api_key: API_KEY used to connect to the endpoint service
    :type: str
    :return: DataFrame that contains the results for the ticker in the date range requested
    :rtype: DataFrame
    """

    endpoint = _request_type_validation(data_type, request_type, ticker)
    res = _run_request_report(
        data_type, request_type, ticker, date_begin, trimester, api_key, endpoint
    )
    df = _transform_to_dataframe(res, request_type)

    return df


def get_data_report_tickers(
    data_type: str,
    request_type: str,
    tickers: list,
    date_begin: str,
    trimester: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for a list of tickers. Find more details in the get_data method.

    :param data_type: It can be chosen beetween stock and treasury
    :type: str
    :param request_type: It is the type of data you want to bring
    :type: str
    :param tickers: list of tickers you want to search for information
    :type: list
    :param date_begin: start date you want to search for information
    :type: str
    :param trimester: The number of which trimester you want to retrieve
    type: str
    :param api_key: API_KEY used to connect to the endpoint service
    :type: str
    :return: DataFrame that contains the results for all tickers in the date range requested
    :rtype: DataFrame
    """

    df = pd.DataFrame()

    for i in tickers:
        temp = get_data_report(
            data_type, request_type, i, date_begin, trimester, api_key
        )
        df = pd.concat([df, temp], ignore_index=True)

    return df


def get_data_indicator(
    data_type: str,
    request_type: str,
    ticker: str,
    indicator: str,
    date_begin: str,
    date_end: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for the chosen ticker.

    """

    endpoint = _request_type_validation(data_type, request_type, ticker)
    res = _run_request_indicators(
        data_type,
        request_type,
        ticker,
        indicator,
        date_begin,
        date_end,
        api_key,
        endpoint,
    )
    df = _transform_to_dataframe(res, request_type)

    return df

def get_data_indicator_hist(
    data_type: str,
    request_type: str,
    ticker: str,
    indicator: str,
    api_key: str,
):

    """
    Get historical data for indicators from API using standard parameters for the chosen ticker.

    """

    endpoint = _request_type_validation(data_type, request_type, ticker)
    res = _run_request_indicators_hist(
        data_type,
        request_type,
        ticker,
        indicator,
        api_key,
        endpoint,
    )
    df = _transform_to_dataframe(res, request_type)

    return df


def get_data_accounting(
    data_type: str,
    request_type: str,
    ticker: str,
    item: str,
    date_begin: str,
    date_end: str,
    api_key: str,
):

    """
    Get data from API using standard parameters for the chosen ticker.

    """

    endpoint = _request_type_validation(data_type, request_type, ticker)
    res = _run_request_accounting(
        data_type, request_type, ticker, item, date_begin, date_end, api_key, endpoint
    )
    df = _transform_to_dataframe(res, request_type)

    return df
