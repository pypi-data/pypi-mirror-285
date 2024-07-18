import aiohttp
import pandas as pd
from fudstop.apis.helpers import format_large_numbers_in_dataframe
class CapitalFlow:
    """
    A class representing capital flow data for a stock.

    Attributes:
        superin (float): The amount of super large inflow formatted with commas.
        superout (float): The amount of super large outflow formatted with commas.
        supernet (float): The amount of super large net flow formatted with commas.
        largein (float): The amount of large inflow formatted with commas.
        largeout (float): The amount of large outflow formatted with commas.
        largenet (float): The amount of large net flow formatted with commas.
        newlargein (float): The amount of new large inflow formatted with commas.
        newlargeout (float): The amount of new large outflow formatted with commas.
        newlargenet (float): The amount of new large net flow formatted with commas.
        newlargeinratio (float): The new large inflow ratio formatted as a percentage with 2 decimal places.
        newlargeoutratio (float): The new large outflow ratio formatted as a percentage with 2 decimal places.
        mediumin (float): The amount of medium inflow formatted with commas.
        mediumout (float): The amount of medium outflow formatted with commas.
        mediumnet (float): The amount of medium net flow formatted with commas.
        mediuminratio (float): The medium inflow ratio formatted as a percentage with 2 decimal places.
        mediumoutratio (float): The medium outflow ratio formatted as a percentage with 2 decimal places.
        smallin (float): The amount of small inflow formatted with commas.
        smallout (float): The amount of small outflow formatted with commas.
        smallnet (float): The amount of small net flow formatted with commas.
        smallinratio (float): The small inflow ratio formatted as a percentage with 2 decimal places.
        smalloutratio (float): The small outflow ratio formatted as a percentage with 2 decimal places.
        majorin (float): The amount of major inflow formatted with commas.
        majorinratio (float): The major inflow ratio formatted as a percentage with 2 decimal places.
        majorout (float): The amount of major outflow formatted with commas.
        majoroutratio (float): The major outflow ratio formatted as a percentage with 2 decimal places.
        majornet (float): The amount of major net flow formatted with commas.
        retailin (float): The amount of retail inflow formatted with commas.
        retailinratio (float): The retail inflow ratio formatted as a percentage with 2 decimal places.
        retailout (float): The amount of retail outflow formatted with commas.
        retailoutratio (float): The retail outflow ratio formatted as a percentage with 2 decimal places.

    Methods:
        async def capital_flow(id: str) -> CapitalFlow:
            Returns an instance of the CapitalFlow class for a given stock ticker ID.
            The data is fetched asynchronously using aiohttp.
    """

    def __init__(self, item, ticker):
        print(item)
        self.superin = float(item['superLargeInflow']) if 'superLargeInflow' in item else None
        self.superout = float(item['superLargeOutflow']) if 'superLargeOutflow' in item else None
        self.supernet = float(item['superLargeNetFlow']) if 'superLargeNetFlow' in item else None
        self.largein = float(item['largeInflow']) if 'largeInflow' in item else None
        self.largeout = float(item['largeOutflow']) if 'largeOutflow' in item else None
        self.largenet = float(item['largeNetFlow']) if 'largeNetFlow' in item else None
        self.newlargein = float(item['newLargeInflow']) if 'newLargeInflow' in item else None
        self.newlargeout = float(item['newLargeOutflow']) if 'newLargeOutflow' in item else None
        self.newlargenet = float(item['newLargeNetFlow']) if 'newLargeNetflow' in item else None
        self.newlargeinratio = round(float(item['newLargeInflowRatio']) * 100, 2) if 'newLargeInflowRatio' in item else None
        self.newlargeoutratio = round(float(item['newLargeOutflowRatio']) * 100, 2) if 'newLargeOutflowRatio' in item else None
        self.mediumin = float(item['mediumInflow']) if 'mediumInflow' in item else None
        self.mediumout = float(item['mediumOutflow']) if 'mediumOutflow' in item else None
        self.mediumnet = float(item['mediumNetFlow']) if 'mediumNetFlow' in item else None
        self.mediuminratio = round(float(item['mediumInflowRatio']) * 100, 2) if 'mediumInflowRatio' in item else None
        self.mediumoutratio = round(float(item['mediumOutflowRatio']) * 100, 2) if 'mediumOutflowRatio' in item else None
        self.smallin = float(item['smallInflow']) if 'smallInflow' in item else None
        self.smallout = float(item['smallOutflow']) if 'smallOutflow' in item else None
        self.smallnet = float(item['smallNetFlow']) if 'smallNetFlow' in item else None
        self.smallinratio = round(float(item['smallInflowRatio']) * 100, 2) if 'smallInflowRatio' in item else None
        self.smalloutratio = round(float(item['smallOutflowRatio']) * 100, 2) if 'smallOutflowRatio' in item else None
        self.majorin = float(item['majorInflow']) if 'majorInflow' in item else None
        self.majorinratio = round(float(item['majorInflowRatio']) * 100, 2) if 'majorInflowRatio' in item else None
        self.majorout = float(item['majorOutflow']) if 'majorOutflow' in item else None
        self.majoroutratio = round(float(item['majorOutflowRatio']) * 100, 2) if 'majorOutflowRatio' in item else None
        self.majornet = float(item['majorNetFlow']) if 'majorNetFlow' in item else None
        self.retailin = float(item['retailInflow']) if 'retailInflow' in item else None
        self.retailinratio = round(float(item['retailInflowRatio']) * 100, 2) if 'retailInflowRatio' in item else None
        self.retailout = float(item['retailOutflow']) if 'retailOutflow' in item else None
        self.retailoutratio = round(float(item['retailOutflowRatio']) * 100, 2) if 'retailOutflowRatio' in item else None


        self.data_dict = {
            'ticker': ticker,
            'superLargeInflow': self.superin,
            'superLargeOutflow': self.superout,
            'superLargeNetFlow': self.supernet,
            'largeInflow': self.largein,
            'largeOutflow': self.largeout,
            'largeNetFlow': self.largenet,
            'newLargeInflow': self.newlargein,
            'newLargeOutflow': self.newlargeout,
            'newLargeNetFlow': self.newlargenet,
            'newLargeInflowRatio': self.newlargeinratio,
            'newLargeOutflowRatio': self.newlargeoutratio,
            'mediumInflow': self.mediumin,
            'mediumOutflow': self.mediumout,
            'mediumNetFlow': self.mediumnet,
            'mediumInflowRatio': self.mediuminratio,
            'mediumOutflowRatio': self.mediumoutratio,
            'smallInflow': self.smallin,
            'smallOutflow': self.smallout,
            'smallNetFlow': self.smallnet,
            'smallInflowRatio': self.smallinratio,
            'smallOutflowRatio': self.smalloutratio,
            'majorInflow': self.majorin,
            'majorInflowRatio': self.majorinratio,
            'majorOutflow': self.majorout,
            'majorOutflowRatio': self.majoroutratio,
            'majorNetFlow': self.majornet,
            'retailInflow': self.retailin,
            'retailInflowRatio': self.retailinratio,
            'retailOutflow': self.retailout,
            'retailOutflowRatio': self.retailoutratio
        }
        self.df = pd.DataFrame(self.data_dict, index=[0])
        


class CapitalFlowHistory:
    """
    A class representing capital flow data for a stock.

    Attributes:
        superin (list): List of super large inflow values.
        superout (list): List of super large outflow values.
        supernet (list): List of super large net flow values.
        largein (list): List of large inflow values.
        largeout (list): List of large outflow values.
        largenet (list): List of large net flow values.
        newlargein (list): List of new large inflow values.
        newlargeout (list): List of new large outflow values.
        newlargenet (list): List of new large net flow values.
        newlargeinratio (list): List of new large inflow ratios as percentages.
        newlargeoutratio (list): List of new large outflow ratios as percentages.
        mediumin (list): List of medium inflow values.
        mediumout (list): List of medium outflow values.
        mediumnet (list): List of medium net flow values.
        mediuminratio (list): List of medium inflow ratios as percentages.
        mediumoutratio (list): List of medium outflow ratios as percentages.
        smallin (list): List of small inflow values.
        smallout (list): List of small outflow values.
        smallnet (list): List of small net flow values.
        smallinratio (list): List of small inflow ratios as percentages.
        smalloutratio (list): List of small outflow ratios as percentages.
        majorin (list): List of major inflow values.
        majorinratio (list): List of major inflow ratios as percentages.
        majorout (list): List of major outflow values.
        majoroutratio (list): List of major outflow ratios as percentages.
        majornet (list): List of major net flow values.
        retailin (list): List of retail inflow values.
        retailinratio (list): List of retail inflow ratios as percentages.
        retailout (list): List of retail outflow values.
        retailoutratio (list): List of retail outflow ratios as percentages.
    """

    def __init__(self, historical, date):
        self.date = date
        self.superin = [float(i.get('superLargeInflow')) if 'superLargeInflow' in i else None for i in historical]
        self.superout = [float(i.get('superLargeOutflow')) if 'superLargeOutflow' in i else None for i in historical]
        self.supernet = [float(i.get('superLargeNetFlow')) if 'superLargeNetFlow' in i else None for i in historical]
        self.largein = [float(i.get('largeInflow')) if 'largeInflow' in i else None for i in historical]
        self.largeout = [float(i.get('largeOutflow')) if 'largeOutflow' in i else None for i in historical]
        self.largenet = [float(i.get('largeNetFlow')) if 'largeNetFlow' in i else None for i in historical]
        self.newlargein = [float(i.get('newLargeInflow')) if 'newLargeInflow' in i else None for i in historical]
        self.newlargeout = [float(i.get('newLargeOutflow')) if 'newLargeOutflow' in i else None for i in historical]
        self.newlargenet = [float(i.get('newLargeNetFlow')) if 'newLargeNetFlow' in i else None for i in historical]
        self.newlargeinratio = [round(float(i.get('newLargeInflowRatio')) * 100, 2) if 'newLargeInflowRatio' in i else None for i in historical]
        self.newlargeoutratio = [round(float(i.get('newLargeOutflowRatio')) * 100, 2) if 'newLargeOutflowRatio' in i else None for i in historical]
        self.mediumin = [float(i.get('mediumInflow')) if 'mediumInflow' in i else None for i in historical]
        self.mediumout = [float(i.get('mediumOutflow')) if 'mediumOutflow' in i else None for i in historical]
        self.mediumnet = [float(i.get('mediumNetFlow')) if 'mediumNetFlow' in i else None for i in historical]
        self.mediuminratio = [round(float(i.get('mediumInflowRatio')) * 100, 2) if 'mediumInflowRatio' in i else None for i in historical]
        self.mediumoutratio = [round(float(i.get('mediumOutflowRatio')) * 100, 2) if 'mediumOutflowRatio' in i else None for i in historical]
        self.smallin = [float(i.get('smallInflow')) if 'smallInflow' in i else None for i in historical]
        self.smallout = [float(i.get('smallOutflow')) if 'smallOutflow' in i else None for i in historical]
        self.smallnet = [float(i.get('smallNetFlow')) if 'smallNetFlow' in i else None for i in historical]
        self.smallinratio = [round(float(i.get('smallInflowRatio')) * 100, 2) if 'smallInflowRatio' in i else None for i in historical]
        self.smalloutratio = [round(float(i.get('smallOutflowRatio')) * 100, 2) if 'smallOutflowRatio' in i else None for i in historical]
        self.majorin = [float(i.get('majorInflow')) if 'majorInflow' in i else None for i in historical]
        self.majorinratio = [round(float(i.get('majorInflowRatio')) * 100, 2) if 'majorInflowRatio' in i else None for i in historical]
        self.majorout = [float(i.get('majorOutflow')) if 'majorOutflow' in i else None for i in historical]
        self.majoroutratio = [round(float(i.get('majorOutflowRatio')) * 100, 2) if 'majorOutflowRatio' in i else None for i in historical]
        self.majornet = [float(i.get('majorNetFlow')) if 'majorNetFlow' in i else None for i in historical]
        self.retailin = [float(i.get('retailInflow')) if 'retailInflow' in i else None for i in historical]
        self.retailinratio = [round(float(i.get('retailInflowRatio')) * 100, 2) if 'retailInflowRatio' in i else None for i in historical]
        self.retailout = [float(i.get('retailOutflow')) if 'retailOutflow' in i else None for i in historical]
        self.retailoutratio = [round(float(i.get('retailOutflowRatio')) * 100, 2) if 'retailOutflowRatio' in i else None for i in historical]


        self.data_dict = {
            'date': self.date,
            'superLargeInflow': self.superin,
            'superLargeOutflow': self.superout,
            'superLargeNetFlow': self.supernet,
            'largeInflow': self.largein,
            'largeOutflow': self.largeout,
            'largeNetFlow': self.largenet,
            'newLargeInflow': self.newlargein,
            'newLargeOutflow': self.newlargeout,
            'newLargeNetFlow': self.newlargenet,
            'newLargeInflowRatio': self.newlargeinratio,
            'newLargeOutflowRatio': self.newlargeoutratio,
            'mediumInflow': self.mediumin,
            'mediumOutflow': self.mediumout,
            'mediumNetFlow': self.mediumnet,
            'mediumInflowRatio': self.mediuminratio,
            'mediumOutflowRatio': self.mediumoutratio,
            'smallInflow': self.smallin,
            'smallOutflow': self.smallout,
            'smallNetFlow': self.smallnet,
            'smallInflowRatio': self.smallinratio,
            'smallOutflowRatio': self.smalloutratio,
            'majorInflow': self.majorin,
            'majorInflowRatio': self.majorinratio,
            'majorOutflow': self.majorout,
            'majorOutflowRatio': self.majoroutratio,
            'majorNetFlow': self.majornet,
            'retailInflow': self.retailin,
            'retailInflowRatio': self.retailinratio,
            'retailOutflow': self.retailout,
            'retailOutflowRatio': self.retailoutratio
        }


        as_dataframe = pd.DataFrame(self.data_dict)
        self.as_dataframe= format_large_numbers_in_dataframe(as_dataframe)