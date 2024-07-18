import pandas as pd

import asyncio
import httpx
from .casetext_models import CaseLawBriefs,CaseLawCases,CaseLawRules
from fudstop.apis.polygonio.polygon_database import PolygonDatabase
import urllib.parse



class CasetextSDK:
    def __init__(self):
        self.db = PolygonDatabase(database='law')

    async def fetch_data(self, url, params=None):
        try:
            async with httpx.AsyncClient() as client:
                data = await client.get(url, params=params)
                if data.status_code == 200:
                    data = data.json()
                    return data
        except Exception as e:
            print(e)


    async def parallel_search_cases(self, query, db=None):
        """Casetext"""
        encoded_query = urllib.parse.quote(query)
        endpoint = f"https://parallelsearch.casetext.com/__search/unified?q={encoded_query}&page=1&sort=relevance&type=case"
        data = await self.fetch_data(endpoint)
        results = data['results']
        case = results['case']
        case_rows = case['rows']
        final = CaseLawCases(case_rows)
        if db is not None:
            await db.connect()
            await db.batch_insert_dataframe(final.as_dataframe, table_name='cases', unique_columns='slug')
        return final.as_dataframe

    async def parallel_search_briefs(self, query, db=None):
        encoded_query = urllib.parse.quote(query)
        endpoint = f"https://parallelsearch.casetext.com/__search/unified?q={encoded_query}&page=1&sort=relevance&type=brief"
        data = await self.fetch_data(endpoint)
        results = data['results']
        case = results['brief']
        case_rows = case['rows']
        final = CaseLawBriefs(case_rows)
        if db is not None:
            await db.connect()
            await db.batch_insert_dataframe(final.as_dataframe, table_name='briefs', unique_columns='slug')
        return final.as_dataframe

    async def parallel_search_rules(self, query, db=None):
        encoded_query = urllib.parse.quote(query)
        endpoint = f"https://parallelsearch.casetext.com/__search/unified?q={encoded_query}&page=1&sort=relevance&type=rule"
        data = await self.fetch_data(endpoint)
        results = data['results']
        case = results['rule']
        case_rows = case['rows']
        final = CaseLawRules(case_rows)
        if db is not None:
            await db.connect()
            await db.batch_insert_dataframe(final.as_dataframe, table_name='rules', unique_columns='slug')
        return final.as_dataframe

    async def parallel_search_statutes(self, query, db=None):
        encoded_query = urllib.parse.quote(query)
        endpoint = f"https://parallelsearch.casetext.com/__search/unified?q={encoded_query}&page=1&sort=relevance&type=statute"
        data = await self.fetch_data(endpoint)
        results = data['results']
        case = results['statute']
        case_rows = case['rows']
        final = CaseLawRules(case_rows)
        if db is not None:
            await db.connect()
            await db.batch_insert_dataframe(final.as_dataframe, table_name='statutes', unique_columns='slug')
        return final.as_dataframe
