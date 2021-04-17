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

class yu_kabutan(yu_web.yu_web):
  def __init__(self):
    print("yu_kabutan")
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


if __name__ == "__main__":
  yu = yu_kabutan()
  yu.login_kabutan("aa","bb")

