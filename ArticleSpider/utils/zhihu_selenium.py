# _*_ encoding:utf-8 _*_
# python selenium模块使用出错解决，Message: 'geckodriver' executable needs to be in PATH
# https://blog.csdn.net/liu5257/article/details/53437878
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time

while True:
    #option = webdriver.ChromeOptions()
    #option.set_headless()
    #因为要手动输入验证码，所以无头模式注释掉
    # driver = webdriver.Chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    driver = webdriver.Firefox()
    driver.get('http://www.zhihu.com')
    driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()
    driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('17631094456')
    driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('199641yueqi')
    input('请查看网页是否要输入验证码，如果有请手动输入,输入完请回车确认，没有直接回车!')
    driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').click()
    time.sleep(5)#等待提交后界面加载
    #因为有两种验证码，故输入提交后，对输入后的两种可能结果进行检查，如果输入验证码错误，程序继续运行，提示重新登陆
    try:
        foo = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[2]')
        if foo.text == '请提交正确的验证码 :(':
            print('您输入的验证码错误，稍等后出现新的登陆，再确认！')
            driver.quit()
            continue
    except:
        pass
    try:
        foo = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div[1]/span')
        if foo.text == '请提交正确的验证码 :(':
            print('您输入的验证码错误，稍等后出现新的登陆，再确认！')
            driver.quit()
            continue
    except:
        pass
    print('验证码输入正确，已经成功登陆！')
    cookies = driver.get_cookies()#保存好登陆COOKIE后续网络爬虫要用到
    break
    driver.quit()
