# -*- coding: utf-8 -*-
from scrapy import Selector
import traceback
import csv
import time
import pandas as pd
import requests
import random
import re
from fake_useragent import UserAgent
ua = UserAgent()

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'en-US,en;q=0.9',
}

path = 'D:/reuter/Akshat/megabad_product_page/'

# path = "D:\\reuter"

proxy_list = pd.read_excel(path+"proxy.xlsx")['proxy'].tolist()

def get_proxy():
    proxy = random.choice(proxy_list)

    http_proxy = "http://{}".format(proxy)
    https_proxy = "https://{}".format(proxy)


    proxyDict = {
                  "http": http_proxy
                  # "https": https_proxy
                }
    return proxyDict

def get_crawl(response,i):
    supp = 1
    sku = i.split('-')[-1].split('.')[0]
    try:
        title = response.xpath('//div[@class="col-xs-12 col-md-12"]//h1//text()').extract_first()
    except:
        title = 'NA'
    try:
        price = response.xpath('//div[@class="price-tag price-new"]//text()').extract_first().strip()
        price_req = price.replace('.', '')
        price_req = price_req.replace(',', '.')
    except:
        price_req = 'NA'
    try:
        orig_price = response.xpath(
            '//div[*[contains(text(), "UVP")]]/div[2]/span[1]//text()').extract_first().strip()
        orig_price_req = orig_price.replace('.', '')
        orig_price_req = orig_price_req.replace(',', '.')
    except:
        orig_price_req = 'NA'
    try:
        saving_price = response.xpath(
            '//div[*[contains(text(), "Sie sparen zur UVP")]]//following::div[2]//text()').extract_first().strip()
        saving_price_req = saving_price.replace('.', '')
        saving_price_req = saving_price.replace(',', '.')
    except:
        saving_price_req = 'NA'
    m_ean = 'NA'
    try:
        product_model = str(
            response.xpath('//div[@class="text-paragraph2 word-wrap"]//text()').extract_first().strip())
    except:
        product_model = 'NA'
    mf_name_req = 'NA'
    try:
        mf_name = response.xpath('//div[*[contains(text(), "Marke")]]/div[2]/text()')
        if len(mf_name) == 1:
            mf_name_req = mf_name[0].extract().strip()
        else:
            mf_name_req = mf_name[-1].extract().strip()
        print(mf_name_req)
    except:
        mf_name_req = 'NA'
    try:
        mf_series = response.xpath('//div[*[contains(text(), "Serie")]]/div[2]/text()').extract_first().strip()
    except:
        mf_series = 'NA'
    try:
        delivery = response.xpath('//div[@class="label delivery delivery_2"]/text()').extract_first().strip()
    except:
        delivery = 'NA'
    print('\n')
    return ([supp, i, sku, title, price_req, orig_price_req, saving_price_req, m_ean, product_model, mf_name_req, mf_series,delivery])

def get_response(i):
    retry_var = 0
    while retry_var <= 4:
        try:
            headers['User-Agent'] = ua.random
            time.sleep(random.randint(0, 1))
            resp = requests.get(i, verify=False,headers=headers, proxies=get_proxy())
            print(resp.status_code)
            print("using proxy")
            break
        except:
            print("Retrying")
            retry_var += 1
            time.sleep(random.randint(1, 6))
    if retry_var == 5:
        writer.writerow(
            ["missing value", i, resp.status_code, "missing value", "missing value", "missing value", "missing value",
             "missing value", "missing value", "missing value", "missing value", "missing value"])
        print("missing value===>>>{}".format(i))
        resp = 0
    return resp

url_list = pd.read_excel(path+"Final_megabad.xlsx")['Product_url'].tolist()


with open(path+'mega_product_page_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Supplier_ID", "URL","SKU", "Title", "Price", "Original Price", "Savings", "Manufacturer_EAN", "Products_Model", "Manufacturer_name", "Manufacturer_Series", "Shipping_Time"])
    for i in url_list:
        print(i)
        resp = get_response(i)
        if resp == 0:
            continue
        response = Selector(text=resp.text)
        data_main = get_crawl(response,i)
        writer.writerow(data_main)
        try:
            var_id = list(filter(None, list(set(re.findall('varid=(.*?)\"', resp.text)))))
        except:
            var_id = []
        if var_id:
            for id in var_id:
                link = i+"?varid={}".format(id)
                resp = get_response(link)
                if resp == 0:
                    continue
                response = Selector(text=resp.text)
                data_main1 = get_crawl(response,link)
                writer.writerow(data_main1)
                
# https://www.megabad.com/hersteller-steinberg-ersatzteile-ersatzpumpe-zu-seifenspender-a-179567.htm
# https://www.megabad.com/hersteller-steinberg-ersatzteile-ersatzbuerstenkopf-schwarz-a-94425.htm
# https://www.megabad.com/steinberg-accessoires-serie-450-handtuchhalter-a-78991.htm
# https://www.megabad.com/hersteller-steinberg-bad-accessoires-serie-460-a-79017.htm
# https://www.megabad.com/steinberg-accessoires-serie-650-reservepapierhalter-a-79151.htm

