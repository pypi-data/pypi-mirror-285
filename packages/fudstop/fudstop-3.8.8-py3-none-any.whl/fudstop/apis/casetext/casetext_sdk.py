import httpx
from fudstop.apis.polygonio.polygon_database import PolygonDatabase
import pandas as pd
import random
import asyncio
from datetime import datetime, timezone
class CasetextSDK:
    def __init__(self):
        self.db = PolygonDatabase(host='localhost', database='law')


    async def slug_generator(self, db):
        try:
            query = "SELECT slug FROM slugs where court = 'txsct'"
            results = await db.fetch(query)
            
            # Extract slugs from the results
            slugs = [result['slug'] for result in results]
            
            # Generator to yield 5 slugs at a time randomly
            while slugs:
                yield random.sample(slugs, min(25, len(slugs)))
        except Exception as e:
            print(e)


    async def title_generator(self, db):
        try:
            query = "SELECT title FROM slugs where court = 'txsct'"
            results = await db.fetch(query)
            
            # Extract slugs from the results
            slugs = [result['slug'] for result in results]
            
            # Generator to yield 5 slugs at a time randomly
            while slugs:
                yield random.sample(slugs, min(25, len(slugs)))
        except Exception as e:
            print(e)



    async def fetch_case(self, slug):
        try:
            async with httpx.AsyncClient() as client:
                data = await client.get(f"https://casetext.com/api/search-api/doc/{slug}")

                return data.json()
        except Exception as e:
            print(e)



    async def get_case_details(self, db):
        try:
            await db.connect()
            async for slugs in self.slug_generator(db):

        
                tasks = [self.fetch_case(slug) for slug in slugs]

                slugs = await asyncio.gather(*tasks)

                slug = [i.get('slug') for i in slugs]
                type = [i.get('type') for i in slugs]
                title = [i.get('title') for i in slugs]
                longTitle = [i.get('longTitle') for i in slugs]
                try:

                    decideDate = [datetime.fromtimestamp(i.get('decideDate'), timezone.utc).strftime('%Y-%m-%d') if i.get('decideDate') else None for i in slugs]
                except Exception as e:
                    decideDate = ''
                citation = [i.get('citation') for i in slugs]
                citations = [', '.join(i.get('citations', [])) if isinstance(i.get('citations', []), list) else '' for i in slugs],
                citationSuffix = [i.get('citationSuffix') for i in slugs]
                docket = [i.get('docket') for i in slugs]
                jurisdictionCode = [i.get('jurisdictionCode') for i in slugs]
                jurisdiction = [i.get('jurisdiction') for i in slugs]
                # Assuming 'slugs' is your data list
                published = [str(i.get('published')) for i in slugs]
                publishedStrict = [str(i.get('publishedStrict')) for i in slugs]

                heatmap = [i.get('heatmap') for i in slugs]#NO

                heat_cite = [item for sublist in heatmap for item in sublist]
                heat_cite = [i.get('cite') for i in heat_cite]
                holdings = [i.get('holdings') for i in slugs]

                holdings = [item for sublist in holdings for item in sublist] #NO

                holdings_text = [i.get('text') for i in holdings]
                holdings_id = [i.get('sourceId') for i in holdings]
                holdings_citation = [i.get('citation') for i in holdings]
                holdings_title = [i.get('title') for i in holdings]



                analyses = [i.get('analyses') for i in slugs]#NO
                analyses_total = [i.get('total') for i in analyses]
                analyses_rows = [i.get('rows') for i in analyses]
                analyses_rows = [item for sublist in analyses_rows for item in sublist]
                analyses_slug= [i.get('slug') for i in analyses_rows]
                analyses_casename= [i.get('caseName') for i in analyses_rows]
                analyses_description= [i.get('description') for i in analyses_rows]
                analyses_type = [i.get('type') for i in analyses_rows]

                
                briefs = [i.get('briefs') for i in slugs]#NO
                briefs_total = [i.get('total') for i in briefs]
                briefs_rows = [i.get('rows') for i in briefs]#NO
                briefs_rows = [item for sublist in briefs_rows for item in sublist]#NO

                briefs_slug= [i.get('slug') for i in briefs_rows]
                briefs_casename= [i.get('caseName') for i in briefs_rows]
                briefs_description= [i.get('description') for i in briefs_rows]
                briefs_type = [i.get('type') for i in briefs_rows]



                citator = [i.get('citator') for i in slugs]#NO
                citator = [item for sublist in citator for item in sublist]

                citator_id = [i.get('paginationId') for i in citator]
                citator_type = [i.get('type') for i in citator]
                citator_suffix = [i.get('suffix') for i in citator]
                citatorAll = [i.get('citatorAll') for i in slugs]
                opinionsBelow = [i.get('opinionsBelow') for i in slugs]# NO
                opinionsBelow = [item for sublist in opinionsBelow for item in sublist] # NO
                try:
                    for i in opinionsBelow[0]:
                        print(i)
                except Exception as e:
                    print(e)
                paginations = [i.get('paginations') for i in slugs] #NO

                paginations = [item for sublist in paginations for item in sublist]
                pagination = [i.get('paginationId') for i in paginations]
                pagination_type = [i.get('type') for i in paginations]
                pagination_suffix = [i.get('suffix') for i in paginations]
                
                keyPassages = [i.get('keyPassages') for i in slugs] #NO

                keyPassages = [item for sublist in keyPassages for item in sublist]
                key_id = [i.get('id') for i in keyPassages]
                cite_count = [str(i.get('citeCount')) for i in keyPassages]
                key_quote = [i.get('quote') for i in keyPassages]
                next_restrict = [i.get('nextRestriction') for i in keyPassages]
                prev_restrict = [i.get('previousRestriction') for i in keyPassages]
                passage_type = [i.get('passageType') for i in keyPassages]
                deindexed = [str(i.get('deindexed')) for i in slugs]
                outcomeSentences = [','.join(i.get('outcomeSentences')) for i in slugs]
            

                # Function to extend lists to the max_length
                def extend_list(lst, length, fill_value=None):
                    return lst + [fill_value] * (length - len(lst))
                # Ensure all data are lists
                data_dict = {
                    'slug': slug,
                    'type': type,
                    'title': title,
                    'long_title': longTitle,
                    'decide_date': decideDate,
                    'citation': citation,
                    'citations': [', '.join(c) if isinstance(c, list) else c for c in citations],
                    'citation_suffix': citationSuffix,
                    'docket': docket,
                    'jurisdiction_code': jurisdictionCode,
                    'jurisdiction': jurisdiction,
                    'published': published,
                    'strict': publishedStrict,
                    'heat_cite': heat_cite,
                    'holdings_text': holdings_text,
                    'holdings_id': holdings_id,
                    'holdings_citation': holdings_citation,
                    'holdings_title': holdings_title,
                    'analyses_total': analyses_total,
                    'analyses_slug': analyses_slug,
                    'analyses_casename': analyses_casename,
                    'analyses_description': analyses_description,
                    'analyses_type': analyses_type,
                    'briefs_total': briefs_total,
                    'briefs_slug': briefs_slug,
                    'briefs_casename': briefs_casename,
                    'briefs_description': briefs_description,
                    'briefs_type': briefs_type,
                    'citator_id': citator_id,
                    'citator_type': citator_type,
                    'citator_suffix': citator_suffix,
                    'pagination_id': pagination,
                    'pagination_type': pagination_type,
                    'pagination_suffix': pagination_suffix,
                    'passage_id': key_id,
                    'passage_cite_count': cite_count,
                    'key_quote': key_quote,
                    'next_restrict': next_restrict,
                    'prev_restrict': prev_restrict,
                    'passage_type': passage_type,
                    'deindexed': deindexed,
                    'outcome_sentences': outcomeSentences
                }

                # Find the maximum length of the lists
                max_length = max(len(v) for v in data_dict.values())

                # Function to extend lists to the max_length
                def extend_list(lst, length, fill_value=None):
                    if not isinstance(lst, list):
                        lst = [lst]
                    return lst + [fill_value] * (length - len(lst))

                # Extend all lists in the dictionary
                for key in data_dict:
                    data_dict[key] = extend_list(data_dict[key], max_length)

                # Create DataFrame
                df = pd.DataFrame(data_dict)

                # Print DataFrame to check it
                df = df.dropna(how='all')

                await db.batch_insert_dataframe(df, table_name='caselaw', unique_columns='outcome_sentences')
        except Exception as e:
            print(e)


    async def parallell(self, query, db):
        async for titles in self.title_generator(self.db):

            print(titles)



        async with httpx.AsyncClient() as client:
            data = await client.get(f"https://parallelsearch.casetext.com/__search/unified?q={query}&page=1&sort=relevance&type=case")

            data = data.json()

            results = data.get('results')

            case = results.get('case')

            rows = case.get('rows')

            citation_count = [i.get('citationCount') for i in rows]
            citation_string = [i.get('citationString') for i in rows]
            slug = [i.get('slug') for i in rows]
            title = [i.get('title') for i in rows]
            paragraphs = [i.get('paragraphs') for i in rows]
            pg_rows = [i.get('rows') for i in paragraphs]
            pg_rows = [item for sublist in pg_rows for item in sublist]
            page_text = [i.get('text') for i in pg_rows]
            page_num = [i.get('page') for i in pg_rows]
            pgraph_number = [i.get('paragraphNumber') for i in pg_rows]
            summaries = [i.get('summaries') for i in rows]
            summary_rows = [i.get('rows') for i in summaries]
            summary_rows = [item for sublist in summary_rows for item in sublist]
            summary_slug = [i.get('slug') for i in summary_rows]
            summary_text = [i.get('text') for i in summary_rows]
            summary_title = [i.get('title') for i in summary_rows]
            summary_citation = [i.get('citationString') for i in summary_rows]
            summary_count = [i.get('citationCount') for i in summary_rows]

            max_length = max(len(citation_count), len(citation_string), len(slug), len(title), len(page_text), len(page_num), len(pgraph_number))



            # Function to pad lists
            def pad_list(lst, length, pad_value=None):
                return lst + [pad_value] * (length - len(lst))

            # Pad all lists to the maximum length
            citation_count = pad_list(citation_count, max_length)
            citation_string = pad_list(citation_string, max_length)
            slug = pad_list(slug, max_length)
            title = pad_list(title, max_length)
            page_text = pad_list(page_text, max_length)
            page_num = pad_list(page_num, max_length)
            pgraph_number = pad_list(pgraph_number, max_length)
            summary_slug = pad_list(summary_slug, max_length)
            summary_text = pad_list(summary_text, max_length)
            summary_citation = pad_list(summary_citation, max_length)
            summary_count = pad_list(summary_count, max_length)
            summary_title = pad_list(summary_title, max_length)
            # Create dictionary
            data_dict = { 
                'citation_count': citation_count,
                'citation_string': citation_string,
                'slug': slug,
                'title': title,
                'page_text': page_text,
                'page_num': page_num,
                'pgraph_number': pgraph_number,
                'summary_slug': summary_slug,
                'summary_text': summary_text,
                'summary_title': summary_title,
                'summary_citation': summary_citation,
                'summary_count': summary_count,
            }

            # Create DataFrame
            df = pd.DataFrame(data_dict)

            # Print DataFrame
            df = df.dropna()
            print(df)

            await db.batch_insert_dataframe(df, table_name='cases', unique_columns='slug')
            return df
        

    async def slug_generator(self, db):
        try:
            query = "SELECT slug FROM slugs where court = 'txsct'"
            results = await db.fetch(query)
            
            # Extract slugs from the results
            slugs = [result['slug'] for result in results]
            
            # Generator to yield 5 slugs at a time randomly
            while slugs:
                yield random.sample(slugs, min(25, len(slugs)))
        except Exception as e:
            print(e)


    async def title_generator(db):
        try:
            query = "SELECT title FROM slugs where court = 'txsct'"
            results = await db.fetch(query)
            
            # Extract slugs from the results
            slugs = [result['slug'] for result in results]
            
            # Generator to yield 5 slugs at a time randomly
            while slugs:
                yield random.sample(slugs, min(25, len(slugs)))
        except Exception as e:
            print(e)



    async def fetch_case(slug):
        try:
            async with httpx.AsyncClient() as client:
                data = await client.get(f"https://casetext.com/api/search-api/doc/{slug}")

                return data.json()
        except Exception as e:
            print(e)



    async def get_case_details():
        try:
            await db.connect()
            async for slugs in slug_generator(db):

        
                tasks = [fetch_case(slug) for slug in slugs]

                slugs = await asyncio.gather(*tasks)

                slug = [i.get('slug') for i in slugs]
                type = [i.get('type') for i in slugs]
                title = [i.get('title') for i in slugs]
                longTitle = [i.get('longTitle') for i in slugs]
                try:

                    decideDate = [datetime.fromtimestamp(i.get('decideDate'), timezone.utc).strftime('%Y-%m-%d') if i.get('decideDate') else None for i in slugs]
                except Exception as e:
                    decideDate = ''
                citation = [i.get('citation') for i in slugs]
                citations = [', '.join(i.get('citations', [])) if isinstance(i.get('citations', []), list) else '' for i in slugs],
                citationSuffix = [i.get('citationSuffix') for i in slugs]
                docket = [i.get('docket') for i in slugs]
                jurisdictionCode = [i.get('jurisdictionCode') for i in slugs]
                jurisdiction = [i.get('jurisdiction') for i in slugs]
                # Assuming 'slugs' is your data list
                published = [str(i.get('published')) for i in slugs]
                publishedStrict = [str(i.get('publishedStrict')) for i in slugs]

                heatmap = [i.get('heatmap') for i in slugs]#NO

                heat_cite = [item for sublist in heatmap for item in sublist]
                heat_cite = [i.get('cite') for i in heat_cite]
                holdings = [i.get('holdings') for i in slugs]

                holdings = [item for sublist in holdings for item in sublist] #NO

                holdings_text = [i.get('text') for i in holdings]
                holdings_id = [i.get('sourceId') for i in holdings]
                holdings_citation = [i.get('citation') for i in holdings]
                holdings_title = [i.get('title') for i in holdings]



                analyses = [i.get('analyses') for i in slugs]#NO
                analyses_total = [i.get('total') for i in analyses]
                analyses_rows = [i.get('rows') for i in analyses]
                analyses_rows = [item for sublist in analyses_rows for item in sublist]
                analyses_slug= [i.get('slug') for i in analyses_rows]
                analyses_casename= [i.get('caseName') for i in analyses_rows]
                analyses_description= [i.get('description') for i in analyses_rows]
                analyses_type = [i.get('type') for i in analyses_rows]

                
                briefs = [i.get('briefs') for i in slugs]#NO
                briefs_total = [i.get('total') for i in briefs]
                briefs_rows = [i.get('rows') for i in briefs]#NO
                briefs_rows = [item for sublist in briefs_rows for item in sublist]#NO

                briefs_slug= [i.get('slug') for i in briefs_rows]
                briefs_casename= [i.get('caseName') for i in briefs_rows]
                briefs_description= [i.get('description') for i in briefs_rows]
                briefs_type = [i.get('type') for i in briefs_rows]



                citator = [i.get('citator') for i in slugs]#NO
                citator = [item for sublist in citator for item in sublist]

                citator_id = [i.get('paginationId') for i in citator]
                citator_type = [i.get('type') for i in citator]
                citator_suffix = [i.get('suffix') for i in citator]
                citatorAll = [i.get('citatorAll') for i in slugs]
                opinionsBelow = [i.get('opinionsBelow') for i in slugs]# NO
                opinionsBelow = [item for sublist in opinionsBelow for item in sublist] # NO
                try:
                    for i in opinionsBelow[0]:
                        print(i)
                except Exception as e:
                    print(e)
                paginations = [i.get('paginations') for i in slugs] #NO

                paginations = [item for sublist in paginations for item in sublist]
                pagination = [i.get('paginationId') for i in paginations]
                pagination_type = [i.get('type') for i in paginations]
                pagination_suffix = [i.get('suffix') for i in paginations]
                
                keyPassages = [i.get('keyPassages') for i in slugs] #NO

                keyPassages = [item for sublist in keyPassages for item in sublist]
                key_id = [i.get('id') for i in keyPassages]
                cite_count = [str(i.get('citeCount')) for i in keyPassages]
                key_quote = [i.get('quote') for i in keyPassages]
                next_restrict = [i.get('nextRestriction') for i in keyPassages]
                prev_restrict = [i.get('previousRestriction') for i in keyPassages]
                passage_type = [i.get('passageType') for i in keyPassages]
                deindexed = [str(i.get('deindexed')) for i in slugs]
                outcomeSentences = [','.join(i.get('outcomeSentences')) for i in slugs]
            

                # Function to extend lists to the max_length
                def extend_list(lst, length, fill_value=None):
                    return lst + [fill_value] * (length - len(lst))
                # Ensure all data are lists
                data_dict = {
                    'slug': slug,
                    'type': type,
                    'title': title,
                    'long_title': longTitle,
                    'decide_date': decideDate,
                    'citation': citation,
                    'citations': [', '.join(c) if isinstance(c, list) else c for c in citations],
                    'citation_suffix': citationSuffix,
                    'docket': docket,
                    'jurisdiction_code': jurisdictionCode,
                    'jurisdiction': jurisdiction,
                    'published': published,
                    'strict': publishedStrict,
                    'heat_cite': heat_cite,
                    'holdings_text': holdings_text,
                    'holdings_id': holdings_id,
                    'holdings_citation': holdings_citation,
                    'holdings_title': holdings_title,
                    'analyses_total': analyses_total,
                    'analyses_slug': analyses_slug,
                    'analyses_casename': analyses_casename,
                    'analyses_description': analyses_description,
                    'analyses_type': analyses_type,
                    'briefs_total': briefs_total,
                    'briefs_slug': briefs_slug,
                    'briefs_casename': briefs_casename,
                    'briefs_description': briefs_description,
                    'briefs_type': briefs_type,
                    'citator_id': citator_id,
                    'citator_type': citator_type,
                    'citator_suffix': citator_suffix,
                    'pagination_id': pagination,
                    'pagination_type': pagination_type,
                    'pagination_suffix': pagination_suffix,
                    'passage_id': key_id,
                    'passage_cite_count': cite_count,
                    'key_quote': key_quote,
                    'next_restrict': next_restrict,
                    'prev_restrict': prev_restrict,
                    'passage_type': passage_type,
                    'deindexed': deindexed,
                    'outcome_sentences': outcomeSentences
                }

                # Find the maximum length of the lists
                max_length = max(len(v) for v in data_dict.values())

                # Function to extend lists to the max_length
                def extend_list(lst, length, fill_value=None):
                    if not isinstance(lst, list):
                        lst = [lst]
                    return lst + [fill_value] * (length - len(lst))

                # Extend all lists in the dictionary
                for key in data_dict:
                    data_dict[key] = extend_list(data_dict[key], max_length)

                # Create DataFrame
                df = pd.DataFrame(data_dict)

                # Print DataFrame to check it
                df = df.dropna(how='all')

                await db.batch_insert_dataframe(df, table_name='caselaw', unique_columns='outcome_sentences')
        except Exception as e:
            print(e)