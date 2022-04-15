
# print welcome to test button feature
import string


def write_slogan():
   print('Welcome to the application!')

# find a company's SEC report from ticker
def hyperlink(CIK):
    url = 'https://www.sec.gov/edgar/browse/?CIK=' + CIK
    webbrowser.open_new_tab(url)

# get typed user input
def user_input():
    global input
    global string
    s = input.get().lower()
    print(s)
    return s

# read ticker to cik file
# refer to link https://www.sec.gov/files/company_tickers.json