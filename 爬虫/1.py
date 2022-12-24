from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import configparser
import csv

url = 'https://data.cfi.cn/data_ndkA0A1934A1939A1940A5526.html' #爬取网址         

def get_path():
    filename_project = os.getcwd()+'/project.ini'
    inifile_project = configparser.ConfigParser()
    inifile_project.read(filename_project,encoding = 'utf-8') 
    path = inifile_project.get("Section", "path") # 获取当前程序路径
    return path

def start_chrome(path):
    driver_path = path + 'chromedriver.exe'  # 获取浏览器的地址
    opt = webdriver.ChromeOptions() 
    opt.add_argument('headless')              #设置无界面    
    obj = webdriver.Chrome(executable_path=driver_path,options=opt)
    return obj

def get_data(path):
    obj = start_chrome(path)
    obj.get(url)
    obj.switch_to.frame("content")
    num = 96
    for i in range(1,num+1):
        save_data(obj, path)
        print('第%d页已保存' % i)
        next_bottom = obj.find_element_by_xpath('//*[@id="content"]/div[2]/a[96]')
        obj.execute_script("arguments[0].click();", next_bottom)    #点击下一页
    obj.close()


def save_data(obj,path):
    codes = []
    names = []
    markets = []
    header = ['code','name','market']
    table = obj.find_element_by_xpath('/html/body/div[2]/table[2]')
    td_content = table.find_elements_by_tag_name("td")
    count = 0
    for td in td_content:
        if count % 16 == 0 and count != 0:
            code = td.text
            codes.append('\t'+code.zfill(6))
        if count % 16 == 1 and count != 1:
            names.append(td.text.replace('*',''))
        if count % 16 == 2 and count != 2:
            markets.append(td.text)
        count += 1

    if not os.path.exists(path + "data.csv"):
        with open(path + "data.csv","w",newline="") as csvfile: 
            writer = csv.writer(csvfile)
            writer.writerow(header)
        csvfile.close()
    else:
        with open(path + "data.csv","a",newline="") as csvfile: 
            writer = csv.writer(csvfile)
            writer.writerows(zip(codes,names,markets))
        csvfile.close()

if __name__ == '__main__':
    path = get_path()
    get_data(path)





