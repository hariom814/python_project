from scrapy import Selector
import traceback
import csv
import time
import pandas as pd
import requests
import random

path = "/home/master/Ibex/megabad"

# path = "D:\\reuter"

proxy_list = pd.read_excel(path+"/proxy.xlsx")['proxy'].tolist()

def get_proxy():
    proxy = random.choice(proxy_list)

    http_proxy = "http://{}".format(proxy)
    https_proxy = "https://{}".format(proxy)


    proxyDict = {
                  "http": http_proxy
                  # "https": https_proxy
                }
    return proxyDict
brand_url = []
product_url = []

# data_range = ['b','c','d','e','f']
data_range = ['b','c','d','e','f','g','i','j','k','l','m','n','o','p','q','r','s','t','u','w','x','y','z']
for d_range in data_range:
    sitemap = "https://www.megabad.com/sitemap/{}".format(d_range)

    retry1 = 0
    while retry1 < 10:
        try:
            # response = requests.get(all_product_url[i], verify=False, proxies=get_proxy())
            site_response = requests.get(sitemap,verify=False,proxies=get_proxy())
            print(site_response.status_code)
            time.sleep(random.randint(0, 5))
            # time.sleep(random.randint(0,2))
            print("Using proxy")
            break
        except:
            traceback.print_exc()
            retry1 += 1
    site_data = Selector(text=site_response.text)
    for i in site_data.xpath('//ul[@class="default-list text-paragraph2-semibold m-t-20"]/li//a'):
        brand_url.append(i.xpath('.//@href').extract_first())

    with open(path+'/megabad_links.csv', 'w', newline='',encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Url", "Product_url","Page"])
        for b_url in brand_url:
            if b_url == 'https://www.megabad.com/hersteller-aeg-durchlauferhitzer-k-149867.htm':
                print('available')
            print(b_url)
            page = 1
            while True:
                print("============page no.======>>{}".format(page))
                retry = 0
                while retry < 10:
                    try:
                        # response = requests.get(all_product_url[i], verify=False, proxies=get_proxy())
                        brand_response = requests.get(b_url + '?page={}'.format(page), verify=False, allow_redirects=False,proxies=get_proxy())
                        print(brand_response.status_code)
                        time.sleep(random.randint(0, 5))
                        # time.sleep(random.randint(0,5))
                        print("Using proxy")
                        break
                    except:
                        traceback.print_exc()
                        retry += 1
                    if retry == 10:
                        print("from normal request")
                        brand_response = requests.get(b_url + '?page={}'.format(page), verify=False, allow_redirects=False)

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

print("Completed")

