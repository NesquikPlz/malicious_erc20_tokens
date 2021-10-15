from numpy.core.arrayprint import IntegerFormat
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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
    sleep(0.15)

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
top100token

scam_dataset = pd.DataFrame()



k=1
#이제 하나씩 사칭토큰 모으기                    
for x in official_token['tokenname'] :
    k = k + 1
    print(k)
    if k<=65 :
        continue
    sleep(0.2)
    token_x = top100token[top100token['tokenname']==x]
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
    for i in range(1, 50) : #한페이지에 오십개있음
        xpath_tokenname = '/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[3]/table/tbody/tr[{}]/td[2]'.format(i)
        xpath_token_symbol = '/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[3]/table/tbody/tr[{}]/td[3]'.format(i)
        try :
            tokenname = browser.find_element_by_xpath(xpath_tokenname)
            action = ActionChains(browser)
            action.move_to_element(tokenname).perform()
            tokenname = tokenname.text

            token_symbol = browser.find_element_by_xpath(xpath_token_symbol)
            token_symbol = token_symbol.text
            xpath_contractaddress = '/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[3]/table/tbody/tr[{}]/td[1]/span/a'.format(i)
            contractaddress = browser.find_element_by_xpath(xpath_contractaddress)
            address = contractaddress.text
        except NoSuchElementException:
            i = 50
            continue
        if x in tokenname :
            contractaddress.click()
            sleep(1)
            xholders = '/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div/div'
            xt = '/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/span'
            try:
                holders = browser.find_element_by_xpath(xholders)
                holders = holders.text
                holders = holders.split(' (')[0]
                holders = holders.replace(",","")
            except NoSuchElementException:
                holders = '-1'

            try:
                transfers = browser.find_element_by_xpath(xt)
                transfers = transfers.text
                transfers = transfers.replace(",","")
            except NoSuchElementException:
                transfers = '-1'

            holders = int(holders)
            transfers = int(transfers)

            token_x = top100token[top100token['tokenname']==x]
            contract_official = token_x['contract']
            if transfers<15 and transfers > -1 :
                print(tokenname, 'has not enough transactions : ', transfers)
            else :
                new_scam = {'tokenname': tokenname, 'symbol': token_symbol, 'holders': holders, 'transfers' : transfers, 'contract': address}
                print(new_scam)
                scam_dataset = scam_dataset.append(new_scam, ignore_index=True)
            browser.back()     
    browser.back()#일단 오십개씩만해보기 

    #한페이지 다했으면 다음페이지로 가기(4페이지 까지만)
    # next_page = browser.find_element_by_xpath('/html/body/div[1]/main/div[3]/div[1]/div[2]/div/div/div[1]/nav/ul/li[4]/a')
    # action = ActionChains(browser)
    # action.move_to_element(next_page).perform()
    # if j<4 :
    #     next_page.click()
    # else :
    #     j = 1;

        
print(scam_dataset)
scam_dataset = scam_dataset.drop_duplicates(subset=None, keep='first')
scam_dataset.to_csv('scam.csv')
official_token.to_csv('official.csv')

rest_officials = ['uniswap','Compound Ether','Crypto.com Coin','Compound USD Coin','Graph Token','Celsius','Amp','OMG Network','Compound','Synthetix Network Token','chiliZ','HoloToken','EnjinCoin','Telcoin','Pax Dollar','Polymath','UMA Voting Token v1','Livepeer Token','WAX Token','Gnosis','DENT','Injective Token','Paxos Gold']