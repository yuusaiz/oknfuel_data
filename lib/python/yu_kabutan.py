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

class yu_kabutan(yu.web):
  def __init__(self):
    super().__init__()

  def login_kabutan(self, uname, passwd):
    #session = requests.session()
    url="https://account.kabutan.jp/login"
    #html = urllib.request.urlopen(url).read()
    res = self.session.get(url)
    html = res.content
    soup = BeautifulSoup(html,"html.parser")
    input_email = soup.select("#session_email")
    input_passwd = soup.select("#session_password")
    authenticity_token = soup.find('input', attrs={'name':'authenticity_token', 'type':'hidden'})
    #print("token")
    #print(authenticity_token['value'])
    #print("token end")
    # ログイン
    login_info = {
      "session[email]":uname,
      "session[password]":passwd,
      "authenticity_token":authenticity_token['value'],
      "session[remember_me]":"0"
    }
    # action
    url_login = url
    res = self.session.post(url_login, data=login_info)
    res.raise_for_status()
    #print(res.text)
    if "/logout" in res.text:
      #print("ログイン成功")
      return True
    return False

  def set_target_code(self, code):
    self.code = str(code)
    url = "https://kabutan.jp/stock/finance?code=" + str(code)
    res = self.session.get(url)
    self.cur_html = res.content
    self.soup = BeautifulSoup(self.cur_html,"html.parser")

  def get_quarter_settlement(self):
    self.name=""
    self.quarter_settlement = {}
    self.quarter_settlement['keijo'] = [] 
    self.quarter_settlement['uriage'] = [] 
    self.quarter_settlement['eigyo'] = [] 
    self.quarter_settlement['saishu'] = [] 
    self.quarter_settlement['hitokabueki'] = [] 
    self.quarter_settlement['haito'] = [] 
    #self.quarter_settlement['keijo'] = pd.Series()
    divs=self.soup.find('div',{'class':'si_i1_1'})
    if divs is not None:      
      m=re.search(r'\d+([\s\S]+?)\n', divs.text)
      self.name=m.group(1)
    divs = self.soup.find('div',{'class':'fin_q_t0_d fin_q_t1_d'})
    if divs is not None:      
      for trs in divs.find_all("tr"):
        tds = trs.find_all("td")
        if len(tds)==7 and ('/' in tds[6].text):
          self.quarter_settlement['uriage'].append(yu.util.try_float(tds[0].text.replace(',', '')))
          self.quarter_settlement['eigyo'].append(yu.util.try_float(tds[1].text.replace(',', '')))
          self.quarter_settlement['keijo'].append(yu.util.try_float(tds[2].text.replace(',', '')))
          self.quarter_settlement['saishu'].append(yu.util.try_float(tds[3].text.replace(',', '')))
          self.quarter_settlement['hitokabueki'].append(yu.util.try_Decimal(tds[4].text.replace(',', '')))
          self.quarter_settlement['haito'].append(yu.util.try_Decimal(tds[5].text.replace(',', '')))

  def get_per_history(self):
    self.per_history = {}
    #ashi_list = {"day","wek","mon"}
    ashi_list = {"day","mon"}
    limit = {"day":8, "mon":4} #1年と10年
    for ashi in ashi_list:
      df = pd.DataFrame()
      for i in range(limit[ashi]):
        url = F"https://kabutan.jp/stock/kabuka?code={self.code}&historical=per&ashi={ashi}&page={i+1}"
        df_today,df_tmp = self.get_per_history_in(url)
        if i==0:
          df = pd.concat([df_today, df], axis=0)
        df = pd.concat([df_tmp, df], axis=0)
      df.columns = ["DATE", "PRICE", "PER", "NEWS"]
      df.sort_values("DATE", inplace=True)
      df.reset_index(drop=True, inplace=True)
      #print(df)
      self.per_history[ashi] = df

  def get_per_history_in(self, url):
    res = self.session.get(url)
    html = res.content
    soup = BeautifulSoup(html,"html.parser")

    dftoday = pd.DataFrame()
    tables = soup.find('table', {'class':'stock_kabuka0 w100per'}) or soup.find('table', {'class':'stock_kabuka0'}) 
    for trs in tables.find_all("tr"):
      if (2 <= len(trs)):
        ths = trs.find_all("th")
        date = ths[0].text
        tds = trs.find_all("td")
        if (0 < len(tds)):
          row = pd.Series([date, tds[0].text.replace(",",""), yu.util.try_float(tds[1].text), ""])
          dftoday = dftoday.append(row, ignore_index=True)

    df = pd.DataFrame()
    tables = soup.find('table', {'class':'stock_kabuka_hist w100per'}) or soup.find('table', {'class':'stock_kabuka_hist'})
    for trs in tables.find_all("tr"):
      if (2 <= len(trs)):
        ths = trs.find_all("th")
        date = ths[0].text
        tds = trs.find_all("td")
        if (0 < len(tds)):
          row = pd.Series([date, tds[0].text.replace(",",""), yu.util.try_float(tds[1].text), tds[2].text.replace("\n","")])
          df = df.append(row, ignore_index=True)
    #print(df)
    return dftoday,df

  def get_reit_code_list(self):
    url="http://yahoo.japan-reit.com/list/rimawari/"
    html = urllib.request.urlopen(url).read()
    print (url)
    df = pd.DataFrame()
    soup = BeautifulSoup(html,"html.parser")
    tbody=soup.select('.simple > tbody:nth-child(2)')
    for trs in tbody[0].find_all("tr"):
      tds = trs.find_all("td")
      if (0 < len(tds)):
        row = pd.Series([tds[0].renderContents().decode('utf-8'), tds[1].get_text(strip=True)])
        df = df.append(row, ignore_index=True)

    df.columns = ["Code","Name"]
    #print(df)
    return(df)
    
  def get_tse_code_list(self):
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    res = urllib.request.urlopen(url)
    #res = res.read().decode('shift_jisx0213')
    #res = res.read().decode('cp932')
    xls = pd.ExcelFile(res)
    df = xls.parse(xls.sheet_names[0])
    #df = df.rename(columns={'<TICKER>':'TICKER', '<DTYYYYMMDD>':'DTYYYYMMDD', '<TIME>':'TIME', '<OPEN>':'OPEN', '<HIGH>':'HIGH', '<LOW>':'LOW', '<CLOSE>':'CLOSE', '<VOL>':'VOL'})
    #df["DTYYYYMMDD"] = df["DTYYYYMMDD"].astype(str)
    #df["TIME"] = df["TIME"].map("{:06d}".format)
    ##df["DATETIME"]=pd.to_datetime(df["DTYYYYMMDD"]+df["TIME"], format='%Y%m%d%H%M%S')
    #df.insert(0,"DATETIME", pd.to_datetime(df["DTYYYYMMDD"]+df["TIME"], format='%Y%m%d%H%M%S'))
    #df=df.drop({"DTYYYYMMDD","TIME","VOL"}, axis=1)
    #df.reset_index(drop=True, inplace=True)
    
    return df


class yu_kabutan_test(unittest.TestCase):
  def test1(self):
    self.yu = yu_kabutan()
    f = open('u.txt', 'r', encoding="ascii")
    u = f.read().replace('\n','')
    f.close()
    f = open('p.txt', 'r', encoding="ascii")
    p = f.read().replace('\n','')
    f.close()
    print(u)
    print(p)
    self.assertEqual(True, self.yu.login_kabutan(u, p))

    self.yu.set_target_code("9984")
    #四半期決算
    self.yu.get_quarter_settlement()
    self.assertEqual(2, self.yu.quarter_settlement['uriage'].index(1507507) - self.yu.quarter_settlement['uriage'].index(1450055))
    self.assertEqual(6, self.yu.quarter_settlement['uriage'].index(1337638) - self.yu.quarter_settlement['uriage'].index(2381070))
    self.assertEqual(1, self.yu.quarter_settlement['keijo'].index(833047) - self.yu.quarter_settlement['eigyo'].index(-1351669))
    print(F"name is {self.yu.name}")

    #PER推移
    self.yu.get_per_history()
    print(self.yu.per_history)
    self.assertEqual(240, len(self.yu.per_history['day']))
    #self.assertEqual(0, len(self.yu.per_history['wek']))
    self.assertTrue(100 < len(self.yu.per_history['mon']))

  def test_reit(self):
    self.yu = yu_kabutan()
    df = self.yu.get_reit_code_list()
    self.assertTrue(True)

  def test_tse(self):
    self.yu = yu_kabutan()
    #df = self.yu.get_tse_code_list()
    #print(df)


if __name__ == "__main__":
  unittest.main()
