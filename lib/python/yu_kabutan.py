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
import yu_web 
import unittest

class yu_kabutan(yu_web.yu_web):
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
    url = "https://kabutan.jp/stock/finance?code=" + str(code)
    res = self.session.get(url)
    self.cur_html = res.content
    self.soup = BeautifulSoup(self.cur_html,"html.parser")

  def get_quarter_settlement(self):
    self.quarter_settlement = {}
    self.quarter_settlement['keijo'] = [] 
    self.quarter_settlement['uriage'] = [] 
    self.quarter_settlement['eigyo'] = [] 
    self.quarter_settlement['saishu'] = [] 
    self.quarter_settlement['hitokabueki'] = [] 
    self.quarter_settlement['haito'] = [] 
    #self.quarter_settlement['keijo'] = pd.Series()
    divs = self.soup.find('div',{'class':'fin_q_t0_d fin_q_t1_d'})
    for trs in divs.find_all("tr"):
      tds = trs.find_all("td")
      if len(tds)==7 and ('/' in tds[6].text):
        self.quarter_settlement['uriage'].append(float(tds[0].text.replace(',', '')))
        self.quarter_settlement['eigyo'].append(yu_web.util.try_float(tds[1].text.replace(',', '')))
        self.quarter_settlement['keijo'].append(float(tds[2].text.replace(',', '')))
        self.quarter_settlement['saishu'].append(float(tds[3].text.replace(',', '')))
        self.quarter_settlement['hitokabueki'].append(float(tds[4].text.replace(',', '')))
        self.quarter_settlement['haito'].append(float(tds[5].text.replace(',', '')))


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
    self.yu.get_quarter_settlement()
    self.assertEqual(requests.sessions.Session, type(yu.session))

if __name__ == "__main__":
  unittest.main()
