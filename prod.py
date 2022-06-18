from tkinter import *
from tkinter import ttk
import tkinter as tk
import webbrowser
import requests
import pandas as pd
import numpy as np
import json
import math
import re
import os

# header for accessing API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'From': 'ccardona2000@gmail.com' 
}


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # self.app.title("One Page Thinking - Financial Information Application")            
        self.shared_list = [
        "Assets",
        "CommonStockSharesAuthorized",
        "CommonStockSharesIssued",
        "CommonStockSharesOutstanding",
        "CommonStockDividendsPerShareDeclared",
        "CostOfGoodsAndServicesSold",
        "Dividends",
        "EarningsPerShareDiluted",
        "Liabilities",
        "LiabilitiesAndStockholdersEquity",
        "LongTermDebt",
        "LongTermDebtCurrent",
        "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive",
        "OperatingExpenses",
        "OperatingIncomeLoss",
        "PreferredStockSharesAuthorized",
        "Revenues",
        "StockholdersEquity",
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "NetIncomeLoss"
        ]
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (start_page, list_page):
            page_name = F.__name__
            frame =  F(parent = container, controller = self)
            self.frames[page_name] = frame       
            frame.grid(row=0, column=0, stick="nsew")
        self.show_frame("start_page")
    
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
            
class start_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Input Ticker Label
        label = tk.Label(self, text="Input Ticker Below")
        label.pack(side="top", fill="x", pady=10)
        
        # Ticket Entry
        self.ticker = StringVar()
        self.get_input = ttk.Entry(self)
        self.get_input.pack(side=tk.LEFT, anchor=tk.NW)
        self.input_button = ttk.Button(self, text="Get Input", command=self.user_input)
        self.input_button.pack()
        
        # Quit Button
        self.quit_button = ttk.Button(controller, text="Quit", command=controller.quit)
        self.quit_button.pack()
        
        # Switch Frame
        switch_frame = ttk.Button(self, text="Go to Second Page",
                                command=lambda: controller.show_frame("list_page"))
        switch_frame.pack(side="top", fill="x", pady=10)
                
    # get typed user input
    def user_input(self):
        s = self.get_input.get()
        self.ticker.set(s)
        print(s)
        App.show_frame(self, "list_page")
        return s
        
class list_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Listbox Label
        label = tk.Label(self, text="Choose Items from Listbox")
        label.pack(side="top", fill="x", pady=10)
        
        # SEC Filing Launcher
        webpage = ttk.Button(self,
                             text = "Report")
                            #  command = hyperlink)
        webpage.pack(side=tk.LEFT, anchor=tk.NW)
        
    # find a company's SEC report from ticker
    def hyperlink(CIK):
        url = 'https://www.sec.gov/edgar/browse/?CIK=' + CIK
        webbrowser.open_new_tab(url)
    
    # read ticker to cik file
    # refer to link https://www.sec.gov/files/company_tickers.json
    def tick_to_cik(ticker):
        url = 'https://www.sec.gov/files/company_tickers.json'
        response = requests.get(url, headers=headers)
        if not response.ok:
            print('Retrying...')
        else:
            data = response.json()
            for tick in data.values():
                if tick['ticker'].lower() == ticker.lower():
                    print(tick['title'])
                    return str(tick['cik_str']).zfill(10)
                
    # access SEC Edgar API and return facts
    def company_facts(string, items, info, info_label):
        
        if string:
            info = string.upper() + " Company Facts\n"
            url = "https://data.sec.gov/api/xbrl/companyfacts/CIK"  + tick_to_cik(string) + ".json"
        
            response = requests.get(url, headers=headers)
            
            #ensure that connect works
            if not response.ok:
                print('Retry')
            else:
                #load json data
                response = response.text
                data = json.loads(response)

                #dictionary for wanted metric
                global metric_dict
                metric_dict = {}


                for key, val in data['facts']['us-gaap'].items():
                    unit_df = pd.DataFrame()

                    for unit, unit_val in val['units'].items():
                        val_data = val['units'][unit]
                        val_data_df = pd.DataFrame(unit_val)
                        val_data_df['unit'] = unit
                        
                        
                        # deprecated warning
                        # unit_df = unit_df.append(val_data_df)
                        unit_df = pd.concat([unit_df, val_data_df])
                        metric_dict[key] = unit_df
                
                print([key for key in metric_dict.keys()])
                
                
                for item in items:
                    
                    if item in metric_dict:
                        metric = metric_dict[item]
                        ten_k = metric[metric['form'] == '10-K']
                        date = max(ten_k['filed'])
                        ten_k = ten_k[(ten_k['filed'] == date) & (ten_k['form'] == '10-K') & (ten_k['frame'].isna())]

                        #if the value for the requested metric is not null, then print
                        #else find the latest metric for it available
                        if ten_k['val'].empty:
                            ten_k = metric
                            date = max(ten_k['filed'])
                            ten_k = ten_k[(ten_k['filed']==date)]   
                            print(item + ": Value: ")
                            print(ten_k.iloc[0]['val'])
                            info = info + " ".join(re.sub(r"([A-Z])", r" \1", str(item)).split()) + ": " + "{:,}".format(ten_k.iloc[0]['val']) + "\n"
                            info_label.config(text=info)

                        else:
                            print(item + ": Value: ")
                            print(ten_k.iloc[0]['val'])
                            info = info + " ".join(re.sub(r"([A-Z])", r" \1", str(item)).split()) + ": " + "{:,}".format(ten_k.iloc[0]['val']) +"\n"
                            info_label.config(text=info)
            print("\n===================================================")
            print(info)
        else:
            print('No Input')
            
    
                
    

app = App()
app.title("One Page Thinking - Financial Information Application")
app.mainloop()
