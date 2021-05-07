# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 05:33:47 2019

@author: sgupta9
"""
##########Importing necessary packages
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os, re
import sys
from scrapy import Selector
from datetime import datetime

try:
    date = sys.argv[6]
except:
    date = datetime.now().strftime("%Y-%m-%d")

##########Defining required variables for the code
retailer = 'Bershka'
path = sys.argv[1]+retailer+'/'
input_file = sys.argv[2]
outfilename = sys.argv[3]
chromepath = sys.argv[4]
common_output = sys.argv[5]

# path = 'R:/DataAnalytics/UK_Fashion/UK_Fashion/'
# # input_file = path+'Input/Category_file_2020-01-23.xlsx'
# input_file = path+'Input/Category_file_2019-05-09.xlsx'
# chromepath = path+'selenium/webdriver/chrome/chromedriver.exe'
# outfilename = 'Output_' + retailer + '_' + date + '.xlsx'
# final_outfile = 'Output_retailers_data_'+date+'.xlsx'
# sys.path.append(path)
# common_output = path+'Output/'+date+'/'

if os.path.exists(path+'Dumps/'):
    pass
else:
    os.mkdir(path+'Dumps/')

if os.path.exists(path+'Dumps/'+date+'/'):
    pass
else:
   os.mkdir(path+'Dumps/'+date+'/')

dpath = path+'Dumps/'+date+'/'

base_url = ""
##########Definign function to capture required data points from html
def get_products(html2,category):
    global results
    # sp = BeautifulSoup(html2,"lxml")
    sp = Selector(text=html2)
    try:
        products = sp.xpath('//li[@class="grid-item double"]')
        if len(products) <1:
            products = sp.xpath('//li[@class="grid-item normal"]')
    except:
        pass

    #     products = [product for product in products if 'ng-hide' not in product['class']]
    #     if len(products)==0:
    #         try:
    #             products = sp.find_all("search-item")
    #             products = [product for product in products if 'ng-hide' not in product['class']]
    #         except:
    #             products = sp.find_all("search-item",attrs={'class': None})
    # except:
    #     products = sp.find_all("grid-product",attrs={'class': None})

    brand = 'Bershka'
    style = ''
    for product in products:
        name = ''
        sku = sku2 = ''
        prod_link = (url + str(product.xpath('.//a/@href').extract_first()))
        # sku = product.find('div','image').find('a')['title'].split('/')
        # sku2 = str(''.join(sku[:-1]))
        # color_code = str(sku[-1].strip())
        # name = product.find('div','prodinfo').find('a').getText().strip()
        # prod_link = product.find('div','prodinfo').find('a')['href']
        color_code = prod_link.split('=')[-1]
        name = product.xpath('.//div[@class="product-text"]/p/text()').extract_first()


        # try:
        #     price = product.find('span','productPrice oldPrice').getText().strip().replace(",","").replace('£','')
        #     if '-' in price:
        #         price_list = list(map(float,price.split('-')))
        #         price = sum(price_list)/len(price_list)
        #     else:
        #         price = float(price)
        #     offer_price = float(product.find('span','productPrice newPrice').getText().strip().replace(",","").replace('£',''))
        # except:
        #     try:
        #         price = product.find('span','productPrice').getText().strip().replace(",","").replace('£','')
        #         if '-' in price:
        #             price_list = list(map(float,price.split('-')))
        #             price = sum(price_list)/len(price_list)
        #         else:
        #             price = float(price)
        #         offer_price = ''
        #     except:
        #         price = 0
        #         offer_price = ''

        price = float(product.xpath('.//div[@class="current-price-elem"]/text()').extract_first().strip().replace(",","").replace('£',''))
        try:

            offer = float(product.xpath('.//span[@class="old-price-elem"]/text()').extract_first().strip().replace(",","").replace('£',''))
            price,offer_price = offer,price
        except:
            offer_price = 'None'
        #     price = price_1
        # if price:
        #     offer_price = price
        #     price = price_1



        if price<10:
            tier = 0
        elif price<20:
            tier = 1
        elif price<30:
             tier = 2
        elif price<40:
            tier = 3
        elif price<50:
            tier = 4
        elif price<75:
            tier = 5
        elif price<100:
            tier = 6
        else:
            tier = 7
        try:
            colors = product.find('ul','color-swatches').find_all('li')
            color = colors[0].getText().strip()
            try:
                alt_colors = len(colors)-1
                if alt_colors==0:
                    alt_colors = ''
            except:
                alt_colors = ''
        except:
            color = ''
            alt_colors = ''
        if category=='Sale':
            if 'jacket' in name.lower() or 'coat' in name.lower():
                category = 'Coats and Jackets'
            elif 'jeans' in name.lower():
                category = 'Jeans'
            else:
                continue
        data_row = [date,retailer,category,sku2,prod_link,name,style,brand,price,offer_price,tier,color,alt_colors,color_code,'','']
        results = results.append(pd.DataFrame([data_row],columns = columns),sort=False)

##########Defining input output files and output schema
categories_df = pd.read_excel(input_file)
categories = list(set(list(categories_df[categories_df.Retailer==retailer].Category)))
outfile = path+'Output/'+outfilename

url = 'https://www.bershka.com'
columns = ["DateOfCollection","Retailer","Category","SKU","ProductLink","Name","Style","Brand","Price","OfferPrice","PriceTier","Colour","AlternateColours_Count","ColourCode","HistoricalPrice","Sizes"]
results = pd.DataFrame(columns = columns)

for category in categories:
    cat_urls = list(categories_df[(categories_df.Retailer==retailer) & (categories_df.Category==category)].Cat_Link)
    for ind,cat_url in enumerate(cat_urls,0):
        try:
            option = webdriver.ChromeOptions()
            prefs={"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096 }
            option.experimental_options["prefs"] = prefs
            capabilities = { 'chromeOptions':  { 'useAutomationExtension': True}}
            driver = webdriver.Chrome(chromepath,desired_capabilities = capabilities,options=option)
            driver.get(cat_url.strip())
            time.sleep(2)
            height = driver.execute_script('return document.documentElement.scrollHeight')
            for i in range(20):
                driver.execute_script('window.scrollTo('+str(int(height/10)*(i-1))+','+str(int(height/10)*i)+')')
                time.sleep(.15)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # try:
            #     ind = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//span[@class="grid-product-header-num-products"]')))
            # except:
            #     pass
            # html2 = driver.page_source
            try:
                driver.find_element_by_css_selector('#main-container > div:nth-child(4) > div.notification-container-foreground.is-offset > div > div.notifications.fixed-bottom.geo-blocking-notification.rounded.is-sticky-right.notification-info > div > div > div > div.select-country-container > button').click()
            except:
                pass
            # try:
            #     total = int(BeautifulSoup(html2,"lxml").find('span','grid-product-header-num-products').getText().replace('Items','').replace('Item','').strip())
            # except:
            #     try:
            #         total = int(re.sub('[^0-9]','',BeautifulSoup(html2,"lxml").find('span','grid-product-header-num-products').getText()).strip())
            #     except:
            #         total = int(re.sub('[^0-9]','',BeautifulSoup(html2,"lxml").find('span','facet-quantity hide-mobile').getText()).strip())
            # count = len(BeautifulSoup(html2,"lxml").find_all('span','product-price'))
            # counter=0
            # while count<total:
            #     height = driver.execute_script('return document.documentElement.scrollHeight')
            #     for i in range(10):
            #         driver.execute_script('window.scrollTo('+str(int(height/10)*(i-1))+','+str(int(height/10)*i)+')')
            #         time.sleep(0.15)
            html2 = driver.page_source
            # counter+=1
            # count = len(BeautifulSoup(html2,"lxml").find_all('span','product-price prices'))
                # if counter==20:
                #     break
            html2 = driver.page_source

            f = open(dpath+category+'_'+str(ind)+'.html','wb')
            f.write(html2.encode('utf-8'))
            f.close()

            driver.quit()
            get_products(html2,category)
            time.sleep(1.5)
        except:
            try:
                driver.quit()
            except:
                pass
            continue

##########Writing data captured to excel
results.insert(columns.index("AlternateColours_Count")+1,"TotalColours",1)
results.drop_duplicates(inplace=True)
results.to_excel(outfile,index=False)
results.to_excel(common_output+outfilename,index=False)
