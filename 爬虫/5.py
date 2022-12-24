from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import configparser
import csv
import re
import json

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

def get_gdtj(path,suffixs):
    count = 1
    obj = start_chrome(path)
    url_list = []
    for suffix in suffixs:
        url = "https://quote.cfi.cn/gsda/{}".format(suffix)
        url_list.append(url)
    for url in url_list:
        # print(url)
        print(count)
        # if count < 1812:       
            # count +=1
            # continue
        obj.get(url)
        get_gsda_data(obj,path,url[-11:-5])
        count += 1
    obj.close()


def get_gsda_data(obj,path,code):
    table = obj.find_elements_by_xpath('//*[@id="content"]/div[2]/table')
    td_content = table[0].find_elements_by_tag_name("td")
    
    company_dict = {}
    company_dict['code'] = code
    company_dict['fullname'] = td_content[4].text
    # print(company_dict)

    if not os.path.exists(path + "company.json"):
        with open(path + "company.json","w") as f: 
            str_ = json.dumps(company_dict, ensure_ascii=False)
            f.write(str_)
            f.write('\n')
        f.close()

    else:
        with open(path + "company.json","a") as f: 
            str_ = json.dumps(company_dict, ensure_ascii=False)
            f.write(str_)
            f.write('\n')
        f.close()


if __name__ == '__main__':
    path = get_path()
    suffixs = []
    with open(path + 'suffix.txt') as f:
        for line in f:
            suffixs.append(line.strip('\n'))
    # print(suffixs)
    get_gdtj(path,suffixs)
