import sys
from pathlib import Path
import random
import json
import re
# Add the project directory to the sys.path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import feedparser
import pandas as pd
import asyncio
import datetime
from .models.sec_models import Entries, DocumentParser, FilerInfo
from _asyncpg.asyncpg_sdk import AsyncpgSDK
import httpx
import asyncio
from bs4 import BeautifulSoup
class SECSdk:
    def __init__(self):
        self.inline_filings_url=f"https://www.sec.gov/Archives/edgar/usgaap.rss.xml"
        self.headers = { 
            'User-Agent': 'fudstop AdminContact@fudstop.io',
            "Accept-Encoding": "gzip, deflate",
            'Host': 'www.sec.gov'
        }
        self.base_url = f"https://www.sec.gov"
        self.db = AsyncpgSDK(host='localhost', user='chuck', database='market_data', password='fud', port=5432)
        self.ticker_df = pd.read_csv('files/ciks.csv')
    def get_cik_by_ticker(self, df, ticker):

        row = df[df['ticker'] == ticker]
        if not row.empty:
            return row.iloc[0]['cik']
        else:
            return None
    def get_ticker_by_cik(self, df, cik):
        # Search the DataFrame for the given CIK
        row = df[df['cik'] == cik]
        
        # If a matching row is found, return the ticker symbol
        if not row.empty:
            return row.iloc[0]['ticker']
        
        # If no matching row is found, return None
        else:
            return None
    async def fetch_and_parse_rss(self, url):
        prev_published = None
        while True:
            feed = feedparser.parse(url, request_headers=self.headers)
            new_entries = []

            for entry in feed.entries:
                published_parsed = entry.published_parsed if 'published_parsed' in entry else None
                if prev_published is None or (published_parsed and published_parsed > prev_published):
                    new_entries.append(entry)
            
            if new_entries:
                prev_published = new_entries[0].published_parsed
                print(f"Found {len(new_entries)} new entries at {datetime.datetime.now()}")

                yield Entries(new_entries)
                data = Entries(new_entries)

            
            # Wait before checking the feed again
            await asyncio.sleep(10)  # Check every 60 seconds

    async def fetch_document(self, link):
        """Fetch and parse a single document given its link."""
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(link)
            response.raise_for_status()  # Ensure we got a '200 OK' response
            return response.text

    async def get_filing_content(self):
        """get URL from database - parse further"""

        query = f"""SELECT link from SEC"""

        links = await self.db.fetch(query)

        links = [i['link'] for i in links]

        async with httpx.AsyncClient(headers=self.headers) as client:
            for link in links:
                try:
                    response = await client.get(link)
                    response.raise_for_status()  # Raises exception for 4XX/5XX responses
                    return response.text
                except Exception as e:
                    print(e)

    async def get_document_links(self, html_content):
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Initialize a dictionary to hold your parsed data
        parsed_data = {
            "interactive_data_link": "",
            "document_format_files": [],
            "data_files": [],
            "filer_info": {}
        }

        # Extract the Interactive Data link
        interactive_data_btn = soup.find(id="interactiveDataBtn")
        if interactive_data_btn and interactive_data_btn.has_attr('href'):
            parsed_data["interactive_data_link"] = interactive_data_btn['href']

        # Extract Document Format Files
        for row in soup.select("#formDiv table.tableFile tr:not(:first-child)"):
            cells = row.find_all('td')
            if len(cells) >= 5:
                parsed_data["document_format_files"].append({
                    "seq": cells[0].text.strip(),
                    "description": cells[1].text.strip(),
                    "document_link": cells[2].find('a')['href'] if cells[2].find('a') else "",
                    "type": cells[3].text.strip(),
                    "size": cells[4].text.strip()
                })

        # Extract Data Files (similar approach as Document Format Files)
        # Assuming there's another div with id=formDiv specifically for data files, or adjust the selector as needed

        # Extract Filer Information
        filer_div = soup.find(id="filerDiv")
        if filer_div:
            parsed_data["filer_info"] = {
                "mailing_address": " ".join([span.text for span in filer_div.find_all(class_="mailer")[0].find_all(class_="mailerAddress")]),
                "business_address": " ".join([span.text for span in filer_div.find_all(class_="mailer")[1].find_all(class_="mailerAddress")]),
                "company_name": filer_div.find(class_="companyName").text.strip() if filer_div.find(class_="companyName") else "",
                "cik": filer_div.find("a", href=True).text.strip() if filer_div.find("a", href=True) else "",
                # Add more attributes as needed
            }

        # Display or use the parsed data
        interactive_data_link = parsed_data.get('interactive_data_link')
        document_format_files = DocumentParser(parsed_data.get('document_format_files'))
        data_files = parsed_data.get('data_files')
        filer_info = FilerInfo(parsed_data.get('filer_info'))
        df = document_format_files.as_dataframe
        cik = filer_info.cik
        df['cik'] = cik


        # Map the CIKs in your DataFrame to ticker symbols and create a new 'ticker' column
        
        df['company'] = filer_info.company_name
        ticker = self.get_ticker_by_cik(self.ticker_df, cik)
        df['ticker'] = ticker
        return df
    

    async def parse_sec_filings(self, text):
        documents = []

        # Split the text into documents using the DOCUMENT markers
        document_texts = re.split(r'(?<=</DOCUMENT>)', text)
        
        for doc_text in document_texts:
            if "<DOCUMENT>" in doc_text:
                # Extract fields from each document
                doc_info = {
                    "type": re.search(r'<TYPE>(.*?)\n', doc_text).group(1) if re.search(r'<TYPE>(.*?)\n', doc_text) else None,
                    "sequence": re.search(r'<SEQUENCE>(.*?)\n', doc_text).group(1) if re.search(r'<SEQUENCE>(.*?)\n', doc_text) else None,
                    "filename": re.search(r'<FILENAME>(.*?)\n', doc_text).group(1) if re.search(r'<FILENAME>(.*?)\n', doc_text) else None,
                    "description": re.search(r'<DESCRIPTION>(.*?)\n', doc_text).group(1) if re.search(r'<DESCRIPTION>(.*?)\n', doc_text) else None,
                    "content": None
                }
                
                # Extract and parse the HTML content within <TEXT> tags
                html_content_match = re.search(r'<TEXT>(.*?)</TEXT>', doc_text, re.DOTALL)
                if html_content_match:
                    html_content = html_content_match.group(1)
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Here you could further process the soup object to extract data
                    # For simplicity, we'll just clean and set the HTML content
                    doc_info["content"] = soup.get_text(strip=True)
                
                documents.append(doc_info)
        
        return documents
