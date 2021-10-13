from selenium import webdriver
from selenium.webdriver import ActionChains
import numpy as np
import pandas as pd
from time import sleep

official_token = pd.DataFrame()

#크롬웹드라이버다운받아야지 실행될걸?
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)
browser.get("https://etherscan.io/tokens")

token_name = []
token_holder = []

#top100토큰 가져오기, 코드 실행시킬때 한번에 100개 보이도록 페이지 수정해야됨
lists_name = browser.find_elements_by_class_name('text-primary')
for list in lists_name :
    token_name.append(list.text)

for i in range(1,101):
    xpath = '//*[@id="tblResult"]/tbody/tr[{}]/td[7]'.format(i)
    Holders = browser.find_element_by_xpath(xpath)
    str = Holders.text
    if '\n' in str :
        str = str.split('\n')[0]
        # print(">>>>  ", str)
        token_holder.append(str)
        continue;
    # print(">>>>  ", str)
    token_holder.append(str)

# token_name
# token_holder
official_token['coinname'] = token_name
official_token['holders'] = token_holder

#토큰 이름이랑 심볼 분리하기
token = official_token['coinname'].apply(lambda x : x.split(' (')[0])
symbol = official_token['coinname'].apply(lambda x : x.split(' (')[1])

official_token['tokenname'] = token
official_token['symbol'] = symbol

str = ")"   #헷갈려서 변수로 뺌
official_token['symbol'] = official_token['symbol'].apply(lambda x : x.split(str)[0])

official_token = official_token.drop(columns = ['coinname'])
official_token['id'] = official_token.index
official_token = official_token[['id', 'tokenname', 'symbol', 'holders']]

namelist = []
contract = []

#top100토큰 컨트랙트주소 가져오기
for i in range(1,101):
    xpath = '//*[@id="tblResult"]/tbody/tr[{}]/td[2]/div/div/h3/a'.format(i)
    token = browser.find_element_by_xpath(xpath)
    action = ActionChains(browser)
    action.move_to_element(token).perform()

    print(token.text)
    namelist.append(token.text)
    token.click()
    contract_address = browser.find_element_by_xpath('/html/body/div[1]/main/div[4]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/a[1]')
    print(contract_address.text)
    contract.append(contract_address.text)
    browser.back()
    sleep(0.5)

namelist
contract

#top100token은 100개 다있고 official_token은 홀더 10000명 넘는애들만 둔거
top100token = official_token
top100token['fullname'] = namelist
top100token['contract'] = contract

official_token['holders'] = official_token['holders'].apply(lambda x : x.replace(",",""))
official_token['holders'] = official_token['holders'].astype('int32')
official_token = official_token[official_token['holders']>=10000]

official_token.info()


#이제 하나씩 사칭토큰 모으기
#
