import urllib.request
from bs4 import BeautifulSoup
import sys
import math
import requests
import unittest

class util:
  def try_float(f):
    try:
      return(float(f))
    except:
      return(None)
          

class yu_web:
  def __init__(self):
    self.session = requests.session()
    self.cur_html = ""
    self.soup = None


class yu_web_test(unittest.TestCase):
  def test1(self):
    yu = yu_web()
    self.assertEqual(requests.sessions.Session, type(yu.session))

  def test_try_float(self):
    self.assertEqual(123, util.try_float("123"))
    self.assertEqual(123, util.try_float("123.0"))
    self.assertEqual(123.1, util.try_float("123.1"))
    self.assertEqual(None, util.try_float("-"))
    self.assertEqual(None, util.try_float("－"))
    self.assertEqual(-123, util.try_float("-123"))


if __name__ == "__main__":
  unittest.main()
