import urllib.request
from bs4 import BeautifulSoup
import sys
import math
import requests


class yu_web:
  def __init__(self):
    self.session = requests.session()
    self.cur_html = ""
    self.soup = None


if __name__ == "__main__":
  yu = yu_web()
