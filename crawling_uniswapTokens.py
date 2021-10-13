from numpy.core.arrayprint import IntegerFormat
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

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

wordd = ")"   #헷갈려서 변수로 뺌
official_token['symbol'] = official_token['symbol'].apply(lambda x : x.split(wordd)[0])

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
    sleep(0.3)

namelist
contract

#top100token은 100개 다있고 official_token은 홀더 10000명 넘는애들만 둔거
top100token = official_token
top100token['fullname'] = namelist
top100token['contract'] = contract

official_token['holders'] = official_token['holders'].apply(lambda x : x.replace(",",""))
official_token['holders'] = official_token['holders'].astype('int32')
official_token = official_token[official_token['holders']>=10000]

official_token

scam_dataset = pd.DataFrame()

#이제 하나씩 사칭토큰 모으기
def find_scam(x) : #x는 토큰이름
    global top100token    
    token_x = top100token[top100token['tokenname']=='BNB']
    symbol_official = token_x['symbol']
    xpath = '/html/body/div[1]/main/div[3]/div[1]/div[1]/div[2]/div/a'
    sleep(0.3)
    search = browser.find_element_by_xpath(xpath)
    search.click()

    #토큰이름 검색
    input_xpath = '/html/body/div[1]/main/div[3]/div[1]/div[1]/div[2]/div/div/form/input'
    input = browser.find_element_by_xpath(input_xpath)
    input.send_keys(x)
    input.send_keys(Keys.RETURN)
    j = 1 #페이지
    for i in range(1, 51) : #한페이지에 오십개있음
        xpath_tokenname = '/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[3]/table/tbody/tr[{}]/td[2]'.format(i)
        xpath_token_symbol = '/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[3]/table/tbody/tr[{}]/td[3]'.format(i)
        tokenname = browser.find_element_by_xpath(xpath_tokenname)
        browser.execute_script('window.scrollTo(0, 100)')
        action = ActionChains(browser)
        action.move_to_element(tokenname).perform()
        token_symbol = browser.find_element_by_xpath(xpath_token_symbol)
        if x in tokenname.text and token_symbol == symbol_official:
            tokenname.click()
            holders, transfers = get_token_info(tokenname.text)
            if holders != -1 :
                new_scam = {'tokenname': tokenname.text, 'symbol': token_symbol, 'holders': holders, 'transfers' : transfers, 'contract': contract}
                scam_dataset = scam_dataset.append(new_scam)
    #한페이지 다했으면 다음페이지로 가기(4페이지 까지만)
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    next_page = browser.find_element_by_class_name('page-link')
    if j<4 :
        next_page.click()
    else :
        j = 1;
        browser.execute_script('window.scrollTo(0, 100)')

def get_token_info(x) : #토큰 페이지에서 정보 가져오기
    global scam_dataset
    global top100token
    browser.execute_script('window.scrollTo(0, 100)')
    holders = int(browser.find_element_by_class_name('mr-3').text)
    transfers = int(browser.find_element_by_id('totaltxns').text)
    contract = browser.find_element_by_xpath('/html/body/div[1]/main/div[4]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div/a[1]').text
    token_x = top100token[top100token['tokenname']=='BNB']
    contract_official = token_x['contract']

    if transfers<15 :
        print(x, 'has not enough transactions : ', transfers)
        browser.back()
        return -1, -1, -1
    if contract == contract_official :
        browser.back()
        return -1, -1, -1
    browser.back()
    return holders, transfers, contract

find_scam('BNB')



official_token['tokenname'].apply(lambda x: find_scam(x))
print(scam_dataset)
