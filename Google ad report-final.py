#!/usr/bin/env python
# coding: utf-8

from imap_tools import MailBox, AND
import traceback
import datetime
from selenium import webdriver
import os,shutil
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd

def timeit(method):
    import time
    def timed(*args,**kwargs):
        ts = time.time()
        result = method(*args,**kwargs)
        te = time.time()
        print(f'{method.__name__} ---> {te-ts:.2f} seconds')
        return result
    return timed


class read_mail():
    def __init__(self,email,password):
        self.email         = email
        self.password      = password
        self.imap          = 'imap.gmail.com'
        self.folder        = 'INBOX'
        self.search        = 'Your Google Ads report is ready: ad_report'
        self.archive_path  = f'./archive/'
        self.download_path = os.getcwd()
        if not os.path.exists(self.archive_path):
            os.mkdir(self.archive_path)
        if os.listdir(self.download_path):
            for f in os.listdir(self.download_path):
                if f.endswith('.csv'):
                    shutil.move( f'{self.download_path}/{f}', f'{self.archive_path}/{datetime.datetime.now().strftime("%m-%d-%Y")}_{f}')
                else:
                    pass
    @timeit
    def fetch_link(self):
        with MailBox(self.imap).login(self.email, self.password, initial_folder=self.folder) as mailbox:
            try:
                msg_uid = [msg for msg in mailbox.fetch(AND(subject=self.search)) if msg.date.date() == datetime.date.today()]
                link = [x for x in msg_uid[0].text.splitlines() if 'https://ads.google.com' in x][0].strip('<>')
            except IndexError:
                msg_uid = [msg for msg in mailbox.fetch(AND(subject=self.search)) if msg.date.date() == (datetime.date.today()- datetime.timedelta(days = 1))]
                link = [x for x in msg_uid[0].text.splitlines() if 'https://ads.google.com' in x][0].strip('<>')
        return(link)

@timeit
def download_csv(gecko_path,link):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', os.getcwd())
    profile.set_preference("browser.helperApps.neverAsk.openFile", 'text/csv')
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    profile.set_preference('general.warnOnAboutConfig', False)
    profile.update_preferences()
    driver = webdriver.Firefox(firefox_profile=profile,executable_path=gecko_path)

    driver.set_page_load_timeout(10)
    try:
        driver.get(link)
    except TimeoutException:
        driver.quit()
        

@timeit
def read_csv():
    account = ['xxxxx',
                'yyyyy']

    df = pd.read_csv('ad_report.csv',header = 2)
    df = df[df['Account'].isin(account)]
    df.rename(columns= {'Start date':'Date', 'Account': 'Account Name', 'Avg. CPC':'CPC', 'Avg. CPM': 'CPM'},inplace=True)
    df['Platform'] = 'Google Ads'
    df = df[['Date','Account Name','Platform','Currency','Impressions','Clicks','CPC','CTR','CPM','Cost']]

    df.Date = pd.to_datetime(df.Date)
    df = df[df.Date>pd.to_datetime(datetime.date(2020,10,1))]
    df = df.sort_values(by='Date',ascending=True)
    df['Date'] = df['Date'].map(lambda x: x.strftime('%m-%d-%Y'))
    return(df)

@timeit
def push_to_sheets(df,url,cred_filename='ad-report-302608-9159f5eebc9e.json'):
    gc = gspread.service_account(cred_filename)
    sh = gc.open_by_url(url)
    worksheet = sh.get_worksheet(0)

    set_with_dataframe(worksheet, df)

def main():
    email      = 'xxxxx@gmail.com'
    password   = 'xxxxxxxxxxx'
    url        = 'https://docs.google.com/spreadsheets/xxxxxx'
    gecko_path = "geckodriver.exe"
    
    my_inbox   = read_mail(email,password)
    link       = my_inbox.fetch_link()
    download_csv(gecko_path,link)
    df         = read_csv()
    push_to_sheets(df,url)



if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())
    else:
        print('Done!')
