import pandas as pd
import requests 
import zipfile  
import numpy as np
import urllib.request
from pathlib import Path
from datetime import datetime
import urllib3
import os
import wget


#path = 'https://raw.githubusercontent.com/victorncg/financas_quantitativas/main/Data%20Extraction/Stock%20Exchange/Index%20Composition/'
#file = 'backend_index.py'

# DEACTIVETED FOR FIXING BUGS - JULY 11
#with urllib.request.urlopen(path + file) as response:
#    py_content = response.read().decode('utf-8')

#exec(py_content)


def _return_index(index:str):

    conversion = {'ibov':'eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjEifQ==',
                 'ibra':'QlJB',
                 'ifix': 'eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJRklYIiwic2VnbWVudCI6IjEifQ==',
                  'idiv': 'RElW'}

    # Desabilitar avisos de verificação SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Configurar sessão para não verificar SSL
    session = requests.Session()
    session.verify = False
    
    # URLs
    url1 = 'https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/'
    url2 = conversion[index] 
    
    # Fazer a requisição
    response = session.get(url1 + url2)
    
    # Verificar o status da resposta
    if response.status_code == 200:
        dados = pd.DataFrame(response.json()["results"])
    else:
        print(f"A biblioteca está funcionando mas houve erro na requisição a partir da B3, código: {response.status_code}")

    return dados


def _parse_ibov():

    try:

        url = "https://raw.githubusercontent.com/victorncg/financas_quantitativas/main/IBOV.csv"
        df = pd.read_csv(
            url, encoding="latin-1", sep="delimiter", header=None, engine="python"
        )
        df = pd.DataFrame(df[0].str.split(";").tolist())

        return df

    except:

        print("An error occurred while parsing data from IBOV.")



def _standardize_ibov():

    try:
        df = _parse_ibov()
        df.columns = list(df.iloc[1])
        df = df[2:][["Código", "Ação", "Tipo", "Qtde. Teórica", "Part. (%)"]]
        df.reset_index(drop=True, inplace=True)

        return df
    except:

        print("An error occurred while manipulating data from IBOV.")



def _standardize_sp500():
    """
    This function fetches the updated composition of the S&P 500 index. 
    
    Parameters
    ----------
    
    """

    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = table[0]

    return df



def _adapt_index(
    index: object, assets: object = "all", mode: object = "df"
):
    """
    This function processes the data from the latest composition of either IBOV or S&P 500. 
    
    Parameters
    ----------
    index : choose the index to be returned, if IBOV or S&P 500
    ativos : you can pass a list with the desired tickets. Default = 'all'.
    mode: you can return either the whole dataframe from B3, or just the list containing the tickers which compose IBOV. Default = 'df'.
    
    """

    if index == "sp500":

        df = _standardize_sp500()

        if assets != "all":
            df = df[df["Symbol"].isin(assets)]

        if mode == "list":
            df = list(df.Symbol)

    else:

        df = _return_index(index)

        if assets != "all":
            df = df[df["cod"].isin(assets)]

        if mode == "list":
            df = list(df.cod)
    
    return df



def index_composition(
    index: object, assets: object = "all", mode: object = "df"
):
    """
    This function captures the latest composition of either IBOV or S&P 500. It is updated every 4 months.
    
    Parameters
    ----------
    index : choose the index to be returned, if IBOV or S&P 500
    ativos : you can pass a list with the desired tickets. Default = 'all'.
    mode: you can return either the whole dataframe from B3, or just the list containing the tickers which compose IBOV. Default = 'df'.
    
    """

    df = _adapt_index(index, assets, mode)

    return df

def download_ClassifSetorial(url_dataset):
    """
    Downloads and extracts a zip file from the provided URL.
    ------------------------------------------------------------------------
    Parameters:
    - url_dataset (str): URL pointing to the zip file to be downloaded.
    ------------------------------------------------------------------------
    Returns:
    - io.BytesIO: Bytes stream of the extracted file from the downloaded zip.
      named dataset. 
    """

    file = url_dataset.split('/')[-1]

    download = requests.get(url_dataset)
    with open(file, "wb") as dataset_B3:
        dataset_B3.write(download.content)
    arquivo_zip = zipfile.ZipFile(file)
    dataset = arquivo_zip.open(arquivo_zip.namelist()[0])
    return dataset


def B3Eng_DataProcessing(df):
    """
    Description:
    The function Processes and clean DataFrame containing B3 (Brazilian Stock Exchange) sectors data in english.
    --------------------------------------------------------------------------------------------------
    Parameters:
    - df (pandas.DataFrame): DataFrame containing B3 sectors data in english.
    -------------------------------------------------------------------------------------------------
    Returns:
    pandas.DataFrame: Processed DataFrame with renamed columns and cleaned data:
        - 'SECTORS': Economic sector.
        - 'SUBSECTORS': Subsector.
        - 'SEGMENTS': Segment.
        - 'NAME': Company name.
        - 'CODE': Ticker code.
        - 'SEGMENT B3': B3 listing segment such as 'ON', 'PN', 'UNIT' and 'DR'.    
    """
    
    df.rename(columns = {'LISTING': 'CODE', 'Unnamed: 4':'SEGMENT B3'}, inplace = True)
        
    df['NAME'] = df['SEGMENTS'].copy()
        
    df.dropna(subset = ['NAME'], inplace = True)
    indexNames = df[df['SECTORS'] == 'SECTORS'].index
    df.drop(indexNames, inplace=True)
        
    df['SEGMENTS'] = np.where(df['CODE'].isna(),df['NAME'],pd.NA )    
    df['SECTORS'] = df['SECTORS'].ffill()
    df['SUBSECTORS'] = df['SUBSECTORS'].ffill()
    df['SEGMENTS'] = df['SEGMENTS'].ffill()
    df.dropna(subset = ['CODE'], inplace = True)

    df.reset_index(drop=True, inplace=True)

    df = df[['SECTORS','SUBSECTORS','SEGMENTS','NAME','CODE','SEGMENT B3']]
    
    return df


def B3Pt_DataProcessing(df):
    """
    Description:
    Processes DataFrame containing B3 (Brazilian Stock Exchange) data in Portuguese.
    -------------------------------------------------------------------------------
    Parameters:
    - df (pandas.DataFrame): DataFrame containing B3 sectors data in portuguese.

    Returns:
    pandas.DataFrame: DataFrame : Processed DataFrame with renamed columns and cleaned data:
        - 'SETOR ECONÔMICO': Setor econômico.
        - 'SUBSETOR': Subsetor.
        - 'SEGMENTO': Nome ou código do segmento.
        - 'NOME NO PREGÃO': Nome da empresa.
        - 'CÓDIGO': Código da ação.
        - 'SEGMENTO B3': Segmento de listagem na B3.
    """
    
    df.rename(columns = {'LISTAGEM': 'CÓDIGO', 'Unnamed: 4':'SEGMENTO B3'}, inplace = True)
        
    df['NOME NO PREGÃO'] = df['SEGMENTO'].copy()
        
    df.dropna(subset = ['NOME NO PREGÃO'], inplace = True)
    indexNames = df[df['SETOR ECONÔMICO'] == 'SETOR ECONÔMICO'].index
    df.drop(indexNames, inplace=True)
        
    df['SEGMENTO'] = np.where(df['CÓDIGO'].isna(),df['NOME NO PREGÃO'],pd.NA )    
    df['SETOR ECONÔMICO'] = df['SETOR ECONÔMICO'].ffill()
    df['SUBSETOR'] = df['SUBSETOR'].ffill()
    df['SEGMENTO'] = df['SEGMENTO'].ffill()
    df.dropna(subset = ['CÓDIGO'], inplace = True)

    df.reset_index(drop=True, inplace=True)

    df = df[['SETOR ECONÔMICO','SUBSETOR','SEGMENTO','NOME NO PREGÃO','CÓDIGO','SEGMENTO B3']]
    
    return df

def request_nasdaq(url):
    headers = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Java-http-client/'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        return json_data

    else:
        print(f"Failed to retrieve data: {response.status_code}")


def get_sectors(stock_exchange: str, B3_language: str = None, symbols: list = None) -> pd.DataFrame:
    """
    Description: 
    It retrieves economic and activity sector classifications for companies listed 
    on NASDAQ, NYSE, AMEX, or the Brazilian stock exchange (B3).

    You can leave the 'symbols' parameter as None to return data for all companies, 
    or specify a list of specific symbols.

    ---------------------------------------------------------------------------------------
    Parameters:
    - stock_exchange (str): Code for the stock exchange ('NASDAQ', 'NYSE', 'AMEX', or 'B3').
    - B3_language (str, optional): Language option only for B3 data ('pt' for Portuguese, default is 'eng').
    - symbols (list, optional): List of ticker symbols (e.g., symbols = ['AAPL', 'AMD']) 
      of specific companies to retrieve sector data for. 
      
      Notice that: 
      - For Brazilian companies on B3, you can pass the symbol with or without 
        the ordinary/common stock number (e.g., ['PETR4', 'PETR3'] or ['PETR']).
    -----------------------------------------------------------------------------------------
    Returns:
    pandas.DataFrame: DataFrame containing the following columns based on the stock exchange:
        - For B3 (Brazilian stock exchange):
            - 'sector' (pt: 'SETOR ECONÔMICO'): Economic sector of the company.
            - 'subsectors (pt: 'SUBSETOR'): Subsector of the company.
            - 'segments' (pt:'SEGMENTO'): Industry of the company.
            - 'name'(pt: 'NOME NO PREGÃO'): Company name.
            - 'CODE'(pt: 'CÓDIGO'): Ticker symbol without the ordinary or commom stock number.
            - 'SEGMENT B3'(pt: SEGMENTO B3'): Type of stock
           
        - For NASDAQ, NYSE, AMEX:
            - 'sector': Sector of the company.
            - 'industry': Industry of the company.
            - 'country': Country where the company is listed.
            - 'name': Company name.
            - 'symbol': Ticker symbol.
    """     
    stock_exchange = stock_exchange.upper()
      
    if stock_exchange == 'B3':
        pt_url = r"https://www.b3.com.br/data/files/57/E6/AA/A1/68C7781064456178AC094EA8/ClassifSetorial.zip"
        eng_url = r"http://www.b3.com.br/data/files/DB/57/3B/29/78C7781064456178AC094EA8/ClassifSetorial_i.zip"
       
        if B3_language is None:
            column = 'CODE'
            url_dataset = eng_url
            dataset = download_ClassifSetorial(url_dataset)
            df = pd.read_excel(dataset, header=6)
            df = B3Eng_DataProcessing(df)
            
        elif B3_language == 'pt':
            column = 'CÓDIGO'
            url_dataset = pt_url
            dataset = download_ClassifSetorial(url_dataset)
            df = pd.read_excel(dataset, header=6)
            df = B3Pt_DataProcessing(df)

        if symbols is None:
            pass
    
        else:
            tickers = [ticker[:4].upper() for ticker in symbols]
            df = df.loc[df[column].isin(tickers)]
  
    else: 
        url = f'https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&exchange={stock_exchange}&download=true'
    
        json_data = request_nasdaq(url)
    
        df = pd.DataFrame(json_data['data']['rows'])
        if B3_language is None:
            df = df[['sector', 'industry', 'country', 'name', 'symbol']]
        else:
            print('The data does not have a Portuguese version')
            
        if symbols is None:
            pass
            
        else:
            tickers = [ticker.upper() for ticker in symbols]
            df = df.loc[df['symbol'].isin(tickers)]
    
    return df

  

# Define the function to fetch historical data
def get_historical_klines(symbol, interval, start_time, end_time=None):
    base_url = 'https://api.binance.com'
    endpoint = '/api/v3/klines'
    
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
    }
    
    if end_time:
        params['endTime'] = end_time
    
    response = requests.get(base_url + endpoint, params=params)
    data = response.json()
    
     # Convert data to DataFrame
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Convert timestamp to readable date
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df

def get_histdata_binance(symbol, interval, start_time, end_time):
    """
    This function returns Crypto Historical Data from Binance
    
    Parameters
    ----------
    symbol     : 'BTCUSDT'      - string format
    interval   : '1m' '5m' '1d' - string format
    start_time : '2024-01-01'   - '%Y-%m-%d' - string format
    end_time   : '2024-03-01'   - '%Y-%m-%d' - string format
    
    """
    all_data = []
    start_time = int((datetime.strptime(start_time, '%Y-%m-%d')).timestamp() *1000)
    end_time = int((datetime.strptime(end_time, '%Y-%m-%d')).timestamp() *1000)
    while start_time < end_time:
        df = get_historical_klines(symbol, interval, start_time, end_time)
        if df.empty:
            break
        all_data.append(df)
        start_time = int(df['timestamp'].iloc[-1].timestamp() * 1000) + 1  # move to the next interval
    
    return pd.concat(all_data)

def get_tick_b3(date):
    """
    This function extract Tick Data from B3 api for every Instrument traded in that given day.
    It returns and Pandas DataFrame

    Parameter
    ----------
    day : '2024-07-15'

    """
    url = 'https://arquivos.b3.com.br/apinegocios/tickercsv/'+ date
    file_name = str(date+'_B3_TickData.zip')
    wget.download(url,file_name)
    
    # Get the directory of the zip file
    zip_dir = os.path.dirname(file_name)
    
    # Create a ZipFile object
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        # Extract all the contents into the directory of the zip file
        zip_ref.extractall(zip_dir)
    print('/n')
    print("1/8 - Extracted all contents of ",file_name)
    
    # Read Extracted File
    folder_ref = os.getcwd()
    files = os.listdir(folder_ref)
    files_txt = [i for i in files if i.endswith('_NEGOCIOSAVISTA.txt')]
        
    df = pd.read_csv(files_txt[0], sep=";")

    # Update PrecoNegocio
    df['PrecoNegocio'] = df.PrecoNegocio.str.replace(",", ".").astype('float')
    print('2/8 - PrecoNegocio Updated')

    # Update Codigos Participantes
    df[['CodigoParticipanteComprador','CodigoParticipanteVendedor']] = df[['CodigoParticipanteComprador','CodigoParticipanteVendedor']].fillna(0)
    df[['CodigoParticipanteComprador','CodigoParticipanteVendedor']] = df[['CodigoParticipanteComprador','CodigoParticipanteVendedor']].astype('int').astype('str')
    print('3/8 - Codigos Participantes Updated')

    #Update Datetime
    # Ensure 'HoraFechamento' is a string and pad with leading zeros to ensure it's 9 characters long
    df['HoraFechamento'] = df['HoraFechamento'].astype(str).str.zfill(9)
    # Extract the hours, minutes, seconds, and milliseconds
    df['HoraFechamento'] = df['HoraFechamento'].apply(
        lambda x: f"{x[:2]}:{x[2:4]}:{x[4:6]}.{x[6:9]}"
    )
    # Ensure 'HoraFechamento' is a string
    df['HoraFechamento'] = df['HoraFechamento'].astype(str)
    # Convert the 'HoraFechamento' to datetime with the appropriate format including milliseconds
    df['HoraFechamento'] = pd.to_datetime(df['HoraFechamento'], format='%H:%M:%S.%f').dt.time
    print('4/8 - HoraFechamento Updated')

    #Create a New Index
    str1 = df.CodigoInstrumento
    str2 = df.CodigoIdentificadorNegocio.astype(str)
    str3 = df.DataReferencia.astype(str)
    str4 = df.HoraFechamento.astype(str)
    newindex = str1+'_'+str2+'_'+str3+'_'+str4
    df['Index'] = newindex
    # Set 'HoraFechamento' column as the index
    df = df.set_index('Index')
    print('5/8 - New_Index Created')

    # Remove a column inplace
    df.drop(columns=['AcaoAtualizacao','TipoSessaoPregao','DataNegocio'], inplace=True)
    print('6/8 - Columns Remove Updated')
    #Rename Columns
    dicionario = {'DataReferencia' : 'Dia', 'CodigoInstrumento' : 'Instrumento', 'PrecoNegocio' : 'Preco', 'QuantidadeNegociada' : 'Quantidade', 'HoraFechamento' : 'Hora', 'CodigoIdentificadorNegocio' : 'Cod_Negocio', 'CodigoParticipanteComprador' : 'Comprador', 'CodigoParticipanteVendedor' : 'Vendedor'}
    df.rename(dicionario, axis = 1, inplace=True)
    print('7/8 - Columns Rename Updated')
    #Reorder Columns
    new_order = ['Cod_Negocio', 'Instrumento', 'Dia', 'Hora','Preco','Quantidade','Comprador','Vendedor']
    df = df[new_order]
    print('(8/8 - Columns New Order Updated')
    print('Data Extraction and Transformation - Done')
    
    return df

