from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import configparser
import csv
import re

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

def get_home(path,codes):
    count = 1
    obj = start_chrome(path)
    url_list = []
    for code in codes:
        url = "http://quote.cfi.cn/quote_{}.html".format(code)
        url_list.append(url)
    for url in url_list:
        print(count)
        # if count < 3042:       
        #     count +=1
        #     continue
        obj.get(url)
        get_suffix(obj,path)
        count += 1
    obj.close()


def get_suffix(obj,path):
    for link in obj.find_elements_by_xpath('//*[@id="nodea1"]/nobr/a'):
        url_suffix = link.get_attribute('href').replace("https://quote.cfi.cn/cwfxzb/","")
    f = open(path + "suffix.txt","a")
    f.write(url_suffix + '\n')
    f.close()

if __name__ == '__main__':
    path = get_path()
    with open(path + 'data.csv') as csvfile:
        reader = csv.reader(csvfile)
        codes = [row[0].replace('\t','') for row in reader]
    codes = codes[1:]
    get_home(path,codes)
