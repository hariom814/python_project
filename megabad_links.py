from scrapy import Selector
import traceback
import csv
import time
import pandas as pd
import requests
import random
from fake_useragent import UserAgent


path = '/Users/hari/Documents/hari/Crisil/Reuter'


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
brand_url = []
product_url = []

def crawl_links(all_links):
    b_url = all_links
    print(b_url)
    page = 1
    while True:
        print("============page no.======>>{}".format(page))
        retry = 0
        while retry < 10:
            try:
                # headers['user-agent'] = ua.random
                # response = requests.get(all_product_url[i], verify=False, proxies=get_proxy())
                brand_response = requests.get(b_url + '?page={}'.format(page), verify=False,proxies=get_proxy())
                print(brand_response.status_code)
                if brand_response.status_code == 200:
                    print("using proxy")
                    break
                else:
                    retry += 1
                    time.sleep(1)
                    print("=========>>>In else section Retrying again=======>>>{}".format(retry))
                    continue

            except:
                traceback.print_exc()
                retry = 5
                continue

        brand_data = Selector(text=brand_response.text)
        try:
            p_url = brand_data.xpath('//div[@class="row grid grid_katalog t-container"]/div')
            for i in p_url:
                p_url_temp = i.xpath('.//a/@href').extract_first()
                product_url.append(p_url_temp)
                writer.writerow([b_url, p_url_temp, page])
        except:
            pass
        if page == 1:
            total_page = 1
            try:
                total_page = int(brand_data.xpath('//li[@class="pagination-last"]/a/@href').extract_first().split('=')[-1])
                print(total_page)
            except:
                pass

        page += 1
        if page > total_page:
            break




def crawl_sub_brand(all_brand):
    temp_sub_brand = all_brand
    retry = 0
    while retry < 5:
        sub_brand_selector = requests.get(all_brand, verify=False, proxies=get_proxy())
        if sub_brand_selector.status_code == 200:
            print("success")
            break
        else:
            print(sub_brand_selector.status_code)
            retry += 1

    sub_brand_response = Selector(text=sub_brand_selector.text)
    try:
        sub_brand = sub_brand_response.xpath('//div[@class="m-t-15"]//a/@href').extract()
        if len(sub_brand) > 0:
            temp_sub_brand = sub_brand
            for i in sub_brand:
                crawl_sub_brand(i)
    except:
        try:
            all_links = temp_sub_brand

        except:
            pass
    if len(sub_brand) == 0:
        crawl_links(temp_sub_brand)


with open(path + '/megabad_links.csv', 'w', newline='', encoding="UTF-8") as file:

    writer = csv.writer(file)
    writer.writerow(["Url", "Product_url", "Page"])
    retry = 0
    while retry < 5:
        all_brand_selector = requests.get('https://www.megabad.com/marken-k-73105.htm', verify=False,proxies=get_proxy())
        if all_brand_selector.status_code == 200:
            print("success")
            break
        else:
            print(all_brand_selector.status_code)
            print("====== retrying")
            retry += 1

    all_brand_response = Selector(text=all_brand_selector.text)
    all_brand = all_brand_response.xpath('//a[@class="hersteller-link"]/@href').extract()
    for brand in all_brand[:1]:
        retry1 = 0
        while retry1 < 5:

            sub_brand_selector = requests.get(brand, verify=False,proxies=get_proxy())
            if sub_brand_selector.status_code == 200:
                print("success")
                break
            else:
                print(sub_brand_selector.status_code)
                print("====== retrying")
                retry1 += 1
        sub_brand_response = Selector(text=sub_brand_selector.text)
        sub_brand = sub_brand_response.xpath('//div[@class="m-t-15"]//a/@href').extract()
        for i in sub_brand:
            all_links = []
            crawl_sub_brand(i)



    print('Hi')


# print("Completed")

