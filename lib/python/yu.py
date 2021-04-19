import urllib.request
from bs4 import BeautifulSoup
import sys
import math
import requests
import unittest
from decimal import *

class util:
  def try_float(f):
    try:
      return(float(f))
    except:
      return(None)
          
  def try_Decimal(f):
    try:
      return(Decimal(f))
    except:
      return(None)

class web:
  def __init__(self):
    self.session = requests.session()
    self.cur_html = ""
    self.soup = None

  def __del__(self):
    self.session.close()


class yu_web_test(unittest.TestCase):
  def test1(self):
    yu = web()
    self.assertEqual(requests.sessions.Session, type(yu.session))

  def test_try_float(self):
    self.assertEqual(123, util.try_float("123"))
    self.assertEqual(123, util.try_float("123.0"))
    self.assertEqual(123.1, util.try_float("123.1"))
    self.assertEqual(123.2, util.try_float("123.2"))
    self.assertEqual(None, util.try_float("-"))
    self.assertEqual(None, util.try_float("－"))
    self.assertEqual(-123, util.try_float("-123"))

  def test_try_Decimal(self):
    self.assertEqual(123, util.try_Decimal("123"))
    self.assertEqual(123, util.try_Decimal("123.0"))
    self.assertEqual(Decimal(123)+Decimal("0.1"), util.try_Decimal("123.1"))
    self.assertEqual(Decimal(123)+Decimal("0.2"), util.try_Decimal("123.2"))
    self.assertEqual(None, util.try_Decimal("-"))
    self.assertEqual(None, util.try_Decimal("－"))
    self.assertEqual(-123, util.try_Decimal("-123"))


if __name__ == "__main__":
  unittest.main()
