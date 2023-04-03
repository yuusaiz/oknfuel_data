import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import urllib.request
from io import StringIO
import subprocess
import os
import statistics
import math
from IPython.display import HTML
from bs4 import BeautifulSoup
import sys
import math
import requests
import yu 
import unittest
import re
import threading
import datetime
import unicodedata

class yu_irbank(yu.web):
  def __init__(self):
    super().__init__()

  def set_target_code(self, code):
    self.code = str(code)

  def get_pbr_history(self):
    self.pbr_history = {}
    df = pd.DataFrame()
    url = F"https://irbank.net/{self.code}/pbr?mw=2"
    df = self.get_pbr_history_in(url)
    df.columns = ["DATE", "PRICE", "PER", "PBR"]
    df.sort_values("DATE", inplace=True)
    df.reset_index(drop=True, inplace=True)
    #print(df)
    self.pbr_history['week'] = df

  def get_pbr_history_in(self, url):
    res = self.session.get(url)
    html = res.content
    soup = BeautifulSoup(html,"html.parser")
    #'#tbc > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(11)'
    #'/html/body/div[2]/main/div[2]/div/div/section/div[4]/table/tbody/tr[2]/td[11]'

    df = pd.DataFrame()
    tables = soup.find('table', {'id':'tbc'})
    for trs in tables.find_all("tr"):
      #print(F"trs {len(trs)}")
      if (0 <= len(trs)):
        tds = trs.find_all("td")
        ths = trs.find_all("th")
        #print(F"tds {len(tds)} ths {len(ths)}")
        #print(ths)
        #print(tds)
        if (1 == len(tds)):
          year = tds[0].text
          #print(F"year {year}")
        if (11 <= len(tds)):
          date = year + '/' +  tds[0].text
          row = pd.Series([date, tds[4].text.replace(',',''), yu.util.try_float(tds[9].text), yu.util.try_float(tds[10].text)])
          #df = df.append(row, ignore_index=True)
          df = pd.concat([df, pd.DataFrame(row).transpose()], ignore_index=True)

    return df

class yu_irbank_test(unittest.TestCase):
  def test1(self):
    self.yu = yu_irbank()
    self.yu.set_target_code("7533")
    self.yu.get_pbr_history()
    print(self.yu.pbr_history['week'])

if __name__ == "__main__":
  unittest.main()
