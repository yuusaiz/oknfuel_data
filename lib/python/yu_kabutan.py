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
import jpholiday


def read_txt(filename):
  f = open(filename, 'r', encoding="utf8")
  p = f.read()
  f.close()
  return p

class yu_kabutan(yu.web):
  def __init__(self):
    super().__init__()
    self.df_master = pd.DataFrame()
    self.use_local = False

  def use_local_file(self):
    self.use_local = True 

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
    #HTML取得
    if self.use_local:
      self.cur_html = read_txt(f"/home/arle/work/PositionAnalyzer/kabutan/kt{code}.html")
    else:
      th = threading.Thread(target=self.set_target_code_th1, args=[code])
      th.start()
      url = "https://kabutan.jp/stock/finance?code=" + str(code)
      res = self.session.get(url)
      self.cur_html = res.content
      th.join()
    #解析
    self.soup = BeautifulSoup(self.cur_html,"html.parser")
    self.kabuka=0
    self.jikaso=0
    self.per = 0
    self.pbr = 0
    self.haito_rimawari=0
    try:
      #株価
      kabuka = self.soup.find('span',{'class':'kabuka'})
      self.kabuka = kabuka.text.replace(',','').replace('円','')
      if not self.kabuka.isdigit():
        self.kabuka = 0
      #時価総額
      jikaso = self.soup.find('td',{'class':'v_zika2'})
      if '兆' in jikaso.text:
        cho = yu.util.try_float(jikaso.text.split('兆')[0].replace(',',''))
        jikaso = jikaso.text.split('兆')[1]
      else:
        cho = 0
        jikaso = jikaso.text
      jikaso = jikaso.replace(',','').replace('億','').replace('円','')
      self.jikaso = cho * 1000000000000 + yu.util.try_float(jikaso) * 100000000
      #取引所
      sss = self.soup.find('span',{'class':'market'})
      self.market = sss.text
      #配当利回り
      per_pbr_rimawari = self.soup.find('div',{"id":"stockinfo_i3"})
      result = re.match("[\s\S]*?([\d\.－]+)[\s\S]+?倍[\s\S]*?([\d\.－]+)[\s\S]+?倍[\s\S]*?([\d\.－]+)[\s\S]+?％", per_pbr_rimawari.text)
      self.per = result.group(1)
      self.pbr = result.group(2)
      self.haito_rimawari = result.group(3)

    except:
      print(f"except!!{code},{sys._getframe().f_code.co_name}", file=sys.stderr)

    try:
      #値付かずのときは前日株価を参照する
      if self.kabuka==0:
        kabuka = self.soup2.find('span',{'class':'price'})
        self.kabuka = kabuka.text.replace(',','').replace(' 円','').replace('株価 ','')
    except:
      pass

    try:
      #決算予定日
      sss = self.soup2.find('div',{'class':'block_update right'})
      self.kessan_str = ' '.join(sss.text.split())
      sss = self.soup2.find('div',{'class':'date left'})
      jjj = ''.join(sss.text.split())
      jjj = jjj.replace('下旬','/25').replace('中旬','/15').replace('上旬','/05')
      self.kessan = datetime.datetime.strptime(jjj, '%Y/%m/%d')
    except:
      self.kessan_str = 'fail'
      self.kessan = datetime.datetime.strptime('9999/1/1', '%Y/%m/%d')

  #株予報スレッド
  def set_target_code_th1(self, code):
    url = "https://kabuyoho.ifis.co.jp/index.php?id=100&action=tp1&sa=report&bcode=" + str(code)
    #print(url)
    res = self.session2.get(url, headers=self.header)
    self.cur_html2 = res.content
    self.soup2 = BeautifulSoup(self.cur_html2,"html.parser")

  def get_shuseihoukou(self):
    try:
      q4tbl = self.soup.find('div',{'class':'fin_year_t0_d fin_year_forecast_d dispnone'}).find('table')
      self.shuseihoukou_years = q4tbl.text.count('実')
      up = q4tbl.text.count('↑')
      down = q4tbl.text.count('↓')
      self.shuseihoukou_ratio = up/(up+down)
    except:
      self.shuseihoukou_ratio = 0
      self.shuseihoukou_years = 0 

    try:
      q2tbl = self.soup.find('div',{'class':'fin_half_t0_d fin_half_forecast_d dispnone'}).find('table')
      self.shuseihoukou_half_years = q2tbl.text.count('実')
      up = q2tbl.text.count('↑')
      down = q2tbl.text.count('↓')
      self.shuseihoukou_half_ratio = up/(up+down)
    except:
      self.shuseihoukou_half_ratio = 0
      self.shuseihoukou_half_years = 0 
    
  def get_cashflow(self):
    #キャッシュフロー
    self.cashflow = {}
    self.cashflow['free'] = []
    self.cashflow['eigyo'] = []
    self.cashflow['toushi'] = []
    self.cashflow['zaimu'] = []
    self.cashflow['genkin'] = []
    self.cashflow['genkin_ratio'] = []
    tr=self.soup.find('tr',{'class':'oc_t1 oc_t1_cf'})
    trs=tr.parent.find_all('tr')
    for tr in trs:
      tds=tr.find_all("td")
      #print(f"{tds}")
      if 5 < len(tds):
        self.cashflow['free'].append(''.join(tds[1].text.split()).replace(',',''))
        self.cashflow['eigyo'].append(''.join(tds[2].text.split()).replace(',',''))
        self.cashflow['toushi'].append(''.join(tds[3].text.split()).replace(',',''))
        self.cashflow['zaimu'].append(''.join(tds[4].text.split()).replace(',',''))
        self.cashflow['genkin'].append(''.join(tds[5].text.split()).replace(',',''))
        self.cashflow['genkin_ratio'].append(''.join(tds[6].text.split()).replace(',',''))

    self.eigyo_cf_per = self.jikaso / (1000000 * 4 * float(self.cashflow['eigyo'][-1]))

  def get_quarter_settlement(self):
    #四半期決算
    self.name=""
    self.quarter_settlement = {}
    self.quarter_settlement['keijo'] = [] 
    self.quarter_settlement['uriage'] = [] 
    self.quarter_settlement['eigyo'] = [] 
    self.quarter_settlement['saishu'] = [] 
    self.quarter_settlement['hitokabueki'] = [] 
    self.quarter_settlement['date'] = [] 
    #self.quarter_settlement['keijo'] = pd.Series()
    try:
      divs=self.soup.find('div',{'class':'si_i1_1'})
      if divs is not None:      
        m=re.search(r'[\s]*\d+[\s]+([\S]+)', divs.text)
        self.name=m.group(1)
      divs = self.soup.find('div',{'class':'fin_quarter_t0_d fin_quarter_result_d'})
      if divs is not None:      
        trs = divs.find_all("tr")
        for tr in trs:
          tds = tr.find_all("td")
          if len(tds)==7 and ('/' in tds[6].text):
            self.quarter_settlement['uriage'].append(yu.util.try_float(tds[0].text.replace(',', '')))
            self.quarter_settlement['eigyo'].append(yu.util.try_float(tds[1].text.replace(',', '')))
            self.quarter_settlement['keijo'].append(yu.util.try_float(tds[2].text.replace(',', '')))
            self.quarter_settlement['saishu'].append(yu.util.try_float(tds[3].text.replace(',', '')))
            self.quarter_settlement['hitokabueki'].append(yu.util.try_Decimal(tds[4].text.replace(',', '')))
            self.quarter_settlement['date'].append(tds[6].text)

      #通年決算
      self.year_settlement = {}
      self.year_settlement['hitokabueki'] = []
      self.year_settlement['keijo'] = []
      self.year_settlement['saishu'] = []
      self.year_settlement['haito'] = []
      self.year_settlement['date'] = []
      self.year_settlement['period'] = []
      divs = self.soup.find('div',{'class':'fin_year_t0_d fin_year_result_d'})
      if divs is not None:      
        for trs in divs.find_all("tr"):
          tds = trs.find_all("td")
          ths = trs.find_all("th")
          if len(tds)==7 and ('/' in tds[6].text):
            self.year_settlement['date'].append(tds[6].text)
            self.year_settlement['period'].append(''.join(unicodedata.normalize("NFKD", ths[0].text).split()))
            self.year_settlement['keijo'].append(yu.util.try_float(tds[2].text.replace(',', '')))
            self.year_settlement['saishu'].append(yu.util.try_float(tds[3].text.replace(',', '')))
            self.year_settlement['hitokabueki'].append(yu.util.try_float(tds[4].text.replace(',', '')))
            self.year_settlement['haito'].append(yu.util.try_float(tds[5].text.replace(',', '')))
        #print(self.year_settlement['period'])
    except:
      exception_type, exception_object, exception_traceback = sys.exc_info()
      print(f"エラーが起きたファイル名：{exception_traceback.tb_frame.f_code.co_filename}",  file=sys.stderr)
      print(f"行番号：{exception_traceback.tb_lineno}",  file=sys.stderr)

    #各種PER
    try:
      self.eigyo_per = self.jikaso / (1000000 * 4 * self.quarter_settlement['eigyo'][-1])
      self.eigyo_per4 = self.jikaso / (1000000 * (self.quarter_settlement['eigyo'][-1]+self.quarter_settlement['eigyo'][-2]+self.quarter_settlement['eigyo'][-3]+self.quarter_settlement['eigyo'][-4]))
    except:
      self.eigyo_per = 0
    try:
      self.keijo_per = self.jikaso / (1000000 * 4 * self.quarter_settlement['keijo'][-1])
      self.keijo_per4 = self.jikaso / (1000000 * (self.quarter_settlement['keijo'][-1]+self.quarter_settlement['keijo'][-2]+self.quarter_settlement['keijo'][-3]+self.quarter_settlement['keijo'][-4]))
    except:
      self.keijo_per = 0
    try:
      self.saishu_per = self.jikaso / (1000000 * 4 * self.quarter_settlement['saishu'][-1])
      self.saishu_per4 = self.jikaso / (1000000 * (self.quarter_settlement['saishu'][-1]+self.quarter_settlement['saishu'][-2]+self.quarter_settlement['saishu'][-3]+self.quarter_settlement['saishu'][-4]))
    except:
      self.saishu_per = 0
    #print(F"{self.jikaso} {self.quarter_settlement['saishu'][len(self.quarter_settlement['saishu'])-1]}")

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
        if len(df_today)==0:
          return
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
          #dftoday = dftoday.append(row, ignore_index=True)
          dftoday = pd.concat([dftoday, pd.DataFrame(row).transpose()])

    df = pd.DataFrame()
    tables = soup.find('table', {'class':'stock_kabuka_hist w100per'}) or soup.find('table', {'class':'stock_kabuka_hist'})
    for trs in tables.find_all("tr"):
      if (2 <= len(trs)):
        ths = trs.find_all("th")
        date = ths[0].text
        tds = trs.find_all("td")
        if (0 < len(tds)):
          row = pd.Series([date, tds[0].text.replace(",",""), yu.util.try_float(tds[1].text), tds[2].text.replace("\n","")])
          #df = df.append(row, ignore_index=True)
          df = pd.concat([df, pd.DataFrame(row).transpose()])
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
        period = tds[9].get_text(strip=True).replace(" ","").split("/")
        period = period * 2 #12ヶ月決算の場合は同じ値を2つ入れておく
        row = pd.Series([tds[0].renderContents().decode('utf-8'), tds[1].get_text(strip=True), period[0], period[1]])
        #df = df.append(row, ignore_index=True)
        df = pd.concat([df, pd.DataFrame(row).transpose()])

    df.columns = ["Code","Name", "Period1", "Period2"]
    #print(df)
    return(df)
    
  def get_tse_code_list(self):
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    df = pd.read_excel(url)
    df.set_index('コード', inplace=True)
    return df

    #res = urllib.request.urlopen(url)
    #res = res.read().decode('shift_jisx0213')
    #res = res.read().decode('cp932')
    #xls = pd.ExcelFile(res)
    #df = xls.parse(xls.sheet_names[0])
    #df = df.rename(columns={'<TICKER>':'TICKER', '<DTYYYYMMDD>':'DTYYYYMMDD', '<TIME>':'TIME', '<OPEN>':'OPEN', '<HIGH>':'HIGH', '<LOW>':'LOW', '<CLOSE>':'CLOSE', '<VOL>':'VOL'})
    #df["DTYYYYMMDD"] = df["DTYYYYMMDD"].astype(str)
    #df["TIME"] = df["TIME"].map("{:06d}".format)
    ##df["DATETIME"]=pd.to_datetime(df["DTYYYYMMDD"]+df["TIME"], format='%Y%m%d%H%M%S')
    #df.insert(0,"DATETIME", pd.to_datetime(df["DTYYYYMMDD"]+df["TIME"], format='%Y%m%d%H%M%S'))
    #df=df.drop({"DTYYYYMMDD","TIME","VOL"}, axis=1)
    #df.reset_index(drop=True, inplace=True)
    
    #return df

  def get_topix400(self):
    df = self.get_tse_code_list()
    df_topiix_mid400 = df[df.loc[:,'規模区分']=='TOPIX Mid400']

    self.code_j = df
    return df_topiix_mid400.index

  def days_to_next_open_day(self):
    today = datetime.datetime.now().date()
    for i in range(1,10):
      day = today + datetime.timedelta(days=i)
      if not (5<=day.weekday() or jpholiday.is_holiday(day)):
        break
    return i

  #単元株数を返す
  def get_tangen(self, code):
    if (len(self.df_master)==0):
      self.df_master = pd.read_csv('master_CLMIssueMstKabu.csv', index_col='sIssueCode')
    return self.df_master.loc[int(code),'sBaibaiTani']


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

    self.yu.set_target_code("7533")
    self.yu.get_quarter_settlement()
    self.yu.get_per_history()

    self.yu.set_target_code("8617")
    self.yu.get_quarter_settlement()
    print(F"株価：{self.yu.kabuka}, 時価総額：{self.yu.jikaso}")
    #各種PER
    print(F"営業PER:{self.yu.eigyo_per:.1f} 経常PER:{self.yu.keijo_per:.1f} 最終PER:{self.yu.saishu_per:.1f}")
    print(F"営業PER4:{self.yu.eigyo_per4:.1f} 経常PER4:{self.yu.keijo_per4:.1f} 最終PER4:{self.yu.saishu_per4:.1f}")
    print(F"決算:{self.yu.kessan_str} {self.yu.kessan}")

    self.yu.set_target_code("9984")
    print(F"株価：{self.yu.kabuka}, 時価総額：{self.yu.jikaso}")
    #四半期決算
    self.yu.get_quarter_settlement()
    print(self.yu.quarter_settlement)
    self.assertEqual(2, self.yu.quarter_settlement['uriage'].index(1507507) - self.yu.quarter_settlement['uriage'].index(1279973))
    self.assertEqual(6, self.yu.quarter_settlement['uriage'].index(1337638) - self.yu.quarter_settlement['uriage'].index(2381070))
    self.assertEqual(1, self.yu.quarter_settlement['keijo'].index(834120) - self.yu.quarter_settlement['eigyo'].index(-1351669))
    print(F"name is {self.yu.name}")
    print(F"latest date is {self.yu.quarter_settlement['date'][-1]}")

    #PER推移
    self.yu.get_per_history()
    print(self.yu.per_history)
    self.assertEqual(240, len(self.yu.per_history['day']))
    #self.assertEqual(0, len(self.yu.per_history['wek']))
    self.assertTrue(100 < len(self.yu.per_history['mon']))

  def test_reit(self):
    self.yu = yu_kabutan()
    df = self.yu.get_reit_code_list()
    print(df)
    self.assertTrue(True)

  def test_tse(self):
    self.yu = yu_kabutan()
    df = self.yu.get_tse_code_list()
    print(df)

  def test_tangen(self):
    self.yu = yu_kabutan()
    self.assertTrue(1==self.yu.get_tangen(1321))
    self.assertTrue(100==self.yu.get_tangen(9984))

  def test_local(self):
    self.yu = yu_kabutan()
    self.yu.use_local_file()
    #self.yu.set_target_code(1869)
    #self.yu.set_target_code(4194)
    self.yu.set_target_code(1301)
    self.yu.get_shuseihoukou()
    self.yu.get_cashflow()
    self.yu.get_quarter_settlement()
    self.assertTrue(0.9 < self.yu.shuseihoukou_ratio)
    print(f"---------{self.yu.shuseihoukou_years}----------")
    self.assertTrue(3 <= self.yu.shuseihoukou_years)
    print(f"name={self.yu.name}")
    #print(f"{self.yu.quarter_settlement['uriage']}")
    print(f"per={self.yu.per} pbr={self.yu.pbr} {self.yu.haito_rimawari}%")
    print(f"free_cash_flow={self.yu.cashflow['free']}")
    print(f"free_cash_flow={self.yu.cashflow['eigyo']}")


if __name__ == "__main__":
  unittest.main()
