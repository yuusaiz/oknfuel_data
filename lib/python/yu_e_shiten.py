import urllib3
import ssl
import datetime
import json
import time
import yu_kabutan
import pickle


# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = work_key
        self.str_value = work_value

class yu_e_shiten:
  def __init__(self):
    self.sUrlRequest = ''       # request用仮想URL
    self.sUrlMaster = ''        # master用仮想URL
    self.sUrlPrice = ''         # price用仮想URL
    self.sUrlEvent = ''         # event用仮想URL
    self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。
    self.sTokuteiKouzaKubunGenbutu = '' # 12.特定口座区分現物    0：一般、1：特定源泉徴収なし、2：特定源泉徴収あり
    self.sTokuteiKouzaKubunSinyou = ''  # 13.特定口座区分信用    0：一般、1：特定源泉徴収なし、2：特定源泉徴収あり。信用口座未開設の場合、0がセットされる。
    self.sSinyouKouzaKubun = '' # 16.信用取引口座開設区分  0：未開設、1：開設
    self.sHikazeiKouzaKubun = ''# 21.非課税口座開設区分  0：未開設、1：開設  ※ＮＩＳＡ口座の開設有無を示す。
    self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース>概要」の「3-2.ログイン、ログアウト」参照
    self.sPassword = ''
    self.sUserId = ''
    self.sJsonOfmt = '5'         # 返り値の表示形式指定
    self.int_p_no = 0
    #self.my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'
    #self.my_url = 'https://kabuka.e-shiten.jp/e_api_v4r5/'
    #self.my_url = 'https://kabuka.e-shiten.jp/e_api_v4r6/'
    #self.my_url = 'https://kabuka.e-shiten.jp/e_api_v4r7/'
    self.my_url = 'https://kabuka.e-shiten.jp/e_api_v4r8/'

# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
  def func_p_sd_date(self, int_systime):
      str_psddate = ''
      str_psddate = str_psddate + str(int_systime.year) 
      str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
      str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
      str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
      str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
      str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
      str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
      return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
  def func_check_json_dquat(self, str_value) :
      if len(str_value) == 0 :
          str_value = '""'
          
      if not str_value[:1] == '"' :
          str_value = '"' + str_value
          
      if not str_value[-1:] == '"' :
          str_value = str_value + '"'
          
      return str_value
      
      
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
  def func_strip_dquot(self, text):
      if len(text) > 0:
          if text[0:1] == '"' :
              text = text[1:]
              
      if len(text) > 0:
          if text[-1] == '\n':
              text = text[0:-1]
          
      if len(text) > 0:
          if text[-1:] == '"':
              text = text[0:-1]
          
      return text
# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
#
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
  def func_replace_urlecnode( self, str_input ):
      str_encode = ''
      str_replace = ''

      for i in range(len(str_input)):
          str_char = str_input[i:i+1]

          if str_char == ' ' :
              str_replace = '%20'       #「 」 → 「%20」 半角空白
          elif str_char == '!' :
              str_replace = '%21'       #「!」 → 「%21」
          elif str_char == '"' :
              str_replace = '%22'       #「"」 → 「%22」
          elif str_char == '#' :
              str_replace = '%23'       #「#」 → 「%23」
          elif str_char == '$' :
              str_replace = '%24'       #「$」 → 「%24」
          elif str_char == '%' :
              str_replace = '%25'       #「%」 → 「%25」
          elif str_char == '&' :
              str_replace = '%26'       #「&」 → 「%26」
          elif str_char == "'" :
              str_replace = '%27'       #「'」 → 「%27」
          elif str_char == '(' :
              str_replace = '%28'       #「(」 → 「%28」
          elif str_char == ')' :
              str_replace = '%29'       #「)」 → 「%29」
          elif str_char == '*' :
              str_replace = '%2A'       #「*」 → 「%2A」
          elif str_char == '+' :
              str_replace = '%2B'       #「+」 → 「%2B」
          elif str_char == ',' :
              str_replace = '%2C'       #「,」 → 「%2C」
          elif str_char == '/' :
              str_replace = '%2F'       #「/」 → 「%2F」
          elif str_char == ':' :
              str_replace = '%3A'       #「:」 → 「%3A」
          elif str_char == ';' :
              str_replace = '%3B'       #「;」 → 「%3B」
          elif str_char == '<' :
              str_replace = '%3C'       #「<」 → 「%3C」
          elif str_char == '=' :
              str_replace = '%3D'       #「=」 → 「%3D」
          elif str_char == '>' :
              str_replace = '%3E'       #「>」 → 「%3E」
          elif str_char == '?' :
              str_replace = '%3F'       #「?」 → 「%3F」
          elif str_char == '@' :
              str_replace = '%40'       #「@」 → 「%40」
          elif str_char == '[' :
              str_replace = '%5B'       #「[」 → 「%5B」
          elif str_char == ']' :
              str_replace = '%5D'       #「]」 → 「%5D」
          elif str_char == '^' :
              str_replace = '%5E'       #「^」 → 「%5E」
          elif str_char == '`' :
              str_replace = '%60'       #「`」 → 「%60」
          elif str_char == '{' :
              str_replace = '%7B'       #「{」 → 「%7B」
          elif str_char == '|' :
              str_replace = '%7C'       #「|」 → 「%7C」
          elif str_char == '}' :
              str_replace = '%7D'       #「}」 → 「%7D」
          elif str_char == '~' :
              str_replace = '%7E'       #「~」 → 「%7E」
          else :
              str_replace = str_char

          str_encode = str_encode + str_replace

      return str_encode

# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
  def func_make_url_request(self, auth_flg, \
                            url_target, \
                            work_class_req) :
      work_key = ''
      work_value = ''

      str_url = url_target
      if auth_flg == True :
          str_url = str_url + 'auth/'
      
      str_url = str_url + '?{\n\t'
      
      for i in range(len(work_class_req)) :
          work_key = self.func_strip_dquot(work_class_req[i].str_key)
          if len(work_key) > 0:
              if work_key[:1] == 'a' :
                  work_value = work_class_req[i].str_value
              else :
                  work_value = self.func_check_json_dquat(work_class_req[i].str_value)

              str_url = str_url + self.func_check_json_dquat(work_class_req[i].str_key) \
                                  + ':' + work_value \
                                  + ',\n\t'
                 
          
      str_url = str_url[:-3] + '\n}'
      return str_url


# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
  def func_api_req(self, str_url): 
      print('送信文字列＝')
      print(str_url)  # 送信する文字列

      # e-shitenのTSL暗号方式制限の回避
      ssl_context = ssl.create_default_context()
      ssl_context.set_ciphers('RSA+AES')

      # APIに接続
      http = urllib3.PoolManager(ssl_context=ssl_context)
      req = http.request('GET', str_url)
      print("req.status= ", req.status )

      # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
      bytes_reqdata = req.data
      str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

      print('返信文字列＝')
      #print(str_shiftjis)

      # JSON形式の文字列を辞書型で取り出す
      json_req = json.loads(str_shiftjis)

      return json_req


# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
  def func_login(self):
      # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
      # p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
      
      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sCLMID"'
      str_value = 'CLMAuthLoginRequest'
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sUserId"'
      #str_value = str_userid
      str_value = self.sUserId
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      str_key = '"sPassword"'
      #str_value = str_passwd
      str_value = self.sPassword 
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      str_value = "5"    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # ログインとログイン後の電文が違うため、第１引数で指示。
      # ログインはTrue。それ以外はFalse。
      # このプログラムでの仕様。APIの仕様ではない。
      # URL文字列の作成
      str_url = self.func_make_url_request(True, \
                                       self.my_url, \
                                       req_item)
      # API問合せ
      json_return = self.func_api_req(str_url)
      # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
      # p2/46 No.2 引数名:CLMAuthLoginAck を参照してください。

      int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
      if not json_return.get('sResultCode') == None :
          int_sResultCode = int(json_return.get('sResultCode'))
      else :
          int_sResultCode = -1
      # sResultCodeは、マニュアル
      # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
      # (api_request_if_order_vOrO.pdf)
      # の p13/42 「6.メッセージ一覧」を参照ください。
      #
      # 時間外の場合 'sResultCode' が返らないので注意
      # 参考例
      # {
      #         "p_no":"1",
      #         "p_sd_date":"2022.11.25-08:28:04.609",
      #         "p_rv_date":"2022.11.25-08:28:04.598",
      #         "p_errno":"-62",
      #         "p_err":"システム、情報提供時間外。",
      #         "sCLMID":"CLMAuthLoginRequest"
      # }




      if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
          # ---------------------------------------------
          # ログインでの注意点
          # 契約締結前書面が未読の場合、
          # 「int_p_errno = 0 And int_sResultCode = 0」で、
          # sUrlRequest=""、sUrlEvent="" が返されログインできない。
          # ---------------------------------------------
          if len(json_return.get('sUrlRequest')) > 0 :
              # 口座属性クラスに取得した値をセット
              self.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')      # 8.譲渡益課税区分    1：特定  3：一般  5：NISA
              self.sTokuteiKouzaKubunGenbutu = json_return.get('sTokuteiKouzaKubunGenbutu') # 12.特定口座区分現物    0：一般、1：特定源泉徴収なし、2：特定源泉徴収あり
              self.sTokuteiKouzaKubunSinyou = json_return.get('sTokuteiKouzaKubunSinyou')  # 13.特定口座区分信用    0：一般、1：特定源泉徴収なし、2：特定源泉徴収あり。信用口座未開設の場合、0がセットされる。
              self.sSinyouKouzaKubun = json_return.get('sSinyouKouzaKubun')    # 16.信用取引口座開設区分  0：未開設、1：開設
              self.sHikazeiKouzaKubun = json_return.get('sHikazeiKouzaKubun')  # 21.非課税口座開設区分  0：未開設、1：開設  ※ＮＩＳＡ口座の開設有無を示す。
              self.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
              self.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
              self.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
              self.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
              bool_login = True
          else :
              print('契約締結前書面が未読です。')
              print('ブラウザーで標準Webにログインして確認してください。')
      else :  # ログインに問題があった場合
          print('p_errno:', json_return.get('p_errno'))
          print('p_err:', json_return.get('p_err'))
          print('sResultCode:', json_return.get('sResultCode'))
          print('sResultText:', json_return.get('sResultText'))
          print()
          bool_login = False


      f = open('login.pickle','wb')
      pickle.dump(self,f)
      f.close

      return bool_login

  def func_login_pickle(self):
      print("func_login_pickle.")
      f = open('login.pickle','rb')
      picke_e = pickle.load(f)
      f.close
      #p_noについて、現在時刻から適当に決める。午前6時基準。
      dd=datetime.datetime.now()
      print(dd)
      daysec=0
      if dd.hour < 6:
        daysec = (dd.hour+24)*60*60 + dd.minute*60 + dd.second
      else:
        daysec = (dd.hour)*60*60 + dd.minute*60 + dd.second
      picke_e.int_p_no = daysec*1000
      #print(F"set int_p_no = {picke_e.int_p_no}.")
      return picke_e
      
# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
  def func_logout(self):
      # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
      # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
      
      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sCLMID"'
      str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      str_value = "5"    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # ログインとログイン後の電文が違うため、第１引数で指示。
      # ログインはTrue。それ以外はFalse。
      # このプログラムでの仕様。APIの仕様ではない。
      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlRequest, \
                                       req_item)
      # API問合せ
      json_return = self.func_api_req(str_url)
      # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
      # p3/46 No.4 引数名:CLMAuthLogoutAck を参照してください。

      print(json_return.get('sResultCode'))
      int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
      if int_sResultCode ==  0 :    # ログアウトエラーでない場合
          bool_logout = True
      else :  # ログアウトに問題があった場合
          bool_logout = False

      return bool_logout

# 機能: 日足株価データ取得
# 返値： 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 引数1: p_no
# 引数2: 銘柄コード
# 引数3: 市場（現在、東証'00'のみ）
# 引数4: 口座属性クラス
# 備考: 銘柄コードは、通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
  def func_get_daily_price(self, 
                          str_sIssueCode,
                          str_sSizyouC,
                          ):
      self.int_p_no += 1
      
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # API request区分
      str_key = '"sCLMID"'
      str_value = 'CLMMfdsGetMarketPriceHistory'  # 蓄積情報問合取得を指示。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 銘柄コード     通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
      str_key = '"sIssueCode"'    #
      str_value = str_sIssueCode
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # 市場C   対象の市場コード（現在"00":東証のみ）、引数省略可能（デフォルト＝東証）。
      str_key = '"sSizyouC"'
      str_value = str_sSizyouC
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)


      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      str_value = "5"    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlPrice, \
                                       req_item)
      # API問合せ
      json_return = self.func_api_req(str_url)

      return json_return

# 機能: タイトル行を株価情報のファイルに書き込む
# 引数1: 出力ファイル名
# 備考: 指定ファイルを開き、１行目に項目コード、２行目に項目名を書き込む。
  def func_write_daily_price_title(self, str_fname_output):
      try:
          with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
              #print('file open at w, "fout": ', str_fname_output )
              # 項目コード
              str_text_out = ''
              str_text_out = str_text_out + 'sDate' + ','
              str_text_out = str_text_out + 'pDOP' + ','
              str_text_out = str_text_out + 'pDHP' + ','
              str_text_out = str_text_out + 'pDLP' + ','
              str_text_out = str_text_out + 'pDPP' + ','
              str_text_out = str_text_out + 'pDV' + ','
              str_text_out = str_text_out + 'pDOPxK' + ','
              str_text_out = str_text_out + 'pDHPxK' + ','
              str_text_out = str_text_out + 'pDLPxK' + ','
              str_text_out = str_text_out + 'pDPPxK' + ','
              str_text_out = str_text_out + 'pDVxK' + ','
              str_text_out = str_text_out + 'pSPUO' + ','
              str_text_out = str_text_out + 'pSPUC' + ','
              str_text_out = str_text_out + 'pSPUK' + '\n'
              #fout.write(str_text_out)     # １行目に列名を書き込む

              # 項目名
              str_text_out = ''
              str_text_out = str_text_out + '日付' + ','
              str_text_out = str_text_out + '始値' + ','
              str_text_out = str_text_out + '高値' + ','
              str_text_out = str_text_out + '安値' + ','
              str_text_out = str_text_out + '終値' + ','
              str_text_out = str_text_out + '出来高' + ','
              str_text_out = str_text_out + '始値（分割調整済み）' + ','
              str_text_out = str_text_out + '高値（分割調整済み）' + ','
              str_text_out = str_text_out + '安値（分割調整済み）' + ','
              str_text_out = str_text_out + '終値（分割調整済み）' + ','
              str_text_out = str_text_out + '出来高（分割調整済み）' + ','
              str_text_out = str_text_out + '株式分割前単位' + ','
              str_text_out = str_text_out + '株式分割後単位' + ','
              str_text_out = str_text_out + '株式分割換算係数（pSPUO/pSPUC）' + '\n'
              fout.write(str_text_out)     # １行目に列名を書き込む

      except IOError as e:
          print('Can not Write!!!')
          print(type(e))


# 機能: 取得した株価情報を追記モードでファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 取得した株価情報（リスト型）
# 備考:
#   指定ファイルを開き、1〜2行目に取得する情報名を書き込み、3行目以降で取得した情報を書き込む。
#   pSPUO,pSPUC,pSPUK は株式分割日（権利落ち日)のみデータが返る。通常は項目自体返らない。
  def func_write_daily_price(self, str_fname_output, list_return):
      try:
          with open(str_fname_output, 'a', encoding = 'utf-8') as fout:
              #print('file open at a, "fout": ', str_fname_output )
              # 取得した情報から行データを作成し書き込む
              str_text_out = ''
              for i in range(len(list_return)):
                  # 行データ作成
                  str_text_out = list_return[i].get("sDate")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDOP")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDHP")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDLP")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDPP")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDV")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDOPxK")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDHPxK")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDLPxK")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDPPxK")
                  str_text_out = str_text_out + ',' + list_return[i].get("pDVxK")
                  # pSPUO,pSPUC,pSPUK は株式分割日（権利落ち日)のみ設定される。
                  if not list_return[i].get("pSPUO") ==  None:
                      str_text_out = str_text_out + ',' + list_return[i].get("pSPUO")
                      str_text_out = str_text_out + ',' + list_return[i].get("pSPUC")
                      str_text_out = str_text_out + ',' + list_return[i].get("pSPUK")
                  str_text_out = str_text_out + '\n'

                  fout.write(str_text_out)     # 処理済みの株価データをファイルに書き込む

      except IOError as e:
          print('Can not Write!!!')
          print(type(e))


  def func_get_and_write_daily_price(self,
                          str_sIssueCode,
                          str_sSizyouC, str_fname_top):
    dic_return = self.func_get_daily_price( str_sIssueCode, str_sSizyouC)
    my_fname_output = str_fname_top + str_sIssueCode + '.csv'   # 書き込むファイル名。カレントディレクトリに上書きモードでファイルが作成される。
    # 出力ファイルにタイトル行を書き込む。
    self.func_write_daily_price_title(my_fname_output)
    
    # 日足株価部分をリスト型で抜き出す。
    list_price = dic_return.get('aCLMMfdsMarketPriceHistory')
    
    # 取得した株価情報を追記モードでファイルに書き込む。
    self.func_write_daily_price(my_fname_output, list_price)

###################################################################################
#  現在価格取得処理

# 株価取得リストの読み込み
# 引数：ファイル名、銘柄コード保存用配列、取得する情報コード用配列
# 指定ファイルを開き、1行目で取得する情報コードを読み込み、2行目以降で銘柄コードを読み込む。
# （通常1行目の）情報コードを読み込む行の第1項目は、'stock_code'とすることが必要。
  def func_read_price_list(self, str_fname_input, my_code, my_column):
      try:
          # 入力データを読み込み処理開始
          with open(str_fname_input, 'r', encoding = 'utf-8') as fin:
              print('file read ok -----', str_fname_input)
                              
              while True:
                  line = fin.readline()
                  
                  if not len(line):
                      #EOFの場合
                      break

                  # 行のデータをcsvの「,」で分割し必要なフィールドを読み込む。
                  sprit_out = line.split(',')
                  
                  if len(sprit_out) > 0:
                      if len(sprit_out[0]) > 0 and self.func_strip_dquot(sprit_out[0]) == 'stock_code':
                          # １行目は表題行なので、情報コードを取得する。
                          # 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
                          # p6-8/26 【情報コード一覧】を利用する。
                          # 取得コードの書式：型+情報コード
                          
                          for i in range(1,len(sprit_out)):
                              my_column.append('')
                              my_column[i] = self.func_strip_dquot(sprit_out[i])

                          # 銘柄コードのリストの最初の項目に、便宜上'stock_code'を入れておく。
                          my_code[-1] = self.func_strip_dquot(sprit_out[0])

                          #1行目だけで良いんで。
                          break
                              
                      elif  len(sprit_out[0]) > 0 :
                          my_code.append('')
                          my_code[-1] = self.func_strip_dquot(sprit_out[0])
                          
                      else:
                          pass
                                      
      except IOError as e:
          print('File Not Found!!!')
          print(type(e))
          #print(line)

      #銘柄はtopix400を使用
      yu = yu_kabutan.yu_kabutan()
      topix400 = yu.get_topix400()
      for c in topix400:
        my_code.append('')
        my_code[-1] = str(c)
      topix100 = yu.get_topix100()
      for c in topix100:
        my_code.append('')
        my_code[-1] = str(c)



# １行目タイトルを株価情報のファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
  def func_write_price_title(self, str_fname_output, my_column):
      try:
          with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
              print('file open at w, "fout": ', str_fname_output )
              # 出力ファイルの１行目の列名を作成
              str_text_out = 'stock_code'
              for i in range(len(my_column)):
                  if len(my_column[i]) > 0 :
                      str_text_out = str_text_out + ',' + self.func_code_to_name(my_column[i])     # 情報コードを名前に変換。
              str_text_out = str_text_out + '\n'
              fout.write(str_text_out)     # １行目に列名を書き込む

      except IOError as e:
          print('Can not Write!!!')
          print(type(e))
          #print(line)




# 取得した株価情報を追記モードでファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
  def func_write_price_list(self, str_fname_output, dic_return, my_column):
      try:
          with open(str_fname_output, 'a', encoding = 'utf-8') as fout:
              print('file open at a, "fout": ', str_fname_output )
              # 取得した情報から行データを作成し書き込む
              str_text_out = ''
              for i in range(len(dic_return)):
                  # 行データ作成
                  str_sIssueCode = dic_return[i].get('sIssueCode') 
                  if not str_sIssueCode == 'stock_code' :
                      str_text_out = str_sIssueCode
                      for n in range(len(my_column)):
                          if len(my_column[n]) > 0 :
                              str_text_out = str_text_out + ',' + dic_return[i].get(my_column[n])
                      str_text_out = str_text_out + '\n'
                      fout.write(str_text_out)     # 処理済みの株価データを書き込む
                    

      except IOError as e:
          print('Can not Write!!!')
          print(type(e))
          #print(line)




# 株価情報の取得
# 引数：銘柄コード（配列）, 取得する「情報コード」（配列）, 口座属性クラス
# マニュアル「ｅ支店・ＡＰＩ、ブラウザからの利用方法」の「時価」シートの時価関連情報取得サンプル
#
# ３．利用方法（２）時価関連情報の取得
# https://10.62.26.91/e_api_v4r2/request/MDExNDczNTEwMDQwNi05MS02NDU1NA==/?{"p_no":"20","p_sd_date":"2021.06.04-14:56:50.000",
# "sCLMID":"CLMMfdsGetMarketPrice","sTargetIssueCode":"6501,6501,101","sTargetColumn":"pDPP,tDPP:T,pPRP","sJsonOfmt":"5"}
#
# 
# 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
# p6-8/26 【情報コード一覧】を利用する。
# 取得コードの書式：型+情報コード
#
# 株価の取得は通信帯域に負荷が掛かります。利用する情報のみの取得をお願いいたします。
  def func_get_price(self, int_p_no, str_code_list, my_column ):
      self.int_p_no += 1

      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      str_key = '"sCLMID"'
      str_value = '"CLMMfdsGetMarketPrice"'   # 株価取得を指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 株価を取得する銘柄コードをセット
      # 取得したい銘柄コードをカンマで区切りで羅列する。
      # 例：{"sTargetIssueCode":"6501,6502,101"}
      str_key = '"sTargetIssueCode"'
      str_value = str_code_list
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      

      # 取得する「情報コード」をセット
      # 取得したい情報コードをカンマで区切りで羅列する。	
      # 例：{"sTargetColumn":"pDPP,tDPP:T,pPRP"}
      str_list = ''
      for i in range(len(my_column)):
          if len(my_column[i]) > 0:
              str_list = str_list + my_column[i] + ','
          
      str_key = '"sTargetColumn"'
      str_value = str_list[:-1]
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      

      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt
      str_value = "5"
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlPrice, \
                                       req_item)
      # API問合せ
      json_return = self.func_api_req(str_url)

      return json_return

  def func_get_and_write_now_price(self):
    req_item = [class_req()]
    my_column = ['']
    my_code = ['']
    str_fname_input = 'price_list_in.csv'
    str_fname_output = 'price_list_out.csv'

    # ファイルから取得する情報コードと銘柄を読み込む。
    self.func_read_price_list(str_fname_input, my_code, my_column)

    # 株価情報の出力ファイルに１行目タイトルを書き込む。
    self.func_write_price_title(str_fname_output, my_column)

    start_time = datetime.datetime.now()    # 開始時刻計測

    str_code_list = ''
    i = 0
    j = 0
    int_set = 0
    # v4r3 より、株価取得は1度に120銘柄までに変更となった。
    while j < len(my_code):
        if len(my_code[j]) > 0 and not my_code[j] == 'stock_code' :
            str_code_list = str_code_list + my_code[j] + ','
        if i >= 119 :
            str_code_list = str_code_list[:-1]
            self.int_p_no += 1
            # 株価を取得。
            json_return = self.func_get_price(self.int_p_no, str_code_list, my_column )
            # 株価情報部分を辞書型で抜き出す。
            dic_return = json_return.get('aCLMMfdsMarketPrice')

            # 取得した株価情報を追記モードでファイルに書き込む。
            self.func_write_price_list(str_fname_output, dic_return, my_column)

            # 120銘柄で初期化            
            i = 0
            int_set = int_set + 1
            str_code_list = ''
        else:
            i = i + 1
        j = int_set * 120 + i
        
    if len(str_code_list) > 0 :
        str_code_list = str_code_list[:-1]
        self.int_p_no += 1
        # 株価を取得。
        json_return = self.func_get_price(self.int_p_no, str_code_list, my_column )

        finish_time = datetime.datetime.now()    # 終了時刻計測
        delta_time = finish_time - start_time
        print('delta_time= ', delta_time, ' ← 株価取得時間')

        # 株価情報部分を辞書型で抜き出す。
        dic_return = json_return.get('aCLMMfdsMarketPrice')

        # 取得した株価情報を追記モードでファイルに書き込む。
        self.func_write_price_list(str_fname_output, dic_return, my_column)


# 「型＋情報コード」から「名前」を取得する
# 引数：型＋情報コード」（string）
# 戻り値：「名前」（string）
# 資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」（api_event_if.pdf）
# p6-9/26 【情報コード一覧】
  def func_code_to_name(self, str_input):
      str_input = self.func_strip_dquot(str_input)
      str_return = ''
      if str_input == 'xLISS':        str_return = '"所属"'         # ShiftJIS文字列を１６進数文字列として設定。（含む半角カナ）
      elif str_input == 'pDPP':       str_return = '"現在値"'        # 
      elif str_input == 'tDPP:T':     str_return = '"現在値時刻"'    # 「HH:MM」
      elif str_input == 'pDPG':       str_return = '"現値前値比較"' # ,「0000」：事象なし「0056」：現値＝前値,「0057」：現値＞前値（↑）,「0058」：現値＜前値(↓),「0059」：中断板寄後の初値「0060」：ザラバ引け（・）,「0061」：板寄引け「0062」：中断引け,「0068」：売買停止引け※（）内は画面表示記号。
      elif str_input == 'pDYWP':      str_return = '"前日比"'        # 
      elif str_input == 'pDYRP':      str_return = '"騰落率"'        # 
      elif str_input == 'pDOP':       str_return = '"始値"'         # 
      elif str_input == 'tDOP:T':     str_return = '"始値時刻"'   # 「HH:MM」
      elif str_input == 'pDHP':       str_return = '"高値"'         # 
      elif str_input == 'tDHP:T':     str_return = '"高値時刻"'   # 「HH:MM」
      elif str_input == 'pDLP':       str_return = '"安値"'         # 
      elif str_input == 'tDLP:T':     str_return = '"安値時刻"'   # 「HH:MM」
      elif str_input == 'pDV':        str_return = '"出来高"'        # 
      elif str_input == 'pQAS':       str_return = '"売気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（ウ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（U）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
      elif str_input == 'pQAP':       str_return = '"売気配値"'    # 
      elif str_input == 'pAV':        str_return = '"売気配数量"'    # 
      elif str_input == 'pQBS':       str_return = '"買気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（カ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（K）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
      elif str_input == 'pQBP':       str_return = '"買気配値"'    # 
      elif str_input == 'pBV':        str_return = '"買気配数量"'    # 
      elif str_input == 'xDVES':      str_return = '"配当落銘柄区分"'    # 「配」：配当権利落、中間配当権利落、期中配当権利落,「」：上記外,※「」内文字を画面表示。
      elif str_input == 'xDCFS':      str_return = '"不連続要因銘柄区分"'    # 「分」：株式分割,「併」：株式併合、減資を伴う併合,「有」：有償,「無」：無償,「預」権利預り証落ち,「ム」：無償割当,「ラ」：ライツオファリング,「」：上記外,※「」内文字を画面表示。
      elif str_input == 'pDHF':       str_return = '"日通し高値フラグ"'    # 「0000」：事象なし,「0071」：ストップ高(S),
      elif str_input == 'pDLF':       str_return = '"日通し安値フラグ"'    # 「0000」：事象なし,「0072」：ストップ安(S), ※（）内は画面表示記号。
      elif str_input == 'pDJ':        str_return = '"売買代金"'    # 
      elif str_input == 'pAAV':       str_return = '"売数量（成行）"'    # 
      elif str_input == 'pABV':       str_return = '"買数量（成行）"'    # 
      elif str_input == 'pQOV':       str_return = '"売-OVER"'    # 
      elif str_input == 'pGAV10':     str_return = '"売-１０-数量"'    # 
      elif str_input == 'pGAP10':     str_return = '"売-１０-値段"'    # 
      elif str_input == 'pGAV9':      str_return = '"売-９-数量"'    # 
      elif str_input == 'pGAP9':      str_return = '"売-９-値段"'    # 
      elif str_input == 'pGAV8':      str_return = '"売-８-数量"'    # 
      elif str_input == 'pGAP8':      str_return = '"売-８-値段"'    # 
      elif str_input == 'pGAV7':      str_return = '"売-７-数量"'    # 
      elif str_input == 'pGAP7':      str_return = '"売-７-値段"'    # 
      elif str_input == 'pGAV6':      str_return = '"売-６-数量"'    # 
      elif str_input == 'pGAP6':      str_return = '"売-６-値段"'    # 
      elif str_input == 'pGAV5':      str_return = '"売-５-数量"'    # 
      elif str_input == 'pGAP5':      str_return = '"売-５-値段"'    # 
      elif str_input == 'pGAV4':      str_return = '"売-４-数量"'    # 
      elif str_input == 'pGAP4':      str_return = '"売-４-値段"'    # 
      elif str_input == 'pGAV3':      str_return = '"売-３-数量"'    # 
      elif str_input == 'pGAP3':      str_return = '"売-３-値段"'    # 
      elif str_input == 'pGAV2':      str_return = '"売-２-数量"'    # 
      elif str_input == 'pGAP2':      str_return = '"売-２-値段"'    # 
      elif str_input == 'pGAV1':      str_return = '"売-１-数量"'    # 
      elif str_input == 'pGAP1':      str_return = '"売-１-値段"'    # 
      elif str_input == 'pGBV1':      str_return = '"買-１-数量"'    # 
      elif str_input == 'pGBP1':      str_return = '"買-１-値段"'    # 
      elif str_input == 'pGBV2':      str_return = '"買-２-数量"'    # 
      elif str_input == 'pGBP2':      str_return = '"買-２-値段"'    # 
      elif str_input == 'pGBV3':      str_return = '"買-３-数量"'    # 
      elif str_input == 'pGBP3':      str_return = '"買-３-値段"'    # 
      elif str_input == 'pGBV4':      str_return = '"買-４-数量"'    # 
      elif str_input == 'pGBP4':      str_return = '"買-４-値段"'    # 
      elif str_input == 'pGBV5':      str_return = '"買-５-数量"'    # 
      elif str_input == 'pGBP5':      str_return = '"買-５-値段"'    # 
      elif str_input == 'pGBV6':      str_return = '"買-６-数量"'    # 
      elif str_input == 'pGBP6':      str_return = '"買-６-値段"'    # 
      elif str_input == 'pGBV7':      str_return = '"買-７-数量"'    # 
      elif str_input == 'pGBP7':      str_return = '"買-７-値段"'    # 
      elif str_input == 'pGBV8':      str_return = '"買-８-数量"'    # 
      elif str_input == 'pGBP8':      str_return = '"買-８-値段"'    # 
      elif str_input == 'pGBV9':      str_return = '"買-９-数量"'    # 
      elif str_input == 'pGBP9':      str_return = '"買-９-値段"'    # 
      elif str_input == 'pGBV10':     str_return = '"買-１０-数量"'    # 
      elif str_input == 'pGBP10':     str_return = '"買-１０-値段"'    # 
      elif str_input == 'pQUV':       str_return = '"買-UNDER"'        # 
      elif str_input == 'pVWAP':      str_return = '"VWAP"'    # 
      elif str_input == 'pPRP':       str_return = '"前日終値"'    # 
      else:                           str_return = 'none'

      return  str_return

##################################################################################

# 機能: 信用新規(制度信用6ヶ月) 買い注文
# 返値： 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 引数1: p_no
# 引数2: 銘柄コード
# 引数3: 市場（現在、東証'00'のみ）
# 引数4: 執行条件
# 引数5: 価格
# 引数6: 株数
# 引数7: 口座属性クラス
  def func_neworder_buy_sinyou_open(self, str_sIssueCode,
                                    str_sSizyouC,
                                    str_sCondition,
                                    str_sOrderPrice,
                                    str_sOrderSuryou,
                                    kaidate=True, hensai=False):
      # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
      # p4/46 No.5 引数名:CLMKabuNewOrder を参照してください。

      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      # 3:買 を指定
      if kaidate:
        str_sBaibaiKubun = '3'          # 12.売買区分  1:売、3:買、5:現渡、7:現引。
        if (hensai):
          str_sBaibaiKubun = '1'
      else:
        str_sBaibaiKubun = '1'          # 12.売買区分  1:売、3:買、5:現渡、7:現引。
        if (hensai):
          str_sBaibaiKubun = '3'

      # 2:新規(制度信用6ヶ月) を指定
      str_sGenkinShinyouKubun = '2'   # 16.現金信用区分     0:現物、
                                      #                   2:新規(制度信用6ヶ月)、
                                      #                   4:返済(制度信用6ヶ月)、
                                      #                   6:新規(一般信用6ヶ月)、
                                      #                   8:返済(一般信用6ヶ月)。
      if (hensai):
        str_sGenkinShinyouKubun = '4'

      # 他のパラメーターをセット
      #str_sZyoutoekiKazeiC            # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
      self.str_sOrderExpireDay = '0'        # 17.注文期日  0:当日、上記以外は、注文期日日(YYYYMMDD)[10営業日迄]。
      self.str_sGyakusasiOrderType = '0'    # 18.逆指値注文種別  0:通常、1:逆指値、2:通常+逆指値
      self.str_sGyakusasiZyouken = '0'      # 19.逆指値条件  0:指定なし、条件値段(トリガー価格)
      self.str_sGyakusasiPrice = '*'        # 20.逆指値値段  *:指定なし、0:成行、*,0以外は逆指値値段。
      self.str_sTatebiType = '*'            # 21.建日種類  *:指定なし(現物または新規) 、1:個別指定、2:建日順、3:単価益順、4:単価損順。
      if (hensai):
        self.str_sTatebiType = '2'
      self.str_sTategyokuZyoutoekiKazeiC =  '*'    # 9.建玉譲渡益課税区分  信用建玉における譲渡益課税区分(現引、現渡で使用)。  *:現引、現渡以外の取引、1:特定、3:一般、5:NISA
      #str_sSecondPassword             # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照     ログインの返信データで設定済み。
      

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # API request区分
      str_key = '"sCLMID"'
      str_value = 'CLMKabuNewOrder'  # 新規注文を指示。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 現物信用区分
      str_key = '"sGenkinShinyouKubun"'    # 現金信用区分
      str_value = str_sGenkinShinyouKubun
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      
      # 注文パラメーターセット
      str_key = '"sIssueCode"'    # 銘柄コード
      str_value = str_sIssueCode
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sSizyouC"'    # 市場C
      str_value = str_sSizyouC
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sBaibaiKubun"'    # 売買区分
      str_value = str_sBaibaiKubun
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      str_key = '"sCondition"'    # 執行条件
      str_value = str_sCondition
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sOrderPrice"'    # 注文値段
      str_value = str_sOrderPrice
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sOrderSuryou"'    # 注文数量
      str_value = str_sOrderSuryou
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 税区分
      str_key = '"sZyoutoekiKazeiC"'  # 税口座区分
      if self.sTokuteiKouzaKubunSinyou == '0':     # 一般口座の場合
          str_value = '3'
      else:   # 特定口座、源泉徴収あり:1、無し:2
          str_value = '1'
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 固定パラメーターセット
      str_key = '"sOrderExpireDay"'    # 注文期日
      str_value = self.str_sOrderExpireDay
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sGyakusasiOrderType"'    # 逆指値注文種別
      str_value = self.str_sGyakusasiOrderType
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sGyakusasiZyouken"'    # 逆指値条件
      str_value = self.str_sGyakusasiZyouken
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sGyakusasiPrice"'    # 逆指値値段
      str_value = self.str_sGyakusasiPrice
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sTatebiType"'    # 建日種類
      str_value = self.str_sTatebiType
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sTategyokuZyoutoekiKazeiC"'     # 9.建玉譲渡益課税区分
      str_value = self.str_sTategyokuZyoutoekiKazeiC
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sSecondPassword"'    # 第二パスワード   APIでは第２暗証番号を省略できない。
      str_value = self.sSecondPassword     # 引数の口座属性クラスより取得
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      str_value = self.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlRequest, \
                                       req_item)

      json_return = self.func_api_req(str_url)
      # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
      # p4-5/46 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。
      
      return json_return      # 注文のjson応答文を返す


##########################################################################

# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p10/46 No.9 CLMShinyouTategyokuList を参照してください。
#
#   9 CLMShinyouTategyokuList
#  1	sCLMID	メッセージＩＤ	char*	I/O	'CLMShinyouTategyokuList'
#  2	sIssueCode	銘柄コード	char[12]	I/O	銘柄コード（6501 等）
#  3	sResultCode	結果コード	char[9]	O	業務処理．エラーコード 0：正常、5桁数字：「結果テキスト」に対応するエラーコード
#  4	sResultText	結果テキスト	char[512]	O	ShiftJis  「結果コード」に対応するテキスト
#  5	sWarningCode	警告コード	char[9]	O	業務処理．ワーニングコード 0：正常、5桁数字：「警告テキスト」に対応するワーニングコード
#  6	sWarningText	警告テキスト	char[512]	O	ShiftJis  「警告コード」に対応するテキスト
#  7	sUritateDaikin	売建代金合計	char[9]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.2。
#							0～9999999999999999、左詰め、マイナスの場合なし
#  8	sKaitateDaikin	買建代金合計	char[16]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.1。
#								0～9999999999999999、左詰め、マイナスの場合なし
#  9	sTotalDaikin	総代金合計	char[16]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.3。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 10	sHyoukaSonekiGoukeiUridate	評価損益合計_売建	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.7。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 11	sHyoukaSonekiGoukeiKaidate	評価損益合計_買建	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.8。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 12	sTotalHyoukaSonekiGoukei	総評価損益合計	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.6。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 13	sTokuteiHyoukaSonekiGoukei	特定口座残高評価損益合計    char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.4。
#									        -999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 14	sIppanHyoukaSonekiGoukei	一般口座残高評価損益合計	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.5。
#									        -999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 15	aShinyouTategyokuList	信用建玉リスト	char[17]	O	以下レコードを配列で設定
# 16-1	sOrderWarningCode	警告コード	char[9]	O	業務処理．ワーニングコード 
#										0：正常、
#										5桁数字：「警告テキスト」に対応するワーニングコード
# 17-2	sOrderWarningText	警告テキスト	char[512]	O	ShiftJis  「警告コード」に対応するテキスト
# 18-3	sOrderTategyokuNumber	建玉番号	char[15]	O	-
# 19-4	sOrderIssueCode	銘柄コード	char[12]	O	-
# 20-5	sOrderSizyouC	市場	char[2]	O	00：東証
# 21-6	sOrderBaibaiKubun	売買区分	char[1]	O	1：売
#   					3：買
#   					5：現渡
#   					7：現引
# 22-7	sOrderBensaiKubun	弁済区分	char[2]	O	00：なし
#   					26：制度信用6ヶ月
#   					29：制度信用無期限
#   					36：一般信用6ヶ月
#   					39：一般信用無期限
# 23-8	sOrderZyoutoekiKazeiC	譲渡益課税区分	char[1]	O	1：特定
#   					3：一般
#   					5：NISA
# 24-9	sOrderTategyokuSuryou	建株数	char[13]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.10。
#								0～9999999999999、左詰め、マイナスの場合なし
# 25-10	sOrderTategyokuTanka	建単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 26-11	sOrderHyoukaTanka	評価単価	char[14]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.13。
#								0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 27-12	sOrderGaisanHyoukaSoneki	評価損益	char[16]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.14。
#								-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 28-13	sOrderGaisanHyoukaSonekiRitu	評価損益率   char[13]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.22。
#								    -999999999.99～9999999999.99、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 29-14	sTategyokuDaikin	建玉代金	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.23。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 30-15	sOrderTateTesuryou	建手数料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.15。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 31-16	sOrderZyunHibu	順日歩	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.16。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 32-17	sOrderGyakuhibu	逆日歩	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.17。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 33-18	sOrderKakikaeryou	書換料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.18。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 34-19	sOrderKanrihi	管理費	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.19。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 35-20	sOrderKasikaburyou	貸株料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.20。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 36-21	sOrderSonota	その他	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.21。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 37-22	sOrderTategyokuDay	建日	char[8]	O	YYYYMMDD,00000000
# 38-23	sOrderTategyokuKizituDay	建玉期日日	char[8]	O	YYYYMMDD、無期限の場合は 00000000
# 39-24	sTategyokuSuryou	建玉数量	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 40-25	sOrderYakuzyouHensaiKabusu	約定返済株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 41-26	sOrderGenbikiGenwatasiKabusu	現引現渡株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 42-27	sOrderOrderSuryou	注文中数量	char[13]    O	0～9999999999999、左詰め、マイナスの場合なし
# 43-28	sOrderHensaiKanouSuryou	返済可能数量	char[13]    O	照会機能仕様書 ２－２．（３）、（２）一覧 No.31。
#								0～9999999999999、左詰め、マイナスの場合なし
# 44-29	sSyuzituOwarine	前日終値	    char[14]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.24。
#						    0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 45-30	sZenzituHi	前日比	    char[14]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.25。
#						    -9999999.9999～99999999.9999、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 46-31	sZenzituHiPer	前日比()      char[7]	O   照会機能仕様書 ２－２．（３）、（２）一覧 No.26。
#						    -999.99～999.99、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 47-32	sUpDownFlag	騰落率Flag     char[2]	O   照会機能仕様書 ２－２．（３）、（２）一覧 No.27 11段階のFlag
#   					            01：+5.01  以上
#   					            02：+3.01  ～+5.00
#   					            03：+2.01  ～+3.00
#   					            04：+1.01  ～+2.00
#   					            05：+0.01  ～+1.00
#   					            06：0 変化なし
#   					            07：-0.01  ～-1.00
#   					            08：-1.01  ～-2.00
#   					            09：-2.01  ～-3.00
#   					            10：-3.01  ～-5.00
#   					            11：-5.01  以下




# --------------------------
# 機能: 信用建玉一覧取得
# 返値: API応答（辞書型）
# 引数1: p_no
# 引数2: 銘柄コード（6501等、'':省略時全銘柄取得）
# 引数3: class_cust_property（request通番）, 口座属性クラス
# 備考:
#       銘柄コードは省略可。
  def func_get_shinyou_tategyoku_list(self,
                                  str_sIssueCode):

      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # コマンド
      str_key = '"sCLMID"'
      str_value = 'CLMShinyouTategyokuList'  # 信用建玉一覧取得
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # 銘柄コード
      str_key = '"sIssueCode"'
      str_value = str_sIssueCode      # 銘柄コード（6501等、'':省略時全銘柄取得）。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      str_value = "5"       # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlRequest, \
                                       req_item)

      json_return = self.func_api_req(str_url)

      return json_return

#信用保証金を取得
  def func_hoshou_shinyou(self):

      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sCLMID"'
      str_value = 'CLMZanRealHosyoukinRitu'  # 
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      str_value = "5"       # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlRequest, \
                                       req_item)

      json_return = self.func_api_req(str_url)

      return json_return

#信用余力を取得
  def func_kanougaku_shinyou(self):

      self.int_p_no += 1
      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(self.int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"sCLMID"'
      str_value = 'CLMZanShinkiKanoIjiritu'  # 信用新規建可能額を指示。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値>指定
      str_value = "5"    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値>指定
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlRequest, \
                                       req_item)

      json_return = self.func_api_req(str_url)

      return json_return

  #株式マスタを更新する
  # 取得するマスター項目の選択（コメント'##'を外して指定。選択は1つのみ。）
  my_sTargetCLMID = 'CLMIssueMstKabu'         # 株式 銘柄マスタ
##my_sTargetCLMID = 'CLMIssueSizyouMstKabu'   # 株式 銘柄市場マスタ
##my_sTargetCLMID = 'CLMIssueMstSak'          # 先物
##my_sTargetCLMID = 'CLMIssueMstOp'           # ＯＰ
##my_sTargetCLMID = 'CLMIssueMstOther'        # 指数、為替、その他
##my_sTargetCLMID = 'CLMOrderErrReason'       # 取引所エラー理由コード
##my_sTargetCLMID = 'CLMDateZyouhou'          # 日付情報
  def func_make_column_CLMIssueMstKabu(self):
      str_column = 'sIssueCode'
      str_column = str_column + ',' + 'sIssueName'
      str_column = str_column + ',' + 'sIssueNameRyaku'
      str_column = str_column + ',' + 'sIssueNameKana'
      str_column = str_column + ',' + 'sIssueNameEizi'
      str_column = str_column + ',' + 'sTokuteiF'
      str_column = str_column + ',' + 'sHikazeiC'
      str_column = str_column + ',' + 'sZyouzyouHakkouKabusu'
      str_column = str_column + ',' + 'sKenriotiFlag'
      str_column = str_column + ',' + 'sKenritukiSaisyuDay'
      str_column = str_column + ',' + 'sZyouzyouNyusatuC'
      str_column = str_column + ',' + 'sNyusatuKaizyoDay'
      str_column = str_column + ',' + 'sNyusatuDay'
      str_column = str_column + ',' + 'sBaibaiTani'
      str_column = str_column + ',' + 'sBaibaiTaniYoku'
      str_column = str_column + ',' + 'sBaibaiTeisiC'
      str_column = str_column + ',' + 'sHakkouKaisiDay'
      str_column = str_column + ',' + 'sHakkouSaisyuDay'
      str_column = str_column + ',' + 'sKessanC'
      str_column = str_column + ',' + 'sKessanDay'
      str_column = str_column + ',' + 'sZyouzyouOutouDay'
      str_column = str_column + ',' + 'sNiruiKizituC'
      str_column = str_column + ',' + 'sOogutiKabusu'
      str_column = str_column + ',' + 'sOogutiKingaku'
      str_column = str_column + ',' + 'sBadenpyouOutputYNC'
      str_column = str_column + ',' + 'sHosyoukinDaiyouKakeme'
      str_column = str_column + ',' + 'sDaiyouHyoukaTanka'
      str_column = str_column + ',' + 'sKikoSankaC'
      str_column = str_column + ',' + 'sKarikessaiC'
      str_column = str_column + ',' + 'sYusenSizyou'              # 優先市場
      str_column = str_column + ',' + 'sMukigenC'
      str_column = str_column + ',' + 'sGyousyuCode'
      str_column = str_column + ',' + 'sGyousyuName'
      str_column = str_column + ',' + 'sSorC'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateDate'
      str_column = str_column + ',' + 'sUpdateNumber'
      return str_column



  def func_make_column_CLMIssueSizyouMstKabu(self):
      str_column = 'sIssueCode'
      str_column = str_column + ',' + 'sZyouzyouSizyou'
      str_column = str_column + ',' + 'sSystemC'
      str_column = str_column + ',' + 'sNehabaMin'
      str_column = str_column + ',' + 'sNehabaMax'
      str_column = str_column + ',' + 'sIssueKubunC'
      str_column = str_column + ',' + 'sNehabaSizyouC'
      str_column = str_column + ',' + 'sSinyouC'
      str_column = str_column + ',' + 'sSinkiZyouzyouDay'
      str_column = str_column + ',' + 'sNehabaKigenDay'
      str_column = str_column + ',' + 'sNehabaKiseiC'
      str_column = str_column + ',' + 'sNehabaKiseiTi'
      str_column = str_column + ',' + 'sNehabaCheckKahiC'
      str_column = str_column + ',' + 'sIssueBubetuC'
      str_column = str_column + ',' + 'sZenzituOwarine'
      str_column = str_column + ',' + 'sNehabaSansyutuSizyouC'
      str_column = str_column + ',' + 'sIssueKisei1C'
      str_column = str_column + ',' + 'sIssueKisei2C'
      str_column = str_column + ',' + 'sZyouzyouKubun'
      str_column = str_column + ',' + 'sZyouzyouHaisiDay'
      str_column = str_column + ',' + 'sSizyoubetuBaibaiTani'
      str_column = str_column + ',' + 'sSizyoubetuBaibaiTaniYoku'
      str_column = str_column + ',' + 'sYobineTaniNumber'
      str_column = str_column + ',' + 'sYobineTaniNumberYoku'
      str_column = str_column + ',' + 'sZyouhouSource'
      str_column = str_column + ',' + 'sZyouhouCode'
      str_column = str_column + ',' + 'sKouboPrice'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateDate'
      str_column = str_column + ',' + 'sUpdateNumber'
      return str_column



  def func_make_column_CLMIssueMstSak(self):
      str_column = 'sIssueCode'
      str_column = str_column + ',' + 'sIssueName'
      str_column = str_column + ',' + 'sIssueNameEizi'
      str_column = str_column + ',' + 'sSakOpSyouhin'
      str_column = str_column + ',' + 'sGensisanKubun'
      str_column = str_column + ',' + 'sGensisanCode'
      str_column = str_column + ',' + 'sGengetu'
      str_column = str_column + ',' + 'sZyouzyouSizyou'
      str_column = str_column + ',' + 'sTorihikiStartDay'
      str_column = str_column + ',' + 'sLastBaibaiDay'
      str_column = str_column + ',' + 'sTaniSuryou'
      str_column = str_column + ',' + 'sYobineTaniNumber'
      str_column = str_column + ',' + 'sZyouhouSource'
      str_column = str_column + ',' + 'sZyouhouCode'
      str_column = str_column + ',' + 'sNehabaMin'
      str_column = str_column + ',' + 'sNehabaMax'
      str_column = str_column + ',' + 'sIssueKisei1C'
      str_column = str_column + ',' + 'sBaibaiTeisiC'
      str_column = str_column + ',' + 'sZenzituOwarine'
      str_column = str_column + ',' + 'sBaDenpyouOutputUmuC'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateDate'
      str_column = str_column + ',' + 'sUpdateNumber'
      return str_column



  def func_make_column_CLMIssueMstOp(self):
      str_column = 'sIssueCode'                       # 銘柄コード
      str_column = str_column + ',' + 'sIssueName'    # 銘柄名
      str_column = str_column + ',' + 'sIssueNameEizi'
      str_column = str_column + ',' + 'sSakOpSyouhin'
      str_column = str_column + ',' + 'sGensisanKubun'    # 原資産区分
      str_column = str_column + ',' + 'sGensisanCode'     # 原資産コード
      str_column = str_column + ',' + 'sGengetu'          # 限月
      str_column = str_column + ',' + 'sZyouzyouSizyou'   # 上場市場
      str_column = str_column + ',' + 'sKousiPrice'       # 行使価格
      str_column = str_column + ',' + 'sPutCall'          # プット・コール
      str_column = str_column + ',' + 'sTorihikiStartDay' # 取引開始日
      str_column = str_column + ',' + 'sLastBaibaiDay'    # 直近売買日
      str_column = str_column + ',' + 'sKenrikousiLastDay'    # 直近権利行使日
      str_column = str_column + ',' + 'sTaniSuryou'       # 単位数量
      str_column = str_column + ',' + 'sYobineTaniNumber' # 呼値単位数
      str_column = str_column + ',' + 'sZyouhouSource'    # 情報ソース
      str_column = str_column + ',' + 'sZyouhouCode'      # 情報コード
      str_column = str_column + ',' + 'sNehabaMin'        # 値幅_最小
      str_column = str_column + ',' + 'sNehabaMax'        # 値幅_最大
      str_column = str_column + ',' + 'sIssueKisei1C'
      str_column = str_column + ',' + 'sZenzituOwarine'   # 前日終値
      str_column = str_column + ',' + 'sZenzituRironPrice'    # 前日理論価格
      str_column = str_column + ',' + 'sBaDenpyouOutputUmuC'  # 場伝票出力有無
      str_column = str_column + ',' + 'sCreateDate'       # 作成日
      str_column = str_column + ',' + 'sUpdateDate'       # 更新日
      str_column = str_column + ',' + 'sUpdateNumber'     # 更新番号
      str_column = str_column + ',' + 'sATMFlag'
      return str_column


# 指数・為替
  def func_make_column_CLMIssueMstOther(self):
      str_column = 'sIssueCode'
      str_column = str_column + ',' + 'sIssueName'
      return str_column


  def func_make_column_CLMDaiyouKakeme(self):
      str_column = 'sSystemKouzaKubun'
      str_column = str_column + ',' + 'sIssueCode'
      str_column = str_column + ',' + 'sTekiyouDay'
      str_column = str_column + ',' + 'sHosyokinDaiyoKakeme'
      str_column = str_column + ',' + 'sDeleteDay'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateNumber'
      str_column = str_column + ',' + 'sUpdateDate'
      return str_column


  def func_make_column_CLMHosyoukinMst(self):
      str_column = 'sSystemKouzaKubun'
      str_column = str_column + ',' + 'sIssueCode'
      str_column = str_column + ',' + 'sZyouzyouSizyou'
      str_column = str_column + ',' + 'sHenkouDay'
      str_column = str_column + ',' + 'sDaiyoHosyokinRitu'
      str_column = str_column + ',' + 'sGenkinHosyokinRitu'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateNumber'
      str_column = str_column + ',' + 'sUpdateDate'
      return str_column


  def func_make_column_CLMDateZyouhou(self):
      str_column = 'sDayKey'
      str_column = str_column + ',' + 'sMaeEigyouDay_1'
      str_column = str_column + ',' + 'sMaeEigyouDay_2'
      str_column = str_column + ',' + 'sMaeEigyouDay_3'
      str_column = str_column + ',' + 'sTheDay'
      str_column = str_column + ',' + 'sYokuEigyouDay_1'
      str_column = str_column + ',' + 'sYokuEigyouDay_2'
      str_column = str_column + ',' + 'sYokuEigyouDay_3'
      str_column = str_column + ',' + 'sYokuEigyouDay_4'
      str_column = str_column + ',' + 'sYokuEigyouDay_5'
      str_column = str_column + ',' + 'sYokuEigyouDay_6'
      str_column = str_column + ',' + 'sYokuEigyouDay_7'
      str_column = str_column + ',' + 'sYokuEigyouDay_8'
      str_column = str_column + ',' + 'sYokuEigyouDay_9'
      str_column = str_column + ',' + 'sYokuEigyouDay_10'
      str_column = str_column + ',' + 'sKabuUkewatasiDay'
      str_column = str_column + ',' + 'sKabuKariUkewatasiDay'
      str_column = str_column + ',' + 'sBondUkewatasiDay'
      return str_column


  def func_make_column_CLMOrderErrReason(self):
      str_column = 'sErrReasonCode'
      str_column = str_column + ',' + 'sErrReasonText'
      return str_column


  def func_make_column_CLMSystemStatus(self):
      str_column = 'sSystemStatusKey'
      str_column = str_column + ',' + 'sLoginKyokaKubun'
      str_column = str_column + ',' + 'sSystemStatus'
      str_column = str_column + ',' + 'sCreateTime'
      str_column = str_column + ',' + 'sUpdateTime'
      str_column = str_column + ',' + 'sUpdateNumber'
      str_column = str_column + ',' + 'sDeleteFlag'
      str_column = str_column + ',' + 'sDeleteTime'
      return str_column


  def func_make_column_CLMYobine(self):
      str_column = 'sYobineTaniNumber'
      str_column = str_column + ',' + 'sTekiyouDay'
      str_column = str_column + ',' + 'sKizunPrice_1'
      str_column = str_column + ',' + 'sKizunPrice_2'
      str_column = str_column + ',' + 'sKizunPrice_3'
      str_column = str_column + ',' + 'sKizunPrice_4'
      str_column = str_column + ',' + 'sKizunPrice_5'
      str_column = str_column + ',' + 'sKizunPrice_6'
      str_column = str_column + ',' + 'sKizunPrice_7'
      str_column = str_column + ',' + 'sKizunPrice_8'
      str_column = str_column + ',' + 'sKizunPrice_9'
      str_column = str_column + ',' + 'sKizunPrice_10'
      str_column = str_column + ',' + 'sKizunPrice_11'
      str_column = str_column + ',' + 'sKizunPrice_12'
      str_column = str_column + ',' + 'sKizunPrice_13'
      str_column = str_column + ',' + 'sKizunPrice_14'
      str_column = str_column + ',' + 'sKizunPrice_15'
      str_column = str_column + ',' + 'sKizunPrice_16'
      str_column = str_column + ',' + 'sKizunPrice_17'
      str_column = str_column + ',' + 'sKizunPrice_18'
      str_column = str_column + ',' + 'sKizunPrice_19'
      str_column = str_column + ',' + 'sKizunPrice_20'
      str_column = str_column + ',' + 'sYobineTanka_1'
      str_column = str_column + ',' + 'sYobineTanka_2'
      str_column = str_column + ',' + 'sYobineTanka_3'
      str_column = str_column + ',' + 'sYobineTanka_4'
      str_column = str_column + ',' + 'sYobineTanka_5'
      str_column = str_column + ',' + 'sYobineTanka_6'
      str_column = str_column + ',' + 'sYobineTanka_7'
      str_column = str_column + ',' + 'sYobineTanka_8'
      str_column = str_column + ',' + 'sYobineTanka_9'
      str_column = str_column + ',' + 'sYobineTanka_10'
      str_column = str_column + ',' + 'sYobineTanka_11'
      str_column = str_column + ',' + 'sYobineTanka_12'
      str_column = str_column + ',' + 'sYobineTanka_13'
      str_column = str_column + ',' + 'sYobineTanka_14'
      str_column = str_column + ',' + 'sYobineTanka_15'
      str_column = str_column + ',' + 'sYobineTanka_16'
      str_column = str_column + ',' + 'sYobineTanka_17'
      str_column = str_column + ',' + 'sYobineTanka_18'
      str_column = str_column + ',' + 'sYobineTanka_19'
      str_column = str_column + ',' + 'sYobineTanka_20'
      str_column = str_column + ',' + 'sDecimal_1'
      str_column = str_column + ',' + 'sDecimal_2'
      str_column = str_column + ',' + 'sDecimal_3'
      str_column = str_column + ',' + 'sDecimal_4'
      str_column = str_column + ',' + 'sDecimal_5'
      str_column = str_column + ',' + 'sDecimal_6'
      str_column = str_column + ',' + 'sDecimal_7'
      str_column = str_column + ',' + 'sDecimal_8'
      str_column = str_column + ',' + 'sDecimal_9'
      str_column = str_column + ',' + 'sDecimal_10'
      str_column = str_column + ',' + 'sDecimal_11'
      str_column = str_column + ',' + 'sDecimal_12'
      str_column = str_column + ',' + 'sDecimal_13'
      str_column = str_column + ',' + 'sDecimal_14'
      str_column = str_column + ',' + 'sDecimal_15'
      str_column = str_column + ',' + 'sDecimal_16'
      str_column = str_column + ',' + 'sDecimal_17'
      str_column = str_column + ',' + 'sDecimal_18'
      str_column = str_column + ',' + 'sDecimal_19'
      str_column = str_column + ',' + 'sDecimal_20'
      str_column = str_column + ',' + 'sCreateDate'
      str_column = str_column + ',' + 'sUpdateDate'
      return str_column







# 機能: 取得するマスターデータの種類により取得項目作成関数に分岐する。
# 引数1: マスターデータ種類
# 返値: 取得項目文字列
# 補足:  'CLMIssueMstKabu'         # 株式 銘柄マスタ
#       'CLMIssueSizyouMstKabu'   # 株式 銘柄市場マスタ
#       'CLMIssueMstSak'          # 先物
#       'CLMIssueMstOp'           # ＯＰ
#       'CLMIssueMstOther'        # 指数、為替、その他
#       'CLMOrderErrReason'       # 取引所エラー理由コード
#       'CLMDateZyouhou'          # 日付情報

  def func_make_sTargetColumn(self,str_sTargetCLMID):
      str_sTargetColumn = ''
      if str_sTargetCLMID == 'CLMIssueMstKabu' :
          str_sTargetColumn = self.func_make_column_CLMIssueMstKabu()
          
      elif str_sTargetCLMID == 'CLMIssueSizyouMstKabu' :
          str_sTargetColumn = self.func_make_column_CLMIssueSizyouMstKabu()
          
      elif str_sTargetCLMID == 'CLMIssueMstSak' :
          str_sTargetColumn = self.func_make_column_CLMIssueMstSak()
          
      elif str_sTargetCLMID == 'CLMIssueMstOp' :
          str_sTargetColumn = self.func_make_column_CLMIssueMstOp()
          
      elif str_sTargetCLMID == 'CLMIssueMstOther' :
          str_sTargetColumn = self.func_make_column_CLMIssueMstOther()
          
      elif str_sTargetCLMID == 'CLMDaiyouKakeme' :
          str_sTargetColumn = self.func_make_column_CLMDaiyouKakeme()
          
      elif str_sTargetCLMID == 'CLMHosyoukinMst' :
          str_sTargetColumn = self.func_make_column_CLMHosyoukinMst()
          
      elif str_sTargetCLMID == 'CLMDateZyouhou' :
          str_sTargetColumn = self.func_make_column_CLMDateZyouhou()
          
      elif str_sTargetCLMID == 'CLMOrderErrReason' :
          str_sTargetColumn = self.func_make_column_CLMOrderErrReason()
          
      elif str_sTargetCLMID == 'CLMSystemStatus' :
          str_sTargetColumn = self.func_make_column_CLMSystemStatus()
          
      elif str_sTargetCLMID == 'CLMYobine' :
          str_sTargetColumn = self.func_make_column_CLMYobine()
              
      return str_sTargetColumn



# 機能： 項目別マスターダウンロード
# 引数1：int_p_no
# 引数2：str_sTargetCLMID
# 引数3：str_sTargetColumn
# 引数4：class_cust_property
# 返値: 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 補足: 項目別のマスターデータ取得は、通常のAPI呼び出し。
#       マスターダウンロード専用（＝ストリーミング形式）の接続は使わない。
# 資料:
# 'sCLMID':'CLMMfdsGetMasterData' の利用方法
# API専用ページ
# ５．マニュアル 
# １．共通説明
# （３）ブラウザからの利用方法
# 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」
# 
# 「マスタ・時価」シート・・・・マスタ情報問合取得、 時価情報問合取得
# ２－２．各Ｉ／Ｆ説明																				
# （１）マスタ情報問合取得																			
#
# マスターデータの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。
  def func_get_master_kobetsu(self, int_p_no, str_sTargetCLMID, str_sTargetColumn, class_cust_property):
      # 送信項目の解説は、マニュアル、（2）インタフェース概要の「立花証券・ｅ支店・ＡＰＩ、インタフェース概要」
      # p7/10 sd 5.マスタダウンロード を参照してください。

      req_item = [class_req()]
      str_p_sd_date = self.func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
      
      str_key = '"p_no"'
      str_value = self.func_check_json_dquat(str(int_p_no))
      #req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = '"p_sd_date"'
      str_value = str_p_sd_date
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)
      
      str_key = 'sCLMID'
      str_value = 'CLMMfdsGetMasterData'  # 。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)


      str_key = 'sTargetCLMID'
      str_value = str_sTargetCLMID  # 。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      str_key = 'sTargetColumn'
      str_value = str_sTargetColumn  # 。
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      
      # 返り値の表示形式指定
      str_key = '"sJsonOfmt"'
      #str_value = class_cust_property.sJsonOfmt
      str_value = "5"
      req_item.append(class_req())
      req_item[-1].add_data(str_key, str_value)

      # URL文字列の作成
      str_url = self.func_make_url_request(False, \
                                       self.sUrlMaster, \
                                       req_item)

      # API問合せ
      json_return = self.func_api_req(str_url)
      # 項目別のマスターデータ取得は、通常のAPI呼び出し。
      # マスターダウンロード専用（＝ストリーミング形式）の呼び出しは使わない。

      return json_return



# 機能: 限月が、当月以後（限月<=当月）ならば、True、当月より前（限月<当月）ならばFalseを返す。
# 
  def func_judge_past_gengetsu(self, list_data):
      bool_judge = True
      
      # システム時刻の取得
      dt_systime = datetime.datetime.now()
      # 当月のyyyymmを取得
      str_tougetsu = str(dt_systime.year) + ('00' + str(dt_systime.month))[-2:]

      if int(list_data.get('sGengetu')) >= int(str_tougetsu) :
          bool_judge = True
      else :
          bool_judge = False

      return bool_judge


# 機能: csv形式でファイルに書き込む
# 返値: 
# 引数1:
# 引数2:
# 備考: 1行目は、タイトル行
#     2行目以降は、データ行 
  def func_write_master_kobetsu(self, str_sTargetCLMID, \
                                json_return, \
                                str_master_filename):
##                              str_sTargetColumn, \
      
      # 返り値からsTargetCLMID内のデータレコードのみ抜き出す
      list_return = json_return.get(str_sTargetCLMID)
          
      try :
              
          with open(str_master_filename, 'w') as fout:
              int_num_of_articles = len(list_return[0].keys())
              iter_keys = iter(list_return[0].keys())
                  
              # タイトル行
              str_text = ''
              for i in range(int_num_of_articles) :
                  str_text = str_text + next(iter_keys) + ','
              str_text = str_text[:-1] + '\n'
              fout.write(str_text)        # タイトル行をファイルに書き込む
                  
              for i in range(len(list_return)):
                  # デフォルトでTrueをセット。
                  # 条件に合わない場合（非上場銘柄、過去の限月）は、以降でFalseをセット。
                  bool_judge = True


                  # 株式
                  # 銘柄マスタ_株       優先市場が 非上場:9 を除外
                  if self.my_sTargetCLMID == 'CLMIssueMstKabu' :
                      if list_return[i].get('sYusenSizyou') == '9' :
                          bool_judge = False

                  # 銘柄市場マスタ_株     上場市場が 非上場:9 を除外
                  if self.my_sTargetCLMID == 'CLMIssueSizyouMstKabu' :
                      if list_return[i].get('sZyouzyouSizyou') == '9' :
                          bool_judge = False
                  
                  # 先物、OPで過去の限月を削除する
                  if self.my_sTargetCLMID == 'CLMIssueMstSak' \
                     or self.my_sTargetCLMID == 'CLMIssueMstOp' :
                      bool_judge = self.func_judge_past_gengetsu(list_return[i])

                  if bool_judge :
                      iter_values = iter(list_return[i].values())
                  
                      str_text = ''
                      for n in range(int_num_of_articles) :
                          str_text = str_text +  next(iter_values) + ','
                      str_text = str_text[:-1] + '\n'
                      fout.write(str_text)        # データを1行ファイルに書き込む
              
      except IOError as e:
          print('File can not write!!!')
          print(type(e))


# 出力ファイル名の設定
  my_master_filename = 'master_' + my_sTargetCLMID +'.csv'
  def update_master_kabu(self):
    # 取得項目名を作成
    my_sTargetColumn = self.func_make_sTargetColumn(self.my_sTargetCLMID)

    self.int_p_no += 1

    json_return = self.func_get_master_kobetsu(self.int_p_no, self.my_sTargetCLMID, my_sTargetColumn, "5")
    # マスターデータの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。
    # カレントディレクトリに「str_master_filename」で指定した名前でファイルを作成する。

    # csv形式でファイルへの書き出し
    self.func_write_master_kobetsu(self.my_sTargetCLMID, json_return, self.my_master_filename)

