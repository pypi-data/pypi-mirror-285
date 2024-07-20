import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
import requests
import httpx
from typing import List
load_dotenv()




import pandas as pd
from fudstop.apis.polygonio.polygon_database import PolygonDatabase
import os
import hashlib
from .screener_models import ScreenerResults,OptionScreenerResults
import time
import uuid
import pickle
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()
import httpx
import asyncio
class PaperTrader:
    def __init__(self):
        self.id = 16067985
        self.headers  = {
        "Accept": os.getenv("ACCEPT"),
        "Accept-Encoding": os.getenv("ACCEPT_ENCODING"),
        "Accept-Language": "en-US,en;q=0.9",
        'Content-Type': 'application/json',
        "App": os.getenv("APP"),
        "App-Group": os.getenv("APP_GROUP"),
        "Appid": os.getenv("APPID"),
        "Device-Type": os.getenv("DEVICE_TYPE"),
        "Did": 'gldaboazf4y28thligawz4a7xamqu91g',
        "Hl": os.getenv("HL"),
        "Locale": os.getenv("LOCALE"),
        "Origin": os.getenv("ORIGIN"),
        "Os": os.getenv("OS"),
        "Osv": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Ph": os.getenv("PH"),
        "Platform": os.getenv("PLATFORM"),
        "Priority": os.getenv("PRIORITY"),
        "Referer": os.getenv("REFERER"),
        "Reqid": os.getenv("REQID"),
        "T_time": os.getenv("T_TIME"),
        "Tz": os.getenv("TZ"),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Ver": os.getenv("VER"),
        "X-S": os.getenv("X_S"),
        "X-Sv": os.getenv("X_SV")
    }
        #miscellaenous
                #sessions

        self._region_code = 6
        self.zone_var = 'dc_core_r001'
        self.timeout = 15
        self.db = PolygonDatabase(host='localhost', user='chuck', database='fudstop2', password='fud', port=5432)
        self.device_id = "gldaboazf4y28thligawz4a7xamqu91g"
        

    def to_decimal(self, value: Optional[str]) -> str:
        """
        Convert percentage string to decimal string if needed.
        """
        if value is not None and float(value) > 1:
            return str(float(value) / 100)
        return value


    async def get_token(self):
        endpoint = f"https://u1suser.webullfintech.com/api/user/v1/login/account/v2"

        async with httpx.AsyncClient(headers=self.headers) as client:
            data = await client.post(endpoint, json={"account":"brainfartastic@gmail.com","accountType":"2","pwd":"306a2ecebccfb37988766fac58f9d0e3","deviceId":"gldaboazf4y28thligawz4a7xamqu91g","deviceName":"Windows Chrome","grade":1,"regionId":1})
            data = data.json()
            token = data.get('accessToken')
            return token

    async def get_data(self, endpoint):
        token = await self.get_token()
        self.headers['Access_token'] = token
        async with httpx.AsyncClient(headers=self.headers) as client:
            data = await client.get(endpoint)

            return data.json()
        
    async def post_data(self, endpoint, payload):
        token = await self.get_token()
        self.headers['Access_token'] = token
        async with httpx.AsyncClient(headers=self.headers) as client:
            data = await client.post(endpoint, json=payload)

            return data.json()
    

    async def option_order(self, type:str='LMT', quantity:int=1, action:str='BUY', option_id:str='1044423960', price:str='0.05'):
        endpoint = f"https://act.webullfintech.com/webull-paper-center/api/paper/v1/order/optionPlace"


        serial_id = int(uuid.uuid4())  # Generate a UUID and convert it to a string
        payload = {"accountId":15765933,"orderType":type,"timeInForce":"DAY","quantity":quantity,"action":action,"tickerId":option_id,"lmtPrice":price,"orders":[{"action":action,"quantity":quantity,"tickerId":option_id,"tickerType":"OPTION"}],"paperId":1,"tickerType":"OPTION","optionStrategy":"Single","serialId":serial_id}
        token = await self.get_token()
        self.headers['Access_token'] = token
        async with httpx.AsyncClient(headers=self.headers) as client:
            data = await client.post(endpoint, headers=self.headers, json=payload)

            print(data.json())


    async def rsi_screener(self, rsi_gte:str='70'):
        payload = {"fetch":200,"rules":{"wlas.screener.rule.rsi":rsi_gte,"wlas.screener.rule.region":"securities.region.name.6"},"sort":{"rule":"wlas.screener.rule.price","desc":True},"attach":{"hkexPrivilege":False}}
        
        endpoint = f"https://quotes-gw.webullfintech.com/api/wlas/screener/ng/query"

        data = await self.post_data(endpoint=endpoint, payload=payload)

        return ScreenerResults(data)
        

    async def options_screener(
        self,
        exp_gte: str,
        exp_lte: str,
        oi_gte: Optional[str] = None,
        oi_lte: Optional[str] = None,
        cr_lte: Optional[str] = None,
        vol_gte: Optional[str] = None,
        vol_lte: Optional[str] = None,
        iv_percentile_gte: Optional[str] = None,
        iv_percentile_lte: Optional[str] = None,
        hv_gte: Optional[str] = None,
        hv_lte: Optional[str] = None,
        delta_gte: Optional[str] = None,
        delta_lte: Optional[str] = None,
        ticker_iv_gte: Optional[str] = None,
        ticker_iv_lte: Optional[str] = None,
        pulse_gte: Optional[str] = None,
        pulse_lte: Optional[str] = None,
        avg30_vol_gte: Optional[str] = None,
        avg30_vol_lte: Optional[str] = None,
        total_vol_gte: Optional[str] = None,
        total_vol_lte: Optional[str] = None,
        total_oi_gte: Optional[str] = None,
        total_oi_lte: Optional[str] = None,
        avg30_oi_gte: Optional[str] = None,
        avg30_oi_lte: Optional[str] = None,
        bid_gte: Optional[str] = None,
        bid_lte: Optional[str] = None,
        change_ratio_gte: Optional[str] = None,
        change_ratio_lte: Optional[str] = None,
        ask_gte: Optional[str] = None,
        ask_lte: Optional[str] = None,
        close_gte: Optional[str] = None,
        close_lte: Optional[str] = None,
        theta_gte: Optional[str] = None,
        theta_lte: Optional[str] = None,
        impl_vol_gte: Optional[str] = None,
        impl_vol_lte: Optional[str] = None,
        additional_rules: Optional[Dict[str, Any]] = None
    ) -> OptionScreenerResults:
        """
        Screen for options based on various criteria.

        Parameters:
            exp_gte (str, optional): Minimum expiration date. Default is '1'.
            exp_lte (str, optional): Maximum expiration date. Default is '1'.
            oi_gte (str, optional): Minimum open interest. Default is '1000'.
            oi_lte (str, optional): Maximum open interest. Default is '35000'.
            cr_lte (str, optional): Maximum change ratio. Default is '-55.12'.
            vol_gte (str, optional): Minimum volume. Default is '2000'.
            vol_lte (str, optional): Maximum volume. Default is '25000'.
            iv_percentile_gte (str, optional): Minimum implied volatility percentile. Default is '0.0'.
            iv_percentile_lte (str, optional): Maximum implied volatility percentile. Default is '40'.
            hv_gte (str, optional): Minimum historical volatility. Default is '0'.
            hv_lte (str, optional): Maximum historical volatility. Default is '45'.
            delta_gte (str, optional): Minimum delta. Default is '-36.63'.
            delta_lte (str, optional): Maximum delta. Default is '35.26'.
            ticker_iv_gte (str, optional): Minimum ticker implied volatility. Default is '28.76'.
            ticker_iv_lte (str, optional): Maximum ticker implied volatility. Default is '62.39'.
            pulse_gte (str, optional): Minimum pulse index. Default is '47.63'.
            pulse_lte (str, optional): Maximum pulse index. Default is '128.73'.
            avg30_vol_gte (str, optional): Minimum 30-day average volume. Default is '150000'.
            avg30_vol_lte (str, optional): Maximum 30-day average volume. Default is '350000'.
            total_vol_gte (str, optional): Minimum total volume. Default is '1990000'.
            total_vol_lte (str, optional): Maximum total volume. Default is '4190000'.
            total_oi_gte (str, optional): Minimum total open interest. Default is '450000'.
            total_oi_lte (str, optional): Maximum total open interest. Default is '1170000'.
            avg30_oi_gte (str, optional): Minimum 30-day average open interest. Default is '490000'.
            avg30_oi_lte (str, optional): Maximum 30-day average open interest. Default is '1270000'.
            bid_gte (str, optional): Minimum bid price. Default is '66.1'.
            bid_lte (str, optional): Maximum bid price. Default is '133.1'.
            change_ratio_gte (str, optional): Minimum change ratio. Default is '-9.29'.
            change_ratio_lte (str, optional): Maximum change ratio. Default is '-0.97'.
            ask_gte (str, optional): Minimum ask price. Default is '63.2'.
            ask_lte (str, optional): Maximum ask price. Default is '127.2'.
            close_gte (str, optional): Minimum close price. Default is '19.9'.
            close_lte (str, optional): Maximum close price. Default is '39.7'.
            theta_gte (str, optional): Minimum theta. Default is '-14.44'.
            theta_lte (str, optional): Maximum theta. Default is '-6.52'.
            impl_vol_gte (str, optional): Minimum implied volatility. Default is '78.87'.
            impl_vol_lte (str, optional): Maximum implied volatility. Default is '140.57'.
            additional_rules (Dict[str, Any], optional): Additional custom rules to include in the payload. Default is None.

        Returns:
            OptionScreenerResults: Results of the options screener.

        Example:
            results = await options_screener(
                exp_gte='30',
                exp_lte='60',
                oi_gte='5000',
                oi_lte='10000'
            )
        """
        payload = {
                "filter": {
                    "options.screener.rule.expireDate": f"gte={exp_gte}&lte={exp_lte}"
                },
                "page": {"fetchSize": 200}
            }

        if oi_gte is not None and oi_lte is not None:
            payload["filter"]["options.screener.rule.openInterest"] = f"gte={oi_gte}&lte={oi_lte}"
        if cr_lte is not None:
            payload["filter"]["options.screener.rule.changeRatio"] = f"lte={self.to_decimal(cr_lte)}"
        if vol_gte is not None and vol_lte is not None:
            payload["filter"]["options.screener.rule.volume"] = f"gte={vol_gte}&lte={vol_lte}"
        if iv_percentile_gte is not None and iv_percentile_lte is not None:
            payload["filter"]["options.screener.rule.ivPercent"] = f"gte={self.to_decimal(iv_percentile_gte)}&lte={self.to_decimal(iv_percentile_lte)}"
        if hv_gte is not None and hv_lte is not None:
            payload["filter"]["options.screener.rule.hisVolatility"] = f"gte={hv_gte}&lte={hv_lte}"
        if delta_gte is not None and delta_lte is not None:
            payload["filter"]["options.screener.rule.delta"] = f"gte={self.to_decimal(delta_gte)}&lte={self.to_decimal(delta_lte)}"
        if ticker_iv_gte is not None and ticker_iv_lte is not None:
            payload["filter"]["options.screener.rule.tickerImplVol"] = f"gte={self.to_decimal(ticker_iv_gte)}&lte={self.to_decimal(ticker_iv_lte)}"
        if pulse_gte is not None and pulse_lte is not None:
            payload["filter"]["options.screener.rule.pulseIndex"] = f"gte={self.to_decimal(pulse_gte)}&lte={self.to_decimal(pulse_lte)}"
        if avg30_vol_gte is not None and avg30_vol_lte is not None:
            payload["filter"]["options.screener.rule.avg30Volume"] = f"gte={avg30_vol_gte}&lte={avg30_vol_lte}"
        if total_vol_gte is not None and total_vol_lte is not None:
            payload["filter"]["options.screener.rule.totalVolume"] = f"gte={total_vol_gte}&lte={total_vol_lte}"
        if total_oi_gte is not None and total_oi_lte is not None:
            payload["filter"]["options.screener.rule.totalOpenInterest"] = f"gte={total_oi_gte}&lte={total_oi_lte}"
        if avg30_oi_gte is not None and avg30_oi_lte is not None:
            payload["filter"]["options.screener.rule.avg30OpenInterest"] = f"gte={avg30_oi_gte}&lte={avg30_oi_lte}"
        if bid_gte is not None and bid_lte is not None:
            payload["filter"]["options.screener.rule.bid"] = f"gte={bid_gte}&lte={bid_lte}"
        if change_ratio_gte is not None and change_ratio_lte is not None:
            payload["filter"]["options.screener.rule.changeRatio"] = f"gte={self.to_decimal(change_ratio_gte)}&lte={self.to_decimal(change_ratio_lte)}"
        if ask_gte is not None and ask_lte is not None:
            payload["filter"]["options.screener.rule.ask"] = f"gte={ask_gte}&lte={ask_lte}"
        if close_gte is not None and close_lte is not None:
            payload["filter"]["options.screener.rule.close"] = f"gte={close_gte}&lte={close_lte}"
        if theta_gte is not None and theta_lte is not None:
            payload["filter"]["options.screener.rule.theta"] = f"gte={self.to_decimal(theta_gte)}&lte={self.to_decimal(theta_lte)}"
        if impl_vol_gte is not None and impl_vol_lte is not None:
            payload["filter"]["options.screener.rule.implVol"] = f"gte={self.to_decimal(impl_vol_gte)}&lte={self.to_decimal(impl_vol_lte)}"
        if additional_rules:
            payload["filter"].update(additional_rules)

        endpoint = "https://quotes-gw.webullfintech.com/api/wlas/option/screener/query"

        data = await self.post_data(endpoint=endpoint, payload=payload)
        data = data['datas'] if 'datas' in data else None
        if data is not None:
            return OptionScreenerResults(data)
        else:
            return "No results found."


