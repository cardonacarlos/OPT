import requests
import pandas as pd
import numpy as np
import json


#read ticker to CIK text file
tick = pd.read_csv("ticker.txt", sep="\t")




#function that turns ticker to CIK id
def tick_to_cik(ticker):
    for i in range(len(tick['Ticker'])):
        if ticker == tick['Ticker'].iloc[i]:
            return str(tick['CIK'].iloc[i]).zfill(10)


#Grab data from SEC EDGAR API and return
#response = requests.get("https://data.sec.gov/submissions/CIK"  + tick_to_cik(ticker) + '.json')


#example use case with AAPL
response = requests.get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json')
print(response.status_code)
response = response.text
data = json.loads(response)

metric_dict = {}
for key, val in data['facts']['us-gaap'].items():
    unit_df = pd.DataFrame()
    for unit, unit_val in val['units'].items():
        val_data = val['units'][unit]
        val_data_df = pd.DataFrame(unit_val)
        val_data_df['unit'] = unit
        unit_df = unit_df.append(val_data_df)
        metric_dict[key] = unit_df


