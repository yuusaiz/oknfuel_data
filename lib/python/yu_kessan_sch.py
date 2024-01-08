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
import pytz


class yu_kessan_sch(yu.web):
  def __init__(self):
    super().__init__()

  #指定した日数後の決算予定銘柄リストを返す
  def get_kessan_sch(self, day_offset):

    now=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    now=now+datetime.timedelta(days=day_offset)

    print(now)
    lines = []

    for i in range(1,5):
      url = F"https://www.nikkei.com/markets/kigyo/money-schedule/kessan/?ResultFlag=1&SearchDate1={now.year}年{now.month:02}&SearchDate2={now.day:02}&hm={i}"
      res = self.session.get(url)
      self.cur_html = res.content
      self.soup = BeautifulSoup(self.cur_html,"html.parser")
      trs = self.soup.find_all('tr',{'class':'tr2'})
      #print(F"{len(trs)} {url}")
      for tr in trs:
        trstr = ' '.join(tr.text.split())
        #print(trstr)
        lines.append(trstr)
      num_str = self.soup.find('p',{'class':'a-fll a-mb0'})
      if (num_str == None):
        break
      pattern = r'[\s\S]+?(\d+)件目[\s\S]+?全(\d+)'
      result = re.match(pattern, num_str.text)
      if result:
        if (result.group(1) == result.group(2)):
          #print("hit")
          break

    codelist = []
    for l in lines:
      #print(l)
      pattern = r'[\s\S]+? (\d+) '
      result = re.match(pattern, l)
      if result:
        codelist.append(result.group(1))

    self.codelist = codelist


class yu_kessan_schtest(unittest.TestCase):
  def test1(self):
    self.yu = yu_kessan_sch()

    print("0")
    self.yu.get_kessan_sch(0)
    print(self.yu.codelist)
    print("1")
    self.yu.get_kessan_sch(1)
    print(self.yu.codelist)
    print("10")
    self.yu.get_kessan_sch(10)
    print(self.yu.codelist)
    print("-11")
    self.yu.get_kessan_sch(-11)
    print(self.yu.codelist)

if __name__ == "__main__":
  unittest.main()




