import zipfile
from collections import OrderedDict
import traceback
import pandas as pd
import re
import io


class yu_zipreader:
  def __init__(self):
    self.re_match = re.compile(r'^.*?\.csv$').match
    self.df = pd.DataFrame()
    self.file_datas = OrderedDict()

  def __del__(self):
    pass

  def _date_psr(self, x):
    from datetime import datetime
    return datetime.strptime(x, '%Y%m%d%H%M')
  
  #ZIPを読み込んでdfに溜める
  def read_click_cfd_hist(self, zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_data:
      # ファイルリスト取得
      infos = zip_data.infolist()

      for info in infos:
        # ファイルパスでスキップ判定
        if self.re_match(info.filename) is None:
          continue
        # zipからファイルデータを読み込む
        file_data = zip_data.read(info.filename)
        self.df = pd.concat([self.df, pd.read_csv(io.StringIO(file_data.decode('sjis')), parse_dates=["日時"], date_parser=self._date_psr)])

  def read_click_cfd_hist_zips(self, zip_dir, zip_names):
    for z in zip_names:
      self.read_click_cfd_hist(zip_dir + "/" + z)

  #後処理。日付の整形とインデックス振り直し
  def read_click_cfd_hist_finish(self):
    self.df.sort_values("日時")
    self.df.reset_index(drop=True, inplace=True)



if __name__ == "__main__":
  yuz = yu_zipreader()
  yuz.read_click_cfd_hist("/home/arle/work/cfdtest/dat/Brent_202109.zip")
  print(yuz.df.head(10))
  print(yuz.df.tail(10))

  yuz.read_click_cfd_hist_zips("/home/arle/work/cfdtest/dat", ["Brent_202110.zip", "Brent_202111.zip"])
  yuz.read_click_cfd_hist_finish()
  print(yuz.df.head(10))
  print(yuz.df.tail(10))

