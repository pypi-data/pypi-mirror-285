import pandas as pd


from fudstop.apis.polybull.polybull_sdk import PolybullSDK
from fudstop.apis.polygonio.polygon_options import PolygonOptions
from fudstop.apis.webull.webull_option_screener import WebullOptionScreener
from fudstop.apis.polygonio.polygon_database import PolygonDatabase
from fudstop.apis.webull.webull_options.webull_options import WebullOptions
from fudstop._markets.list_sets.ticker_lists import most_active_tickers
from fudstop.apis.webull.webull_option_screener import VolumeAnalysisDatas
import httpx
import asyncio
import asyncpg
import pandas as pd

# Initialize API and database objects
screen = WebullOptionScreener()
wb_opts = WebullOptions()
pb = PolybullSDK()
opts = PolygonOptions(database='market_data')
db = PolygonDatabase()
expiry = '2024-06-03'

async def get_data(id, conn_info):
    async with httpx.AsyncClient(headers=wb_opts.headers) as client:
        endpoint = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=200&tickerId={id}"
        response = await client.get(endpoint)
        data = response.json()
        vol_data_dict = { 
            'option_id': id,
            'trades': data.get('totalNum'),
            'total_vol': data.get('totalVolume'),
            'avg_price': data.get('avgPrice'),
            'buy_vol': data.get('buyVolume'),
            'neut_vol': data.get('neutralVolume'),
            'sell_vol': data.get('sellVolume')
        }

        # Filter out None values and convert to float
        vol_data_dict = {k: float(v) for k, v in vol_data_dict.items() if v is not None}
        
        # Update the database table for options
        async with asyncpg.connect(**conn_info) as conn:
            await conn.execute("""
                UPDATE options 
                SET trades = $1, total_vol = $2, avg_price = $3, buy_vol = $4, neut_vol = $5, sell_vol = $6 
                WHERE option_id = $7
            """, vol_data_dict.get('trades'), vol_data_dict.get('total_vol'), vol_data_dict.get('avg_price'), 
                vol_data_dict.get('buy_vol'), vol_data_dict.get('neut_vol'), vol_data_dict.get('sell_vol'), id)
            await conn.execute("""
                UPDATE wb_opts 
                SET trades = $1, total_vol = $2, avg_price = $3, buy_vol = $4, neut_vol = $5, sell_vol = $6 
                WHERE option_id = $7
            """, vol_data_dict.get('trades'), vol_data_dict.get('total_vol'), vol_data_dict.get('avg_price'), 
                vol_data_dict.get('buy_vol'), vol_data_dict.get('neut_vol'), vol_data_dict.get('sell_vol'), id)
        return vol_data_dict
async def update_ticker(ticker):
    conn_info = {
        'user': 'chuck',
        'password': 'fud',
        'database': 'market_data',
        'host': 'localhost',
        'port': 5432
    }

    try:
        base, from_, options = await wb_opts.all_options(ticker=ticker)

        price = await opts.get_price(ticker='I:SPX')
        upper_strike = float(price) * 1.10
        lower_strike = float(price) * 0.90
        if ticker == 'SPX':
            ticker = 'I:SPX'
        x = await opts.get_option_chain_all(underlying_asset=ticker, strike_price_gte=lower_strike, strike_price_lte=upper_strike, expiration_date=expiry)
        df = x.df
        df['option_id'] = options.as_dataframe['option_id']
        ids = df['option_id'].tolist()  # Ensure the ids are in a list format

        # Step 2: Extract volume analysis data
        tasks = [get_data(i, conn_info) for i in ids]
        vol_data_results = await asyncio.gather(*tasks)

        # Convert volume analysis data to DataFrame
        vol_data_df = pd.DataFrame(vol_data_results)

        # Replace NaN with None for database insertion
        vol_data_df = vol_data_df.where(pd.notnull(vol_data_df), None)

        # Step 3: Combine the main DataFrame with volume analysis data
        combined_df = df.merge(vol_data_df, on='option_id', how='left')

        # Replace NaN with None for database insertion
        combined_df = combined_df.where(pd.notnull(combined_df), None)

        # Ensure all values are properly formatted for insertion
        combined_df = combined_df.astype(object).where(pd.notnull(combined_df), None)
        print(combined_df)
        # Store the combined DataFrame in the database
        await db.batch_insert_dataframe(combined_df, table_name='options', unique_columns='ticker,strike,cp,expiry', batch_size=1000)
    except Exception as e:
        print(e)

