import sys
from pathlib import Path
from asyncpg.exceptions import UniqueViolationError
# Add the project directory to the sys.path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import httpx
from dotenv import load_dotenv
load_dotenv()
from asyncpg import create_pool
from urllib.parse import unquote
import os
from fudstop.apis.helpers import format_large_numbers_in_dataframe
from typing import List, Dict, Optional
import pandas as pd
import asyncio
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientConnectionError, ContentTypeError

from .models.aggregates import Aggregates
from .models.ticker_news import TickerNews
from .models.company_info import CombinedCompanyResults
from .models.technicals import RSI, EMA, SMA, MACD
from .models.gainers_losers import GainersLosers
from .models.ticker_snapshot import StockSnapshot
from .models.trades import TradeData, LastTradeData


from datetime import datetime, timedelta
import aiohttp

from urllib.parse import urlencode
import requests
from fudstop.apis.helpers import flatten_dict

YOUR_POLYGON_KEY = os.environ.get('YOUR_POLYGON_KEY')


session = requests.session()
class Polygon:
    def __init__(self, host='localhost', user='chuck', database='market_data', password='fud', port=5432):
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.database=database
        self.api_key = os.environ.get('YOUR_POLYGON_KEY')
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.thirty_days_from_now = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.fifteen_days_ago = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        self.fifteen_days_from_now = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        self.eight_days_from_now = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        self.eight_days_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')

        self.timeframes = ['minute', 'hour','day', 'week', 'month']
        self.session = None
    async def create_session(self):
        try:
            if self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession()
        except Exception as e:
            print(e)

    # Ensure to call this method to close the session
    async def close_session(self):
        if self.session is not None:
            await self.session.close()

    async def fetch_endpoint(self, url):
        await self.create_session()  # Ensure session is created
        async with self.session.get(url) as response:
            response.raise_for_status()  # Raises exception for HTTP errors
            return await response.json()
    async def connect(self, connection_string=None):
        if connection_string:
            self.pool = await create_pool(
                host=self.host,database=self.database,password=self.password,user=self.user,port=self.port, min_size=1, max_size=30
            )
        else:
            self.pool = await create_pool(
                host=os.environ.get('DB_HOST'),
                port=os.environ.get('DB_PORT'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database='market_data',
                min_size=1,
                max_size=10
            )
        return self.pool

    async def save_structured_message(self, data: dict, table_name: str):
        fields = ', '.join(data.keys())
        values = ', '.join([f"${i+1}" for i in range(len(data))])
        
        query = f'INSERT INTO {table_name} ({fields}) VALUES ({values})'
      
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(query, *data.values())
            except UniqueViolationError:
                print('Duplicate - SKipping')



    async def fetch_page(self, url):
        if 'apiKey' not in url:
            url = url + f"?apiKey={os.environ.get('YOUR_POLYGON_KEY')}"
        await self.create_session()
        try:
            async with self.session.get(url) as response:
                return await response.json()
        except Exception:
            print(f"ERROR!")
            
    async def paginate_concurrent(self, url, as_dataframe=False, concurrency=250):

        all_results = []

        

        pages_to_fetch = [url]
        
        while pages_to_fetch:
            tasks = []
            
            for _ in range(min(concurrency, len(pages_to_fetch))):
                next_url = pages_to_fetch.pop(0)
                tasks.append(self.fetch_page(next_url))
                
            results = await asyncio.gather(*tasks)
            if results is not None:
                for data in results:
                    if data is not None:
                        if "results" in data:
                            all_results.extend(data["results"])

                            
                        next_url = data.get("next_url")
                        if next_url:
                            next_url += f'&{urlencode({"apiKey": f"{self.api_key}"})}'
                            pages_to_fetch.append(next_url)
                    else:
                        break
        if as_dataframe:
            import pandas as pd
            return pd.DataFrame(all_results)
        else:
            return all_results
        

    async def fetch_endpoint(self, url):
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def last_trade(self, ticker):
        endpoint = f"https://api.polygon.io/v2/last/trade/{ticker}?apiKey={self.api_key}"

        await self.create_session()
        try:
            async with self.session.get(endpoint) as response:
                response.raise_for_status()
                data = await response.json()
                results = data.get('results')

                if results:
                    return LastTradeData(results)
                else:
                    print("No results found")
        except aiohttp.ClientResponseError as e:
            print(f"Client response error - status {e.status}: {e.message}")
        except aiohttp.ClientError as e:
            print(f"Client error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        

    async def close_session(self):
        await self.session.close()
                    

    async def get_aggs(self, ticker:str='AAPL', multiplier:int=1, timespan:str='second', date_from:str='2024-01-01', date_to:str='2024-04-12', adjusted:str='true', sort:str='asc', limit:int=50000):
        """
        Fetches candlestick data for a ticker, option symbol, crypto/forex pair.
        
        Parameters:
        - ticker (str): The ticker symbol for which to fetch data.

        - timespan: The timespan to survey.

        TIMESPAN OPTIONS:

        >>> second
        >>> minute
        >>> hour
        >>> day
        >>> week
        >>> month
        >>> quarter
        >>> year



        >>> Multiplier: the number of timespans to survey.

        - date_from (str, optional): The starting date for the data fetch in yyyy-mm-dd format.
                                     Defaults to 30 days ago if not provided.
        - date_to (str, optional): The ending date for the data fetch in yyyy-mm-dd format.
                                   Defaults to today's date if not provided.

        - limit: the amount of candles to return. Defaults to 500



        Returns:
        - dict: Candlestick data for the given ticker and date range.

        Example:
        >>> await aggregates('AAPL', date_from='2023-09-01', date_to='2023-10-01')
        """


        endpoint = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{date_from}/{date_to}?adjusted={adjusted}&sort={sort}&limit={limit}&apiKey={os.environ.get('YOUR_POLYGON_KEY')}"
  
        async with httpx.AsyncClient() as client:
            data = await client.get(endpoint)

            data = data.json()

            results = data['results'] if 'results' in data else None

            if results is not None:

                results = Aggregates(results, ticker)


                return results



    async def market_news(self, limit: str = '100'):
        """
        Arguments:

        >>> ticker: the ticker to query (optional)
        >>> limit: the number of news items to return (optional) | Max 1000

        """
        params = {
            'apiKey': self.api_key,
            'limit': limit
        }


        endpoint = "https://api.polygon.io/v2/reference/news"

        data = await self.fetch_endpoint(endpoint, params=params)
        data = TickerNews(data)

        return data
    

    async def dark_pools(self, ticker:str, multiplier:int, timespan:str, date_from:str, date_to:str):

        aggs = await self.get_aggs(ticker=ticker, multiplier=multiplier, timespan=timespan, date_from=date_from, date_to=date_to)



        # Assuming 'aggs' is an instance of the Aggregates class with populated data
        dollar_cost_above_10m_details = [
            {'Close Price': aggs.close[i], 'Timestamp': aggs.timestamp[i], 'Dollar Cost': cost}
            for i, cost in enumerate(aggs.dollar_cost) 
            if cost > 10000000
        ]

        # Create DataFrame from the list of dictionaries
        df_dollar_cost_above_10m = pd.DataFrame(dollar_cost_above_10m_details)

        # Print the DataFrame to see the result
        df = format_large_numbers_in_dataframe(df_dollar_cost_above_10m)

        return df

    async def top_gainers_losers(self, type:str='gainers'):
        endpoint = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/{type}?apiKey={self.api_key}"

        async with httpx.AsyncClient() as client:
            data = await client.get(endpoint)
            data = data.json()
            tickers = data['tickers'] if 'tickers' in data else None
            return GainersLosers(tickers)

    async def company_info(self, ticker) -> CombinedCompanyResults:
        url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
        await self.create_session()
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                results_data = data['results'] if 'results' in data else None
                if results_data is not None:
                    return CombinedCompanyResults(
                        ticker=results_data.get('ticker'),
                        name=results_data.get('name'),
                        market=results_data.get('market'),
                        locale=results_data.get('locale'),
                        primary_exchange=results_data.get('primary_exchange'),
                        type=results_data.get('type'),
                        active=results_data.get('active'),
                        currency_name=results_data.get('currency_name'),
                        cik=results_data.get('cik'),
                        composite_figi=results_data.get('composite_figi'),
                        share_class_figi=results_data.get('share_class_figi'),
                        market_cap=results_data.get('market_cap'),
                        phone_number=results_data.get('phone_number'),
                        description=results_data.get('description'),
                        sic_code=results_data.get('sic_code'),
                        sic_description=results_data.get('sic_description'),
                        ticker_root=results_data.get('ticker_root'),
                        homepage_url=results_data.get('homepage_url'),
                        total_employees=results_data.get('total_employees'),
                        list_date=results_data.get('list_date'),
                        share_class_shares_outstanding=results_data.get('share_class_shares_outstanding'),
                        weighted_shares_outstanding=results_data.get('weighted_shares_outstanding'),
                        round_lot=results_data.get('round_lot'),
                        address1=results_data.get('address', {}).get('address1'),
                        city=results_data.get('address', {}).get('city'),
                        state=results_data.get('address', {}).get('state'),
                        postal_code=results_data.get('address', {}).get('postal_code'),
                        logo_url=results_data.get('branding', {}).get('logo_url'),
                        icon_url=results_data.get('branding', {}).get('icon_url')
                    )
                else:
                    print(f'Couldnt get info for {ticker}')
        finally:
            await self.close_session()
    def company_info_sync(self, ticker) -> CombinedCompanyResults:
        url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
        data = session.get(url).json()
        results_data = data['results'] if 'results' in data else None
        if results_data is not None:
            return CombinedCompanyResults(
                ticker=results_data.get('ticker'),
                name=results_data.get('name'),
                market=results_data.get('market'),
                locale=results_data.get('locale'),
                primary_exchange=results_data.get('primary_exchange'),
                type=results_data.get('type'),
                active=results_data.get('active'),
                currency_name=results_data.get('currency_name'),
                cik=results_data.get('cik'),
                composite_figi=results_data.get('composite_figi'),
                share_class_figi=results_data.get('share_class_figi'),
                market_cap=results_data.get('market_cap'),
                phone_number=results_data.get('phone_number'),
                description=results_data.get('description'),
                sic_code=results_data.get('sic_code'),
                sic_description=results_data.get('sic_description'),
                ticker_root=results_data.get('ticker_root'),
                homepage_url=results_data.get('homepage_url'),
                total_employees=results_data.get('total_employees'),
                list_date=results_data.get('list_date'),
                share_class_shares_outstanding=results_data.get('share_class_shares_outstanding'),
                weighted_shares_outstanding=results_data.get('weighted_shares_outstanding'),
                round_lot=results_data.get('round_lot'),
                address1=results_data.get('address', {}).get('address1'),
                city=results_data.get('address', {}).get('city'),
                state=results_data.get('address', {}).get('state'),
                postal_code=results_data.get('address', {}).get('postal_code'),
                logo_url=results_data.get('branding', {}).get('logo_url'),
                icon_url=results_data.get('branding', {}).get('icon_url')
            )
        else:
            print(f'Couldnt get info for {ticker}')

    async def get_all_tickers(self, include_otc=False, save_all_tickers:bool=False):
        """
        Fetches a list of all stock tickers available on Polygon.io.

        Arguments:
            >>> include_otc: optional - whether to include OTC securities or not

            >>> save_all_tickers: optional - saves all tickers as a list for later processing

        Returns:
            A list of StockSnapshot objects, each containing data for a single stock ticker.

        Usage:
            To fetch a list of all stock tickers available on Polygon.io, you can call:
            ```
            tickers = await sdk.get_all_tickers()
            print(f"Number of tickers found: {len(tickers)}")
            ```
        """
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={self.api_key}"
        params = {
            "apiKey": self.api_key,
        }
    
        await self.create_session()
        try:
            async with self.session.get(url, params=params) as response:
                response_data = await response.json()



                tickers = response_data['tickers']
                
                data = StockSnapshot(tickers)

                return data
                # if save_all_tickers:
                #     # Extract tickers to a list
                #     ticker_list = [ticker['ticker'] for ticker in tickers]
                    
                #     # Write the tickers to a file
                #     with open('list_sets/saved_tickers.py', 'w') as f:
                #         f.write(str(ticker_list))
                # return ticker_data
        finally:
            await self.close_session()

    async def rsi(self, ticker:str, timespan:str, limit:str='1', window:int=14, date_from:str=None, date_to:str=None, session=None, snapshot:bool=False):
        """
        Arguments:

        >>> ticker

        >>> AVAILABLE TIMESPANS:

        minute
        hour
        day
        week
        month
        quarter
        year

        >>> date_from (optional) 
        >>> date_to (optional)
        >>> window: the RSI window (default 14)
        >>> limit: the number of N timespans to survey
        
        >>> *SNAPSHOT: scan all timeframes for a ticker

        """
        try:
            if date_from is None:
                date_from = self.eight_days_ago

            if date_to is None:
                date_to = self.today

            if timespan == 'month':
                date_from = self.thirty_days_ago
            
            endpoint = f"https://api.polygon.io/v1/indicators/rsi/{ticker}?timespan={timespan}&timestamp.gte={date_from}&timestamp.lte={date_to}&limit={limit}&window={window}&expand_underlying=true&apiKey={self.api_key}"
    
       
            async with httpx.AsyncClient() as client:
                try:
                    data = await client.get(endpoint)
                    datas = data.json()
                      
                    if datas is not None:

                        

                
                        return RSI(datas, ticker)
                except ClientOSError as e:
                    print(f'ERROR {e}')
                

            if snapshot == True:
                tasks = []
                timespans = self.timeframes
                for timespan in timespans:
                    tasks.append(asyncio.create_task)
        except Exception as e:
            print(e)


    async def get_cik(self, ticker):
        try:
            endpoint = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={os.environ.get('YOUR_POLYGON_KEY')}"
            async with httpx.AsyncClient() as client:
                data = await client.get(endpoint)

                cik = data.json()['results']['cik']

                
                return cik
        except Exception as e:
            print(e)

    async def macd(self, ticker: str, timespan: str, limit: str = '1000'):
        """
        Arguments:

        >>> ticker

        >>> AVAILABLE TIMESPANS:

        minute
        hour
        day
        week
        month
        quarter
        year
        >>> window: the RSI window (default 14)
        >>> limit: the number of N timespans to survey
        
        """
        try:
            endpoint = f"https://api.polygon.io/v1/indicators/macd/{ticker}?timespan={timespan}&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&apiKey={self.api_key}&limit={limit}"
            async with httpx.AsyncClient() as client:
                data = await client.get(endpoint)
                datas = data.json()
                if datas is not None:
                    return MACD(datas, ticker)
        except Exception as e:
            print(f"Unexpected error - {ticker}: {e}")
    async def sma(self, ticker:str, timespan:str, limit:str='1000', window:str='9', date_from:str=None, date_to:str=None):
        """
        Arguments:

        >>> ticker

        >>> AVAILABLE TIMESPANS:

        minute
        hour
        day
        week
        month
        quarter
        year

        >>> date_from (optional) 
        >>> date_to (optional)
        >>> window: the SMA window (default 9)
        >>> limit: the number of N timespans to survey
        
        """
        try:
            if date_from is None:
                date_from = self.eight_days_ago

            if date_to is None:
                date_to = self.today


            endpoint = f"https://api.polygon.io/v1/indicators/sma/{ticker}?timespan={timespan}&window={window}&timestamp.gte={date_from}&timestamp.lte={date_to}&limit={limit}&apiKey={self.api_key}"
            await self.create_session()
            try:
                

                async with self.session.get(endpoint) as resp:
                    datas = await resp.json()


                    return SMA(datas, ticker)
            finally:
                pass
        except Exception as e:
            print(e)


    async def ema(self, ticker:str, timespan:str, limit:str='1', window:str='21', date_from:str=None, date_to:str=None):
        """
        Arguments:

        >>> ticker

        >>> AVAILABLE TIMESPANS:

        minute
        hour
        day
        week
        month
        quarter
        year

        >>> date_from (optional) 
        >>> date_to (optional)
        >>> window: the EMA window (default 21)
        >>> limit: the number of N timespans to survey
        
        """
        try:
            if date_from is None:
                date_from = self.eight_days_ago

            if date_to is None:
                date_to = self.today


            endpoint = f"https://api.polygon.io/v1/indicators/ema/{ticker}?timespan={timespan}&window={window}&timestamp.gte={date_from}&timestamp.lte={date_to}&limit={limit}&apiKey={self.api_key}"

            
            try:
                await self.create_session()  # Ensure the session is created
                async with self.session.get(endpoint) as resp:
                    datas = await resp.json()
                    return EMA(datas, ticker)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)





    async def get_universal_snapshot(self, ticker, retries=3): #✅
        """Fetches the Polygon.io universal snapshot API endpoint"""
        timeout = aiohttp.ClientTimeout(total=10)  # 10 seconds timeout for the request
        
        for retry in range(retries):
        # async with sema:
            url = f"https://api.polygon.io/v3/snapshot?ticker.any_of={ticker}&apiKey={self.api_key}&limit=250"
            await self.create_session()
            try:
            

                try:
                    async with self.session.get(url) as resp:
                        data = await resp.json()
                        results = data.get('results', None)
        
                        if results is not None:
                            flattened_results = [flatten_dict(result) for result in results]
                            return flattened_results
                            
                except aiohttp.ClientConnectorError:
                    print("ClientConnectorError occurred. Retrying...")
                    continue
                
                except aiohttp.ContentTypeError as e:
                    print(f"ContentTypeError occurred: {e}")  # Consider logging this
                    continue
                
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")  # Consider logging this
                    continue
            except Exception as e:
                print(e)



    async def get_price(self, ticker):
        try:
            url = f"https://api.polygon.io/v2/last/nbbo/{ticker}?apiKey={os.environ.get('YOUR_POLYGON_KEY')}"
            async with httpx.AsyncClient() as client:
                r = await client.get(url)
                if r.status_code == 200:
                    r = r.json()
                    results = r['results'] if 'results' in r else None
                    if results is not None:
                        price = results['P']
              
                        return price
        except Exception as e:
            print(e)

    async def rsi_snapshot(self, ticker):
        try:
            price = await self.get_price(ticker)
            if price is not None:
                rsis = {}
                rsis.update({'ticker': ticker,
                            'price': price})
                minrsi = asyncio.create_task(self.rsi(ticker,timespan='minute'))
                drsi = asyncio.create_task(self.rsi(ticker, timespan='day'))
                hrsi = asyncio.create_task(self.rsi(ticker, timespan='hour'))
                wrsi = asyncio.create_task(self.rsi(ticker, timespan='week'))
                mrsi = asyncio.create_task(self.rsi(ticker, timespan='month'))
                day_rsi, hour_rsi, week_rsi, month_rsi, minute_rsi = await asyncio.gather(drsi, hrsi, wrsi, mrsi, minrsi)
                if day_rsi is not None and hasattr(day_rsi, 'rsi_value') and day_rsi.rsi_value is not None and len(day_rsi.rsi_value) > 0:
                    day_rsi = day_rsi.rsi_value[0]

                    rsis.update({'day_rsi': day_rsi})

                if hour_rsi is not None and hasattr(hour_rsi, 'rsi_value') and hour_rsi.rsi_value is not None and len(hour_rsi.rsi_value) > 0:
                    hour_rsi = hour_rsi.rsi_value[0]
                    rsis.update({'hour_rsi': hour_rsi})


                if week_rsi is not None and hasattr(week_rsi, 'rsi_value') and week_rsi.rsi_value is not None and len(week_rsi.rsi_value) > 0:
                    week_rsi = week_rsi.rsi_value[0]
                    rsis.update({'week_rsi': week_rsi})
                if month_rsi is not None and hasattr(month_rsi, 'rsi_value') and month_rsi.rsi_value is not None and len(month_rsi.rsi_value) > 0:
                    month_rsi = month_rsi.rsi_value[0]
                    rsis.update({'month_rsi': month_rsi})


                if minute_rsi is not None and hasattr(minute_rsi, 'rsi_value') and minute_rsi.rsi_value is not None and len(minute_rsi.rsi_value) > 0:
                    minute_rsi = minute_rsi.rsi_value[0]
                    rsis.update({'minute_rsi': minute_rsi})

                
                df = pd.DataFrame(rsis, index=[0])

                return df
        except Exception as e:
            print(e)

    async def check_macd_sentiment(self, hist: list):
        try:
            if hist is not None:
                if hist is not None and len(hist) >= 3:
                    
                    last_three_values = hist[:3]
                    if abs(last_three_values[0] - (-0.02)) < 0.04 and all(last_three_values[i] > last_three_values[i + 1] for i in range(len(last_three_values) - 1)):
                        return 'bullish'

                    if abs(last_three_values[0] - 0.02) < 0.04 and all(last_three_values[i] < last_three_values[i + 1] for i in range(len(last_three_values) - 1)):
                        return 'bearish'
                else:
                    return '-'
        except Exception as e:
            print(e)



    async def histogram_snapshot(self, ticker):
        try:
            price = await self.get_price(ticker)
            if price is not None:
                histograms = {}
                dhist = asyncio.create_task(self.macd(ticker, timespan='day', limit='10'))
                hhist= asyncio.create_task(self.macd(ticker, timespan='hour', limit='10'))
                whist = asyncio.create_task(self.macd(ticker, timespan='week', limit='10'))
                mhist = asyncio.create_task(self.macd(ticker, timespan='month', limit='10'))
                day_hist, hour_hist, week_hist, month_hist = await asyncio.gather(dhist, hhist, whist, mhist)
                if day_hist is not None and hasattr(day_hist, 'macd_histogram') and day_hist.macd_histogram is not None and len(day_hist.macd_histogram) > 2:
                    day_hist = day_hist.macd_histogram
         


                    day_sentiment = await self.check_macd_sentiment(day_hist)
                    histograms.update({'day_sentiment': day_sentiment})
                if hour_hist is not None and hasattr(hour_hist, 'macd_histogram') and hour_hist.macd_histogram is not None and len(hour_hist.macd_histogram) > 2:
                    hour_hist = hour_hist.macd_histogram
                

                    hour_sentiment = await self.check_macd_sentiment(hour_hist)
                    histograms.update({'hour_sentiment': hour_sentiment})

                if week_hist is not None and hasattr(week_hist, 'macd_histogram') and week_hist.macd_histogram is not None and len(week_hist.macd_histogram) > 2:
                    week_hist = week_hist.macd_histogram
          
         

                    week_sentiment = await self.check_macd_sentiment(week_hist)
                    histograms.update({'week_sentiment': week_sentiment})
                    
                if month_hist is not None and hasattr(month_hist, 'macd_histogram') and month_hist.macd_histogram is not None and len(month_hist.macd_histogram) > 2:
                    month_hist = month_hist.macd_histogram
                


                    month_sentiment = await self.check_macd_sentiment(month_hist)
                    histograms.update({'month_sentiment': month_sentiment})
                
                df = pd.DataFrame(histograms, index=[0])
                df['ticker'] = ticker
                df['price'] = price

                return df
        except Exception as e:
            print(e)


    async def gather_rsi_for_all_tickers(self, tickers) -> List[RSI]:

        """Get RSI for all tickers
        
        Arguments:

        >>> tickers: A list of tickers


        >>> timespan: 

           minute
           hour
           day
           week
           month
           year
           quaeter
        
        """
        timespans = ['minute', 'hour', 'day', 'week']
        tasks = [self.rsi(ticker, timespan) for ticker in tickers for timespan in timespans]
        await asyncio.gather(*tasks)
            
            
    async def get_polygon_logo(self, symbol: str) -> Optional[str]:
        """
        Fetches the URL of the logo for the given stock symbol from Polygon.io.

        Args:
            symbol: A string representing the stock symbol to fetch the logo for.

        Returns:
            A string representing the URL of the logo for the given stock symbol, or None if no logo is found.

        Usage:
            To fetch the URL of the logo for a given stock symbol, you can call:
            ```
            symbol = "AAPL"
            logo_url = await sdk.get_polygon_logo(symbol)
            if logo_url is not None:
                print(f"Logo URL: {logo_url}")
            else:
                print(f"No logo found for symbol {symbol}")
            ```
        """
        try:
            url = f'https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={self.api_key}'
            await self.create_session()
            try:
                async with self.session.get(url) as response:
                    data = await response.json()
                    
                    if 'results' not in data:
                        # No results found
                        return None
                    
                    results = data['results']
                    branding = results.get('branding')

                    if branding and 'icon_url' in branding:
                        encoded_url = branding['icon_url']
                        decoded_url = unquote(encoded_url)
                        url_with_api_key = f"{decoded_url}?apiKey={self.api_key}"
                        return url_with_api_key

            finally:
                pass
        except Exception as e:
            print(e)
    async def stock_trades(self, ticker: str, limit: str = '50000', timestamp_gte: str = None, timestamp_lte: str = None):
        if timestamp_gte is None:
            timestamp_gte = self.thirty_days_ago

        if timestamp_lte is None:
            timestamp_lte = self.today

        # Construct the params dictionary
        params = {
            'limit': limit,
            'timestamp.gte': timestamp_gte,
            'timestamp.lte': timestamp_lte,
            'sort': 'timestamp',
            'apiKey': self.api_key
        }

        # Define the endpoint without query parameters
        endpoint = f"https://api.polygon.io/v3/trades/{ticker}?timestamp.gte={timestamp_gte}&timestamp.lte={timestamp_lte}&apiKey={self.api_key}&limit={limit}"

        await self.create_session()

        async with self.session.get(endpoint) as response:
            data = await response.json()
            results = data.get('results')
            if results is not None:
                return TradeData(results, ticker)
            else:
                print(f'No data for {ticker}')
            

    async def test_trades(self, ticker: str, limit: int = 50000, timestamp_gte: str = None, timestamp_lte: str = None):
        if timestamp_gte is None:
            timestamp_gte = self.thirty_days_ago

        if timestamp_lte is None:
            timestamp_lte = self.today

        # Construct the params dictionary
        params = {
            'limit': limit,
            'timestamp.gte': timestamp_gte,
            'timestamp.lte': timestamp_lte,
            'sort': 'timestamp',
            'apiKey': self.api_key
        }

        # Define the endpoint without query parameters
        endpoint = f"https://api.polygon.io/v3/trades/{ticker}?timestamp.gte={timestamp_gte}&timestamp.lte={timestamp_lte}&apiKey={self.api_key}&limit={limit}"
        try:
            await self.create_session()
            data = await self.fetch_page(endpoint)
            if data is not None:
                results = data.get('results')
                if results is not None:
                    return TradeData(results, ticker)
                else:
                    print(f'No data for {ticker}')
        finally:
            await self.close_session()



    async def get_universal_snapshots_by_type(self, type:str='stocks'):
        try:
            await self.create_session()

            endpoint = f"https://api.polygon.io/v3/snapshot?type={type}&apiKey={self.api_key}"

            data = await self.fetch_page(endpoint)
            if data is not None:
                results = data.get('results')
                if results is not None:
                    return results

        finally:
            await self.close_session()