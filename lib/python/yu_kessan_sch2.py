import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import json

#SBI証券のjsonから決算発表の日時を得る

class SBIScraper:
    def __init__(self, base_url, html_url):
        self.base_url = base_url
        self.html_url = html_url
        self.param = self._extract_param()

    def _extract_param(self):
        # 指定されたURLからHTMLを取得
        response = requests.get(self.html_url)
        response.raise_for_status()
        html = response.text

        # 正規表現を使用してANNOUNCE_INFO_PARAMの値を抽出
        match = re.search(r"var ANNOUNCE_INFO_PARAM = '(.*?)';", html)
        if match:
            return match.group(1)
        else:
            raise ValueError("ANNOUNCE_INFO_PARAMが見つかりません。")

    def _fix_json(self, json_str):
        # 全体の括弧()を置き換える
        json_str = json_str.replace('(', ' ').replace(')', ' ')

        # link キーをダブルコーテーションで囲む
        json_str = re.sub(r'(link)\s*:', r'"\1":', json_str)

        return json_str

    def get_announcement_info(self, date):
        # URLを作成
        selected_date = date.strftime('%Y%m%d')
        url = f"{self.base_url}{self.param}&selectedDate={selected_date}"
        #print(url)

        # データを取得
        response = requests.get(url)
        response.raise_for_status()
        #print(response)
        json_str = response.text

        # JSON文字列を修正
        fixed_json_str = self._fix_json(json_str)
        data = json.loads(fixed_json_str)

        # JSONデータをパースして必要な情報を抽出
        body = data.get('body', [])
        records = []
        for item in body:
            record = {
                'orderDate': item.get('orderDate'),
                'orderTime': item.get('orderTime'),
                'productCode': item.get('productCode'),
                'productName': item.get('productName')
            }
            records.append(record)

        # データフレームに変換
        df = pd.DataFrame(records).sort_values(['orderTime', 'productCode'])
        return df

# 使用例
html_url = 'https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_DataStoreID=DSWPLETmgR001Control&_ActionID=DefaultAID&burl=iris_economicCalendar&cat1=market&cat2=economicCalender&dir=tl1-cal%7Ctl2-schedule%7Ctl3-stock%7Ctl4-calsel&file=index.html&getFlg=on'
base_url = 'https://vc.iris.sbisec.co.jp/calendar/settlement/stock/announcement_info_date.do'

scraper = SBIScraper(base_url, html_url)
#date = pd.to_datetime('2024-05-01')
date = pd.to_datetime('now')
df = scraper.get_announcement_info(date)

print(df)

