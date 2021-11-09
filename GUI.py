import tkinter as tk
import webbrowser
import requests
import pandas as pd
import numpy as np
import json
import math
import re
import pptx
import os
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN

#makes the frame
root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

#hello button function
def write_slogan():
    print("Welcome to the application!")

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

#function to find a company's SEC report from ticker
def hyperlink():
    url = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm'
    webbrowser.register('chrome',
                        None,
                        webbrowser.BackgroundBrowser(
                            "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open_new(url)

#SEC filing launcher button on frame
webpage = tk.Button(root,
                    text="Report",
                    command=hyperlink)
webpage.pack(side=tk.LEFT, anchor=tk.NW)

#function that obtains user input
def user_input():
    global input
    global string
    string = input.get().lower()
    print(string)
    return string

#input button (for ticker)
input = tk.Entry(root)
input.pack(side=tk.BOTTOM, anchor=tk.SW)
input.focus_set()
inputbutton = tk.Button(root, text='Get Input', command=user_input)
inputbutton.pack(side=tk.LEFT, anchor=tk.NW)

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

global info
info = ""

info_label = tk.Label(root,
 fg='dark green',
 font=("Arial", 25),
 justify=tk.LEFT
 )
info_label.pack(side=tk.RIGHT)

# function that accesses SEC Edgar API on command and returns facts
def company_facts():

    #declare global info variable
    global info
    info = string.upper() + " Company Facts\n"

    #url for api
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK"  + tick_to_cik(string) + ".json"


    #header for accessing API
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'From': 'ccardona2000@gmail.com' 
    }

    #api accessing
    response = requests.get(url, headers=headers)

    #ensure that connect works
    if not response.ok:
        print('Retry')
    else:
        #load json data
        response = response.text
        data = json.loads(response)

        #dictionary for wanted metric
        metric_dict = {}


        for key, val in data['facts']['us-gaap'].items():
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
 




#button to retrieve financial information
financial_info = tk.Button(root,
                          text="Retrieve Financial Information",
                          command=company_facts
                          )
financial_info.pack(side=tk.LEFT, anchor=tk.NW)




# response = requests.get('https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json').text




#command that makes powerpoint from financial information
def make_powerpoint():

    #split financial info into array
    split_info = info.split("\n")

    #initialize powerpoint
    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = "Company Facts for " + string.upper()

    #make shape for each info
    shapes = slide.shapes
    left = top = height = Inches(0.5)
    width = Inches(0.7)
    for text in range(len(split_info)):

        #shape configuration
        shape = shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
        )

        #shape filling
        fill = shape.fill 
        fill.solid()
        fill.fore_color.rgb = RGBColor(255,255,255)

        #shape outline
        line = shape.line
        line.color.rgb = RGBColor(0,0,0)

        #shape text
        text_frame = shape.text_frame
        text_frame.word_wrap = True

        p = text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = split_info[text]

        #shape text font
        font = run.font
        font.name = 'Arial Narrow'
        font.size = Pt(6)
        font.color.rgb = RGBColor(0,0,0)
        left = left + width

    pptx_name = string.upper() + ".pptx"
    prs.save(pptx_name)

    #open powerpoint file that was just created

    cwd = os.getcwd()
    path = cwd + "\\" + pptx_name
    os.startfile(path)



#button to create powerpoint
powerpoint_button = tk.Button(root,
                          text="Create Powerpoint",
                          command=make_powerpoint
                          )
powerpoint_button.pack(side=tk.LEFT, anchor=tk.NW)




root.title("One Page Thinking - Financial Information Application")
root.mainloop()
