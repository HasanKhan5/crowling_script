import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import Global_var
from scrap import *

def chromdriver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://www.ocenchik.ru/tender/?lim=0')
    time.sleep(5)

    getAttempt = 0
    while True:
        varify_data = driver.find_elements(By.XPATH,'/html/body/table[2]/tbody/tr/td[2]/a/img')
        if len(varify_data) == 0:
            getAttempt+=1
            time.sleep(2)
            if getAttempt > 5:
                driver.get('https://www.ocenchik.ru/tender/?lim=0')
            continue
        else:
            break
    time.sleep(1)
    collect_links(driver)

def collect_links(driver):
    link_list = []
    element_page = True
    while element_page:
        try:
            for _ in driver.find_elements(By.XPATH,'/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr'):
                xpath = f'(/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr[{Global_var.tr}]/td[1]/span/a)'
                link_href = driver.find_element(By.XPATH, xpath).get_attribute('href')
                print(link_href)
                short_desc = driver.find_element(By.XPATH, xpath).get_attribute('innerText')
                Contract_price = driver.find_element(By.XPATH, f'/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr[{Global_var.tr}]/td[5]').get_attribute('innerText')
                open_close_date = driver.find_element(By.XPATH, f'/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr[{Global_var.tr}]/td[4]/font').get_attribute('innerText')
                publish_date = open_close_date.partition('\n')[0]
                closing_date = open_close_date.partition('\n')[2]
                if not closing_date:
                    Global_var.tr += 1
                    continue
                datetime_object = datetime.strptime(closing_date, '%d.%m.%Y')
                deadline = datetime_object.strftime('%Y-%m-%d')
                day = (datetime.strptime(publish_date, "%d.%m.%Y").date() - datetime.strptime(Global_var.fromdate, '%d-%m-%Y').date()).days
                if day >= 0:
                    link_list.append({'link':link_href, 'short_desc':short_desc, 'Contract_price':Contract_price, 'publish_date':publish_date, 'deadline':deadline})
                    Global_var.tr += 1
                else:scrap(link_list,driver) 
            element_page = False     
        except Exception as e:
            print('next page')

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_page = f'https://www.ocenchik.ru/tender/?lim={Global_var.page}'
            driver.get(next_page), time.sleep(5)
            Global_var.page += 1
            Global_var.tr = 2       
        except Exception as e:
            print(e)
chromdriver()