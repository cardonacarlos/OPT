import tkinter as tk
import webbrowser
import requests
import pandas as pd
import numpy as np
import json
import math

#makes the frame
root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

#hello button function
def write_slogan():
    print("Welcome to the application!")

#button to quit the app
quitbutton = tk.Button(frame,
                 text="Quit",
                 fg="red",
                 command=quit)
quitbutton.pack(side=tk.LEFT)
slogan = tk.Button(frame,
                   text="Hello",
                   command=write_slogan)
slogan.pack(side=tk.LEFT)

#function to find a company's SEC report from ticker
def hyperlink():
    url = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm'
    webbrowser.register('chrome',
                        None,
                        webbrowser.BackgroundBrowser(
                            "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open_new(url)

#SEC filing launcher button on frame
webpage = tk.Button(frame,
                    text="Report",
                    command=hyperlink)
webpage.pack(side=tk.LEFT)

#function that obtains user input
def user_input():
    global input
    global string
    string = input.get().lower()
    print(string)
    return string

#input button (ticker)
input = tk.Entry(root)
input.pack(side=tk.BOTTOM)
input.focus_set()
inputbutton = tk.Button(root, text='Get Input', command=user_input)
inputbutton.pack(side=tk.LEFT)

# Reads ticker to cik file
tick = pd.read_csv("ticker.txt", sep="\t")


# function that converts ticker to cik
def tick_to_cik(ticker):
    for i in range(len(tick['Ticker'])):
        if ticker == tick['Ticker'].iloc[i]:
            return str(tick['CIK'].iloc[i]).zfill(10)

#list of items that we want to observe
items = """
Assets
CommonStockSharesAuthorized
CommonStockSharesIssued
CommonStockSharesOutstanding
CommonStockDividendsPerShareDeclared
CostOfGoodsAndServicesSold
Dividends
EarningsPerShareDiluted
Liabilities
LiabilitiesAndStockholdersEquity
LongTermDebt
LongTermDebtCurrent
LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive
OperatingExpenses
OperatingIncomeLoss
PreferredStockSharesAuthorized
Revenues
StockholdersEquity
WeightedAverageNumberOfSharesOutstandingBasic
NetIncomeLoss
"""
items = items.split()
string = input.get()


# function that accesses SEC Edgar API on command and returns facts
def company_facts():
    #from inputted string obtain request the sec json page
    response = requests.get("https://data.sec.gov/api/xbrl/companyfacts/CIK"  + tick_to_cik(string) + '.json').text
    data = json.loads(response)
    metric_dict = {}
    for key, val in data['facts']['us-gaap'].items():
        date = max(ten_k['filed'])
        ten_k = ten_k[(ten_k['filed'] == date) & (ten_k['form'] == '10-K') & (ten_k['frame'].isna())]
        unit_df = pd.DataFrame()
        for unit, unit_val in val['units'].items():
            val_data = val['units'][unit]
            val_data_df = pd.DataFrame(unit_val)
            val_data_df['unit'] = unit
            unit_df = unit_df.append(val_data_df)
            metric_dict[key] = unit_df

    for item in items:
        metric = metric_dict[item]
        ten_k = metric[metric['form'] == '10-K']

        #if the value for the requested metric is not null, then print
        #else find the latest metric for it available
        if ten_k['val'].empty:
            ten_k = metric
            date = max(ten_k['filed'])
            ten_k = ten_k[(ten_k['filed']==date)]
            print(item + ": Value: ")
            print(ten_k.iloc[0]['val'])

        else:
            print(item + ": Value: ")
            print(ten_k.iloc[0]['val'])


def testprint():
    print(tick_to_cik(string))

#button to retrieve financial information
financial_info = tk.Button(frame,
                          text="Retrieve Financial Information",
                          command=company_facts
                          )
financial_info.pack(side=tk.LEFT)


#
# response = requests.get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json').text
#
#
# data = json.loads(response)




# print(tick)

root.mainloop()


