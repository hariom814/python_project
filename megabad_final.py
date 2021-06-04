# -*- coding: utf-8 -*-
from openpyxl import Workbook
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

path = '/home/master/Ibex/megabad'


proxy_list = pd.read_excel(path+"/proxy.xlsx")['proxy'].tolist()

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
    return ([supp, i, sku, title, price_req, orig_price_req, saving_price_req, m_ean, product_model, mf_name_req, mf_series,delivery])

def get_response(i):
    retry_var = 0
    resp = ''
    while retry_var <= 10:
        try:
            headers['User-Agent'] = ua.random
            # time.sleep(random.randint(0, 2))
            resp = requests.get(i, verify=False,headers=headers, proxies=get_proxy())
            # resp = requests.get(i, verify=False, headers=headers)
            print(resp.status_code)
            if resp.status_code == 200:
                # time.sleep(random.randint(0, 15))
                print("using proxy")
                break
            else:
                retry_var += 1
                # time.sleep(random.randint(0, 2))
                print("=========>>>In else section Retrying again=======>>>{}".format(retry_var))
                continue
        except:
            print("Retrying")
            retry_var += 1
            time.sleep(random.randint(0, 1))
    if retry_var == 5:
        writer.writerow(
            ["missing value", i, resp, "missing value", "missing value", "missing value", "missing value",
             "missing value", "missing value", "missing value", "missing value", "missing value"])
        print("missing value===>>>{}".format(i))
        resp = 0
    return resp



url_list = pd.read_excel(path+"/megabad_all_links.xlsx")['Product_url'].tolist()
url_list = url_list[:20000]

# with open(path+'final_mega_product_page_data_1_7k.csv', 'w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(["Supplier_ID", "URL","SKU", "Title", "Price", "Original Price", "Savings", "Manufacturer_EAN", "Products_Model", "Manufacturer_name", "Manufacturer_Series", "Shipping_Time"])

file_name = path + "/megabad_1_20K.xlsx"
book = Workbook()
sheet = book.active

sheet['A1'] = "Supplier_ID"
sheet['B1'] = "URL"
sheet['C1'] = "SKU"
sheet['D1'] = "Title"
sheet['E1'] = "Price"
sheet['F1'] = "Original Price"
sheet['G1'] = "Savings"
sheet['H1'] = "Manufacturer_EAN"
sheet['I1'] = "Products_Model"
sheet['J1'] = "Manufacturer_name"
sheet['K1'] = "Manufacturer_Series"
sheet['L1'] = "Shipping_Time"
book.save(file_name)

for i in range(0,len(url_list)):
    print(url_list[i])
    resp = get_response(url_list[i])
    if resp == 0:
        continue
    response = Selector(text=resp.text)
    data_main = get_crawl(response,url_list[i])
    # writer.writerow(data_main)
    sheet['A{}'.format(i+2)] = data_main[0]
    sheet['B{}'.format(i+2)] = data_main[1]
    sheet['C{}'.format(i+2)] = data_main[2]
    sheet['D{}'.format(i+2)] = data_main[3]
    sheet['E{}'.format(i+2)] = data_main[4]
    sheet['F{}'.format(i+2)] = data_main[5]
    sheet['G{}'.format(i+2)] = data_main[6]
    sheet['H{}'.format(i+2)] = data_main[7]
    sheet['I{}'.format(i+2)] = data_main[8]
    sheet['J{}'.format(i+2)] = data_main[9]
    sheet['K{}'.format(i+2)] = data_main[10]
    sheet['L{}'.format(i+2)] = data_main[11]
    book.save(file_name)
    try:
        var_id = list(filter(None, list(set(re.findall('varid=(.*?)\"', resp.text)))))
    except:
        var_id = []
    if var_id:
        for id in range(0,len(var_id)):
            link = url_list[i]+"?varid={}".format(var_id[id])
            resp = get_response(link)
            if resp == 0:
                continue
            response = Selector(text=resp.text)
            data_main1 = get_crawl(response,link)
            # writer.writerow(data_main1)
            sheet['A{}'.format(i + id + 3)] = data_main1[0]
            sheet['B{}'.format(i + id + 3)] = data_main1[1]
            sheet['C{}'.format(i + id + 3)] = data_main1[2]
            sheet['D{}'.format(i + id + 3)] = data_main1[3]
            sheet['E{}'.format(i + id + 3)] = data_main1[4]
            sheet['F{}'.format(i + id + 3)] = data_main1[5]
            sheet['G{}'.format(i + id + 3)] = data_main1[6]
            sheet['H{}'.format(i + id + 3)] = data_main1[7]
            sheet['I{}'.format(i + id + 3)] = data_main1[8]
            sheet['J{}'.format(i + id + 3)] = data_main1[9]
            sheet['K{}'.format(i + id + 3)] = data_main1[10]
            sheet['L{}'.format(i + id + 3)] = data_main1[11]
            book.save(file_name)