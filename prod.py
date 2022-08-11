from tkinter import *
from tkinter import ttk
import tkinter as tk
from turtle import width
import webbrowser
import requests
import pandas as pd
import json
from datetime import date

# API Access Header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'From': 'lesparrette@me.com' 
}

# Tkinter Frame Setup
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.metric_dict_keys = None
        self.today = date.today()
        self.year = self.today.year
        self.company_name = ""
        self.CIK = ""
        self.listbox_items = StringVar()
        self.selected_metrics = {}
        self.selected_details = {}
        
        # Uses ticker in order to identify company
        self.ticker = StringVar()
        container = tk.Frame(self)
        container.grid(row=0,column=2, sticky="NSEW")
        self.frames = {}
        for F, geometry in zip((start_page, list_page), ("300x100", "1920x720")):
            frame =  F(parent = container, controller = self)
            self.frames[F] = (frame, geometry)       
            frame.grid(row=0, column=0, sticky="NSEW")
        self.show_frame(start_page)
        
    # Input the requested frame and display it
    def show_frame(self, page_name):
        frame, geometry = self.frames[page_name]
        self.geometry(geometry)
        frame.tkraise()
        
    # Update Listbox page items
    def update_list_page(self):
        self.frames[list_page][0].update_lbox()
            
# Welcome Frame
class start_page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Input Ticker Label
        label = tk.Label(self, text="Input Ticker Below")
        label.grid(row=0, column=1, sticky="NSEW")
        
        # Ticker Entry box
        self.get_input = ttk.Entry(self)
        self.get_input.grid(row=1, column=1, sticky="NSEW")
        
        # Get Input Button
        self.input_button = ttk.Button(self, text="Get Input", command=self.user_input)
        self.input_button.grid(row=2, column=1, sticky="NSEW", pady=10)
        
        # Quit Button
        self.quit_button = ttk.Button(controller, text="Quit", command=quit)
        self.quit_button.grid(row=0, column=0, sticky="NW", padx=10)
        

                
    # Get Typed User Input
    def user_input(self):
        print("Retrieving Company Information")
        
        # get entry from get_input Entry button
        s = self.get_input.get()
        
        # set ticker StringVar to ticker
        self.controller.ticker.set(s)
        
        # set CIK number variable using tick_to_cik function
        self.controller.CIK = self.tick_to_cik(self.controller.ticker.get())
        self.company_facts(self.controller.ticker.get())
                
        # change to second page
        App.show_frame(self.controller, list_page)
        print("Get User Input Pressed")
        return s
    
    # Read Ticker and return associcated CIK
    # Refer to link https://www.sec.gov/files/company_tickers.json
    def tick_to_cik(self, ticker):
        url = 'https://www.sec.gov/files/company_tickers.json'
        response = requests.get(url, headers=headers)
        if not response.ok:
            print('Retrying...')
            return tick_to_cick(self, ticker)
        else:
            data = response.json()
            for tick in data.values():
                if tick['ticker'].lower() == ticker.lower():
                    print(tick['title'])
                    self.controller.company_name = tick['title']
                    self.controller.CIK = str(tick['cik_str']).zfill(10)
                    return self.controller.CIK
                
    # Access SEC Edgar API and return company facts
    # Takes ticker input as string
    def company_facts(self, string):
        if string:
            info = string.upper() + " Company Facts\n"
            url = "https://data.sec.gov/api/xbrl/companyfacts/CIK"  + self.tick_to_cik(string) + ".json"
            response = requests.get(url, headers=headers)
            # ensure that connect works
            if not response.ok:
                print('Retry')
                return company_facts(self, string)
            else:
                # load json data
                response = response.text
                data = json.loads(response)

                # global dictionary for wanted metric
                global metric_dict
                metric_dict = {}
                
                global metric_dict_desc
                metric_dict_desc = {}


                for key, val in data['facts']['us-gaap'].items():
                    unit_df = pd.DataFrame()
                    for unit, unit_val in val['units'].items():
                        val_data = val['units'][unit]                        
                        val_data_df = pd.DataFrame(unit_val)
                        
                        # remove metrics without latest year data (deprecated metrics)
                        if (val_data_df.empty == False) and ((max(val_data_df['fy']) == self.controller.year) 
                                                             or (max(val_data_df['fy']) == self.controller.year-1)):
                            val_data_df['unit'] = unit
 
                            # deprecated warning
                            # unit_df = unit_df.append(val_data_df)
                            unit_df = pd.concat([unit_df, val_data_df])
                            metric_dict[key] = unit_df
                            metric_dict_desc[key] = val["description"]
                
                # list of keys
                
                self.controller.metric_dict_keys = [key for key in metric_dict.keys()]
                self.controller.update_list_page()
                      
class list_page(tk.Frame):
    def __init__(self, parent, controller):
        # tk.Frame.__init__(self, parent)
        super().__init__(parent)
        self.controller = controller
        
        
        # Home button
        self.home = ttk.Button(self, text="Home Page",
                            command=self.home_button)
                            #    command=lambda: controller.show_frame(start_page))
        self.home.grid(row=0,column=0, sticky="NW")
        
        
        # Select Info Label
        self.lbl = ttk.Label(self, text = "Select Desired Information")
        self.lbl.grid(row=0,column=0,pady=10)
        
        # Listbox Label
        self.company = tk.Label(self, text=f"{self.controller.company_name}\n\nChoose Items From List",
                                font=100)
        self.company.grid(row=0, column=0, pady=10)
        
        # label = tk.Label(self, text="Choose Items from Listbox")
        # label.grid(row=0, column=0, pady=10)
        
        # SEC Filing Launcher
        webpage = ttk.Button(self,
                             text = "View Report",
                             command=lambda: self.hyperlink(controller.CIK))
        webpage.grid(row=1, column=0, pady=10, sticky="NW")
        
        # Company Information Listbox
        self.lbox = Listbox(self, listvariable=self.controller.metric_dict_keys, selectmode=MULTIPLE,
               width=50, height=20, font=30)
        self.lbox.grid(row=2, column=0, pady=10, sticky="NSEW")
        
        
        # Select All Button
        self.select_button = ttk.Button(self, text='Select All', command=self.select_all)
        self.select_button.grid(row=1,column=0, pady=10)
        
        
        # Print Information Button
        self.print_info = ttk.Button(self, text="Print Selected Information", command=self.lbox_print)
        self.print_info.grid(row=3, column=0, pady=10)
        
        # Print Details Button
        self.print_details = ttk.Button(self, text="Print Selected Details", command=self.lbox_print_details)
        self.print_details.grid(row=4, column=0, pady=10)
        
        # Currently selected listbox items
        self.listbox_selection = []
        
        # Button Click counter
        self.counter = 0
        
        # Printed Info
        self.printed_information = tk.Text(self, font=("Arial", 12), width=50, wrap=WORD)
        self.printed_information.insert(1.0, "Display Values Below")
        self.printed_information.grid(row=2, column=1, pady=10, sticky="N")
        
        # Printed Details
        self.printed_details = tk.Text(self, font=("Arial", 12), width=50, wrap=WORD)
        self.printed_details.insert(1.0, "Display Details Below")
        self.printed_details.grid(row=2, column=2, pady=10, sticky="N")
        
        
    # reset all variables and return to the home screen
    def home_button(self):
        # metric dict keys variable
        self.controller.metric_dict_keys = None
        
        # company name
        self.controller.company_name = ""
        self.controller.CIK = ""
        self.controller.listbox_items = StringVar()
        self.controller.selected_metrics = {}
        
        # Set empty ticker variable
        self.controller.ticker = StringVar()
        self.counter = 0
        
        # Empty listbox
        self.lbox.delete(0, 'end')
        
        # Empty Text
        self.printed_information.delete("1.0", 'end')
        self.printed_details.delete("1.0", "end")
        
        App.show_frame(self.controller, start_page)
               
        
    def select_all(self):
        if self.counter % 2 == 0:
            self.lbox.select_set(0, END)
            self.counter += 1
        else: 
            self.lbox.selection_clear(0, END)
            self.counter += 1
        
    
    def update_lbox(self):
        
        # update company name
        self.company.configure(text=f"{self.controller.company_name}\n\nChoose Items From List")        
        
        # update listbox
        
        self.lbox.delete(0, 'end')
        for item in self.controller.metric_dict_keys:
            self.lbox.insert("end", item)
        # print(self.controller.metric_dict_keys)
    
        
    # find a company's SEC report from ticker
    def hyperlink(self, CIK):
        url = 'https://www.sec.gov/edgar/browse/?CIK=' + CIK + '&owner=exclude'
        webbrowser.open_new_tab(url)
        
    # print selected info from listbox
    def lbox_print(self):
        
        self.controller.selected_metrics = {}
        
        for selection in self.lbox.curselection():
            current = self.lbox.get(selection)
            self.listbox_selection.append(current)
            self.metric_extractor(current)
            
        self.printed_information.delete("1.0", "end")                    
        for key, val in self.controller.selected_metrics.items():
            
            try:
                kv_string = f"{str(key)}: \n" + f"{val:,}\n" + "\n"
                print(kv_string)
                self.printed_information.insert("end", kv_string)
            except:     
                kv_string = f"{str(key)}: \n" + f"{str(val)}\n" + "\n"
                print(kv_string)
                self.printed_information.insert("end", kv_string)
        
    # print selected details from listbox
    def lbox_print_details(self):
        
        self.controller.selected_details = {}
        
        for selection in self.lbox.curselection():    
            current = self.lbox.get(selection)
            self.controller.selected_details[current] = metric_dict_desc[current]
        
        self.printed_details.delete("1.0", "end")                    
        for key, val in self.controller.selected_details.items():
            kv_string = f"{str(key)}: \n" + f"{str(val)}\n" + "\n"
            # print(kv_string)
            self.printed_details.insert("end", kv_string)
        
        
        
        
    # extract listbox selected metric relevant information
    def metric_extractor(self, m):
        
        info = self.controller.ticker.get().upper() + " Company Facts\n"
        
        metric = metric_dict[m]
        ten_k = metric[(metric['form'] == '10-K') & (metric['fp'] == "FY")]                
        latest = ten_k[ten_k['fy']==self.controller.year]
        
        
        try:
            if latest.empty:
                print(f"No {self.controller.year} 10-K")
                print("Checking Previous Year")
                latest = ten_k[ten_k['fy']==(self.controller.year-1)].reset_index(drop=True)
                ten_k = latest
            else:
                print("Using 2022 10-K")
                ten_k = latest

            
            #if the value for the requested metric is not null, then print
            #else find the latest metric for it available
            if ten_k['val'].empty:
                print("Requested Value Column is empty")
                ten_k = metric
                date = max(ten_k['fy'])
                ten_k = ten_k[(ten_k['filed']==date)]
                print(m + ": Value: ")
                # print(ten_k.iloc[0]['val'])
                print("\n")
                
                ten_k['end'] = pd.to_datetime(ten_k['end'])
                
                try:
                    latest_date_index = ten_k['end'].idxmax()
                    print(latest_date_index)
                                
                    # add metric to list of selected metrics
                    self.controller.selected_metrics[m] = ten_k.iloc[latest_date_index]['val']
                except:
                    print("There is no 'end': using last available value")
                    self.controller.selected_metrics[m] = ten_k.iloc[-1]['val']

            else:
                print(m + ": Value: ")
                print(ten_k.iloc[0]['val'])
                print("\n")
                
                # add metric to list of selected metrics
                ten_k['end'] = pd.to_datetime(ten_k['end'])
                
                
                try:
                    latest_date_index = ten_k['end'].idxmax()
                    print(latest_date_index)
                
                    # add metric to list of selected metrics
                    self.controller.selected_metrics[m] = ten_k.iloc[latest_date_index]['val']
                except:
                    print("There is no 'end': using last available value")
                    self.controller.selected_metrics[m] = ten_k.iloc[-1]['val']
        except:
            print("No Valid Value Found")
            self.controller.selected_metrics[m] = "NULL"
        
        key_remove_list = []
        for key, val in self.controller.selected_metrics.items():
            if val == "NULL":
                key_remove_list.append(key)
        
        for k in key_remove_list:
                self.controller.selected_metrics.pop(k, None)
                self.controller.selected_details.pop(k, None)
            
                
        
            
            
        
                
      

app = App()
app.title("One Page Thinking")
app.mainloop()
