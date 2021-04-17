def yu_login_kabutan(uname, passwd):
  session = requests.session()
  url="https://account.kabutan.jp/login"
  #html = urllib.request.urlopen(url).read()
  res = session.get(url)
  html = res.content
  soup = BeautifulSoup(html,"html.parser")
  input_email = soup.select("#session_email")
  input_passwd = soup.select("#session_password")
  authenticity_token = soup.find('input', attrs={'name':'authenticity_token', 'type':'hidden'})
  #print("TOKEN")
  #print(authenticity_token['value'])
  #print("TOKEN end")
  # ログイン
  login_info = {
    "session[email]":uname,
    "session[password]":passwd,
    "authenticity_token":authenticity_token['value'],
    "session[remember_me]":"0"
  }
  # action
  url_login = url
  res = session.post(url_login, data=login_info)
  res.raise_for_status()
  #print(res.text)
  if "/logout" in res.text:
    #print("ログイン成功")
    return True
  return False
