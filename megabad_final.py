# import os
# import requests

# headers = {
#     'authority': 'www.argos.co.uk',
#     'cache-control': 'max-age=0',
#     'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
#     'sec-ch-ua-mobile': '?0',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'service-worker-navigation-preload': 'true',
#     'sec-fetch-site': 'none',
#     'sec-fetch-mode': 'navigate',
#     'sec-fetch-user': '?1',
#     'sec-fetch-dest': 'document',
#     'accept-language': 'en-US,en;q=0.9,hi;q=0.8',

# }

# response = requests.get('https://www.argos.co.uk/search/smart-tv/smart-tv:yes/opt/sort:customer-rating/',
#                         headers=headers)


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
ua = UserAgent(verify_ssl=False)

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

path = '/Users/hari/Documents/hari/Crisil/Reuter_31_05/'


proxy_list = pd.read_excel(path+"proxy.xlsx")['proxy'].tolist()

def get_proxy():
    proxy = random.choice(proxy_list)

    http_proxy = "http://Vijaysrini:Rtrmba@2020@{}".format(proxy)
    https_proxy = "http://Vijaysrini:Rtrmba@2020@{}".format(proxy)


    proxyDict = {
                  "http": http_proxy,
                  "https": https_proxy
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
        delivery = response.xpath('//div[contains(@class,"label delivery delivery")]//text()').extract_first().strip()
    except:
        delivery = 'NA'
    print('\n')
    return ([supp, i, sku, title, price_req, orig_price_req, saving_price_req, m_ean, "\""+product_model+"\"", mf_name_req, mf_series,delivery])

def get_response(i):
    retry_var = 0
    resp = ''
    while retry_var <= 10:
        try:
            headers['User-Agent'] = ua.random
            # time.sleep(random.randint(0, 2))
            # resp = requests.get(i, verify=False,headers=headers, proxies=get_proxy())
            resp = requests.get(i, verify=False, headers=headers, proxies=get_proxy())
            print(resp.status_code)
            if resp.status_code == 200:
                time.sleep(random.randint(0, 2))
                print("using proxy")
                break
            else:
                retry_var += 1
                time.sleep(random.randint(0, 2))
                print("=========>>>In else section Retrying again=======>>>{}".format(retry_var))
                # continue
        except:
            print("Retrying")
            retry_var += 1
            time.sleep(random.randint(0, 1))
    if retry_var == 11:
        writer.writerow(
            ["missing value", i, resp, "missing value", "missing value", "missing value", "missing value",
             "missing value", "missing value", "missing value", "missing value", "missing value"])
        print("missing value===>>>{}".format(i))
        resp = 0
    return resp

url_list = pd.read_excel(path+"megabad_all_links.xlsx")['Product_url'].tolist()
url_list = url_list[20000:30000]

with open(path+'megabad_20k_30K.csv', 'w', newline='', encoding='utf-8-sig') as file:
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
