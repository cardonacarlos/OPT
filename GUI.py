import tkinter as tk
import webbrowser
import requests
import pandas as pd
import numpy as np
import json
import math
import re
# import pptx
import os
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN


from logic import *


#makes the frame
root = tk.Tk()
frame = tk.Frame(root)
frame.pack()


#button to quit the app
quitbutton = tk.Button(root,
                 text="Quit",
                 fg="red",
                 command=quit)
quitbutton.pack(side=tk.LEFT, anchor=tk.NW)
quitbutton.focus_set()

slogan = tk.Button(root,
                   text="Hello",
                   command=write_slogan)
slogan.pack(side=tk.LEFT, anchor=tk.NW)
slogan.focus_set()

# #function to find a company's SEC report from ticker
# def hyperlink():
#     url = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm'
#     webbrowser.register('chrome',
#                         None,
#                         webbrowser.BackgroundBrowser(
#                             "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
#     webbrowser.get('chrome').open_new(url)

#SEC filing launcher button on frame
webpage = tk.Button(root,
                    text="Report",
                    command=hyperlink)
webpage.pack(side=tk.LEFT, anchor=tk.NW)


#input button (for ticker)
input = tk.Entry(root)
input.pack(side=tk.BOTTOM, anchor=tk.SW)
input.focus_set()
inputbutton = tk.Button(root, text='Get Input', command=user_input)
inputbutton.pack(side=tk.LEFT, anchor=tk.NW)

# # Reads ticker to cik file
# tick = pd.read_csv("ticker.txt", sep="\t")


# # function that converts ticker to cik
# def tick_to_cik(ticker):
#     for i in range(len(tick['Ticker'])):
#         if ticker == tick['Ticker'].iloc[i]:
#             return str(tick['CIK'].iloc[i]).zfill(10)

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

global info
info = ""

info_label = tk.Label(root,
 fg='dark green',
 font=("Arial", 25),
 justify=tk.LEFT
 )
info_label.pack(side=tk.RIGHT)




#button to retrieve financial information
financial_info = tk.Button(root,
                          text="Retrieve Financial Information",
                          command=company_facts
                          )
financial_info.pack(side=tk.LEFT, anchor=tk.NW)




# response = requests.get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json').text




#button to create powerpoint
powerpoint_button = tk.Button(root,
                          text="Create Powerpoint",
                          command=make_powerpoint
                          )
powerpoint_button.pack(side=tk.LEFT, anchor=tk.NW)




root.title("One Page Thinking - Financial Information Application")
root.mainloop()
