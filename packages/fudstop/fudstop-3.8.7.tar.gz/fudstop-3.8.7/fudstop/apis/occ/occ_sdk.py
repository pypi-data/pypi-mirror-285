import os
from dotenv import load_dotenv
load_dotenv
import aiohttp
import asyncio
import pandas as pd
import httpx
from typing import Optional
from .occ_models import OICOptionsMonitor
from .occ_models import OCCMostActive, StockInfo, ExpiryDates
from .occ_models import StockLoans, VolumeTotals, DailyMarketShare
from datetime import datetime, timedelta
from .occ_models import flatten_json
from fudstop.apis.helpers import format_large_numbers_in_dataframe

from asyncpg import create_pool
webull_id_df = pd.read_csv('ticker_csv.csv')
ticker_df = pd.read_csv('occ_tickers.csv')
class occSDK:
    def __init__(self, host, port, user, password, database):
        self.conn = None
        self.pool = None
        self.session = None
        self.ticker_df = pd.read_csv('ticker_csv.csv')
        self.ticker_to_id_map = dict(zip(self.ticker_df['ticker'], self.ticker_df['id']))

        self.host = host
        self.port = port
        self.user = user
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.today_mmddyyyy = datetime.now().strftime('%m/%d/%Y')
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.password = password
        self.database = database
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.base_url = f"https://marketdata.theocc.com/mdapi/"
        self.chat_memory = []  # In-memory list to store chat messages
        
        self.client_key = os.environ.get('OCC_CLIENT')
        self.ticker_to_id = self.load_ticker_to_id()


    @staticmethod
    def load_ticker_to_id():
        # Read the CSV file into a DataFrame
        df = pd.read_csv('occ_tickers.csv')
        # Create a dictionary mapping from the 'symbol' column to the 'id' column
        return pd.Series(df.id.values, index=df.symbol).to_dict()

    # Fetch all URLs
    async def get_headers(self):
        """REFRESH BEARER TOKEN"""    
        payload = { 
            'clientKey': self.client_key,
            'clientName': 'OIC_test',
            'userIdenteficator': os.environ.get('userIdenteficator')
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://ivlivefront.ivolatility.com/token/client/get", json=payload)

            token = resp.text
            headers = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json, text/plain, */*'
            }
            return headers

    async def convert_ms_timestamp(self, timestamp_ms):
        # Convert milliseconds to seconds
        timestamp_s = timestamp_ms / 1000.0
        return datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    async def fetch_url(session, url):
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Error: {response.status}")
                return None
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.pool = await create_pool(
            host=self.host, pool=self.pool, password=self.password, database=self.database, port=self.port, min_size=1, max_size=40
        )

        return self.pool
        

    async def save_to_database(self, flattened_data):
        async with self.pool.acquire() as conn:
            # Flatten the data and prepare it for insertion

            
            # Prepare the SQL INSERT query
            columns = ', '.join(flattened_data.keys())
            placeholders = ', '.join([f'${i+1}' for i in range(len(flattened_data))])
            query = f'INSERT INTO occ_totals ({columns}) VALUES ({placeholders})'
            
            # Execute the query
            await conn.execute(query, *flattened_data.values())


    async def stock_loans(self, report_date: str = None, type: str = "daily", as_dataframe:bool=True) -> Optional[StockLoans]:
        """Retrieve stock loan data for a specific report date and type.

        Args:
            report_date (str): Report date in YYYY-MM-DD format. Defaults to today's date.
            type (str): Report type. Defaults to "daily".

        Returns:
            Optional[StockLoans]: Stock loan data for the specified report date and type, or None if data is not available.
        """
        if report_date is None:
            report_date = self.today
        url=f"https://marketdata.theocc.com/mdapi/stock-loan?report_date={report_date}&report_type={type}"
        async with httpx.AsyncClient() as client:
            data = await client.get(url)
            r = data.json()
            entity = r['entity']
            stockLoanResults = StockLoans(entity['stockLoanResults'] if entity.get('stockLoanResults') is not None else None)
            if as_dataframe == True:
                df = stockLoanResults.as_dataframe
                df = format_large_numbers_in_dataframe(df)
                return df
            if stockLoanResults:
                return stockLoanResults
            else:
                return None



    async def volume_totals(self) -> VolumeTotals:
        """Retrieve volume totals data.

        Returns:
            VolumeTotals: Volume totals data.
        """
        url = "https://marketdata.theocc.com/mdapi/volume-totals"

        async with httpx.AsyncClient() as client:
            data = await client.get(url)
            r = data.json()
            entity = r['entity']
            if entity is not None:

                data = flatten_json(entity)

                df = pd.DataFrame(data, index=[0])

                df = format_large_numbers_in_dataframe(df)
                return df
            

    async def open_interest(self):

        """
        
        DATE FORMAT = MM/DD/YYYY
        """
        url = f"https://marketdata.theocc.com/mdapi/open-interest?report_date={self.today_mmddyyyy}"
        async with httpx.AsyncClient() as client:
            data = await client.get(url)
            r = data.json()

            entity = r['entity']


            optionsOI = entity['optionsOI']
            all_data = []

            for i in optionsOI:
                activityDate = await self.convert_ms_timestamp(i.get('activityDate'))
                equityCalls = i.get('equityCalls')
                equityPuts = i.get('equityPuts')
                indexCalls = i.get('indexCalls')
                indexPuts = i.get('indexPuts')
                treasuryCalls = i.get('treasuryCalls')
                treasuryPuts = i.get('treasuryPuts')
                equityTotal = i.get('equityTotal')
                indexTotal = i.get('indexTotal')
                treasuryTotal = i.get('treasuryTotal')
                futuresTotal = i.get('futuresTotal')
                occTotal = i.get('occTotal')

                data_dict = { 

                    'activity_date': activityDate,
                    'equity_calls': equityCalls,
                    'equity_puts': equityPuts,
                    'equity_total': equityTotal,
                    'index_calls': indexCalls,
                    'index_puts': indexPuts,
                    'index_total': indexTotal,
                    'treasury_calls': treasuryCalls,
                    'treasury_puts': treasuryPuts,
                    'treasury_total': treasuryTotal,
                    'futures_total': futuresTotal,
                    'occTotal': occTotal
                }

                all_data.append(data_dict)


            df =pd.DataFrame(all_data)
            df = format_large_numbers_in_dataframe(df)
            return df


    async def daily_market_share(self, date=None):
        today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
        date = today_str if not date else date
        url = f"https://marketdata.theocc.com/mdapi/daily-volume-totals?report_date={date}"

        async with httpx.AsyncClient() as client:
            data = await client.get(url)
            r = data.json()
            entity = r['entity']
            if entity['total_volume'] == []:
                f"https://marketdata.theocc.com/mdapi/daily-volume-totals?report_date={self.yesterday}"
                entity = r['entity']
                

                total_volume = DailyMarketShare(entity)
                df = total_volume.df
                df = format_large_numbers_in_dataframe(df)
                return df


            

            else:
                total_volume = DailyMarketShare(entity)
                df = total_volume.df
                df = format_large_numbers_in_dataframe(df)
                return df

    async def fetch_most_active(self):
        async with httpx.AsyncClient() as client:
            headers = await self.get_headers()
            response = await client.get("https://private-authorization.ivolatility.com/favorites/instruments/most-active", headers=headers)
            return OCCMostActive(response.json())

    async def get_webull_id(self, symbol):
        """Converts ticker name to ticker ID to be passed to other API endpoints from Webull."""
        try:
            webull_id_df = pd.read_csv('ticker_csv.csv')
            ticker_id = webull_id_df.loc[webull_id_df['ticker'] == symbol, 'id'].values[0]
            return ticker_id
        except IndexError:
            print(f"No ID found for ticker: {symbol}")
            return None
    

    async def get_stock_id(self, ticker):
        """Converts ticker name to ticker ID to be passed to other API endpoints from Webull."""
        try:
            stock_id = ticker_df.loc[ticker_df['symbol'] == ticker, 'id'].values[0]
            return stock_id
        except Exception as e:
            print(e)

        
    async def get_center(self, symbol):
        ticker_id = await self.get_webull_id(symbol)
        async with httpx.AsyncClient() as client:   

            data = await client.get(f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/stat?count=10&tickerId={ticker_id}&type=0")
            print(data)
            data = data.json()
            avg_price = data['avePrice']

            return avg_price



    async def options_monitor(self, symbol):
        try:
            stockId = await self.get_stock_id(symbol)
            center = await self.get_center(symbol)
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://private-authorization.ivolatility.com/options-monitor/listOptionDataRow?stockId={stockId}&regionId=1&center={center}&columns=alpha&columns=ask&columns=asksize&columns=asktime&columns=bid&columns=bidsize&columns=bidtime&columns=change&columns=changepercent&columns=delta&columns=theoprice&columns=gamma&columns=ivint&columns=ivask&columns=ivbid&columns=mean&columns=openinterest_eod&columns=optionsymbol&columns=volume&columns=paramvolapercent_eod&columns=alpha_eod&columns=ask_eod&columns=bid_eod&columns=delta_eod&columns=theoprice_eod&columns=gamma_eod&columns=ivint_eod&columns=mean_eod&columns=rho_eod&columns=theta_eod&columns=vega_eod&columns=changepercent_eod&columns=change_eod&columns=volume_eod&columns=quotetime&columns=rho&columns=strike&columns=style&columns=theta&columns=vega&columns=expirationdate&columns=forwardprice&columns=forwardprice_eod&columns=days&columns=days_eod&columns=iv&columns=iv_eod&rtMode=RT&userId=9999999&uuid=null", headers=await self.get_headers())

                data = response.json()
                data =  OICOptionsMonitor(data)
                df = data.as_dataframe
                df['ticker'] = symbol

                return data
        except Exception as e:
            print(e)
        




    async def get_symbol_ids(self):
        async with httpx.AsyncClient(headers=await self.get_headers()) as client:
            response = await client.get("https://private-authorization.ivolatility.com/lookup/?region=0&matchingType=CONTAINS&sortField=SYMBOL")
            data = response.json()

            page  = data['page']

            symbol = [i.get('symbol', 'N/A') for i in page]
            id = [i.get('stockId', 'N/A') for i in page]


            data_dict =  {
                'symbol': symbol,
                'id': id
            }

            df = pd.DataFrame(data_dict)

            df.to_csv('occ_tickers.csv', index=False)


    async def stock_info(self, symbol: str, has_options: bool = True):
        try:
            # Get the stock ID from the ticker symbol
            stockId = self.ticker_to_id.get(symbol)
            if stockId is None:
                raise ValueError(f"Ticker symbol '{symbol}' not found in the CSV file.")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://private-authorization.ivolatility.com/lookup/stockInformation?stockId={stockId}&region=1&rtMode=RT&hasOptions={has_options}",
                    headers=await self.get_headers()
                )

                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()

                return StockInfo(data, ticker=symbol)
        except Exception as e:
            print(f"Error fetching stock info for symbol '{symbol}': {e}")
        

    async def expiry_dates(self, symbol:str='AAPL'):
        headers = await self.get_headers()
        id = await self.get_webull_id(symbol)
        endpoint = f"https://private-authorization.ivolatility.com/optcalc/dictionary/expiration/{id}?isEod=false"
        async with httpx.AsyncClient(headers=headers) as client:
            data = await client.get(endpoint)
            data = data.json()


            return ExpiryDates(data)