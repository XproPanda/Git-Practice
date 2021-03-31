#!/usr/bin/env python
# coding: utf-8

# In[8]:


import queue
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
import json
import os

'''for git use'''
class ListenData():
    def __init__(self):
        self.listJob=[]
        self.q = queue.Queue()
        executor = ThreadPoolExecutor(max_workers=3)
        executor.submit(self.saveJson)
    
    def listenData_process(self,n):
        if len(self.listJob[:n])>=n:
            self.q.put(self.listJob[:n])
            self.listJob = self.listJob[n:]
    
    def listenData_final(self):
        self.q.put(self.listJob)
        self.listJob=[]
    
    def saveJson(self):
        pass

class JobDownload(ListenData):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")        
    options.add_argument("--incognito")               
    options.add_argument("--disable-popup-blocking ")
    # 消除Chrome 目前受到自動測試軟體控制
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})
    driver = webdriver.Chrome(options = options)
    
    def __init__(self):
        super().__init__()
        self.index=0     #  跑到第幾個
        self.fileNum=1   #  存檔號

    def visit(self):
        JobDownload.driver.get('https://www.104.com.tw/')

    def setCity_and_search(self):
        # 一定要sleep, 跑太快會死機 
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.CSS_SELECTOR, "span#icity"))).click()
        
    # country selector
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.CSS_SELECTOR, "div.category-picker__level-one li")))[0].click()

    # cities selector
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.XPATH, '//span[@class="children" and text()="台北市"]//preceding-sibling::span'))).click()
         
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.XPATH, '//span[@class="children" and text()="新北市"]//preceding-sibling::span'))).click()
    # sure-button
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.CSS_SELECTOR, "button.category-picker-btn-primary"))).click()

    # search
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.CSS_SELECTOR, '[class="btn btn-primary js-formCheck"]'))).click()

    def full_time(self):
        WebDriverWait(JobDownload.driver, 10).until(
                EC.presence_of_element_located( 
                    (By.XPATH, '//li[@data-value="1" and text()="全職"]'))).click()

    def scroll_parse_save(self):
        sleep(2)
    #     print(driver.page_source)
        while True:           
            render_page=JobDownload.driver.find_elements_by_xpath('//div[@id="js-job-content"]//div//button[@class="b-btn b-btn--link js-more-page"]')
            
            if len(render_page)==0:
                JobDownload.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                
            else:
                manual_page = render_page[-1]
                if manual_page.is_displayed():
                    manual_page.click()
                    self.parse()
                else:
                # move last-data to the queue
                    self.listenData_final()
                    break

    def parse(self):
        jobs=JobDownload.driver.find_elements_by_xpath('//*[@id="js-job-content"]//article')
        while self.index!=len(jobs):
    #   「職缺名稱」、「職缺連結」、「公司名稱」、「公司連結」、「地區
            job_name=jobs[self.index].get_attribute('data-job-name')
            job_url=JobDownload.driver.find_elements_by_xpath("//*[@id='js-job-content']//article//div//h2//a")[self.index].get_attribute('href')
            job_conpany=jobs[self.index].get_attribute('data-cust-name')
            job_company_url=JobDownload.driver.find_elements_by_xpath("//*[@id='js-job-content']//article//div//ul//li//a")[self.index].get_attribute('href')
            job_location=jobs[self.index].find_element(By.CSS_SELECTOR, "ul.b-list-inline.b-clearfix.job-list-intro.b-content>li").text
            self.listJob.append({
                "job_name": job_name,
                "job_url": job_url,
                "job_conpany": job_conpany,
                "job_company_url":job_company_url,
                "job_location":job_location
            })
            self.index+=1
            
        # move 500筆 data to the queue
        self.listenData_process(500)
        

    def saveJson(self):
        while True:
            data = self.q.get()
            if not os.path.exists(r'./104job'):
                    os.makedirs("./104job")

            with open(r"./104job/工作清單{}.json".format(self.fileNum), "w+", encoding='utf-8', newline='') as outfile:
                outfile.write(json.dumps(data, ensure_ascii=False))
            self.fileNum+=1
            self.q.task_done()            

    def close(self):
        JobDownload.driver.quit() 


# In[14]:


if __name__ == '__main__':
    jd=JobDownload()
    jd.visit()
    jd.setCity_and_search()
    jd.full_time()
    jd.scroll_parse_save()
    jd.close()


# In[ ]:





# In[ ]:





# In[ ]:





# In[242]:





# In[ ]:




