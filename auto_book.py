import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
import time
import random

class AutoBook:

    th = 1

    def __init__(self, make_user):
        self.make_user = make_user #自動的に作成するかどうか．
        self.driver = ""
        self.month = 0
        self.max_plan_list = [2,2,4,3,4]
        self.max_tr = 5
        self.username_list = []
    
    def setup(self):
        self.driver = webdriver.Chrome(executable_path = '.\\chromedriver_win32\\chromedriver.exe')
        self.driver.implicitly_wait(2)
        url_login = "https://jay-yoga.club/login/"
        self.driver.get(url_login)
        time.sleep(1)
        print("ログインページにアクセスしました")

    def click(self, x_path):
        click_box = self.driver.find_element_by_xpath(x_path)
        time.sleep(1)
        click_box.click()
        time.sleep(1)

    def login(self, username):
        USER = username
        print(USER)
        element = self.driver.find_element_by_name('username')
        element.clear()
        element.send_keys(USER)
        self.click('/html/body/form/div[3]/button[2]')

    def access_calendar_month(self, month):
        url_login = "https://jay-yoga.club/book/{}".format(month)
        self.driver.get(url_login)
        time.sleep(2)

    def logout(self):
        self.access_calendar_month(self.month)
        self.click('/html/body/footer/div/a')

    def click_date(self):
        tr_num = random.choice([int(i+1) for i in range(self.max_tr)])
        th_num = random.choice([1, 2, 3, 4, 5]) #曜日
        self.th = th_num
        while True:
            try:
                self.click('/html/body/div/table/tbody/tr[{}]/th[{}]/a/div[1]/p'.format(tr_num, th_num))
                break
            except:
                self.access_calendar_month(self.month)
                break

    def click_book(self):
        a_list = [int(i+2) for i in range(self.max_plan_list[self.th - 1])]
        div_num = random.choice(a_list)
        while True:
            try:
                self.click('/html/body/div/div[{}]/div/div[2]/div/a'.format(div_num))
                Alert(self.driver).accept()
                time.sleep(1)
                break
            except:
                self.access_calendar_month(self.month)
                return

    def add_zero(self, num):
        if num < 10:
            add_zero_num = "0" + str(num)
        else:
            add_zero_num = str(num)
        return add_zero_num

    def get_list(self):
        FROM_NUM = 32#31
        TO_NUM = 33#50
        self.username_list = ['guest' + self.add_zero(i+1) for i in range(FROM_NUM-1, TO_NUM)]


    def main(self):
        self.setup() #セットアップ

        if self.make_user == True: #自動的にユーザー名を作成する．
            self.get_list()
        
        if self.username_list == []:
            return
        else:
            for username in self.username_list:
                self.login(username)
                self.month = 100
                book_num = random.choice([1,2,3,4,5,6,7,8,9,10])
                for i in range(book_num):
                    self.access_calendar_month(self.month)
                    self.max_tr = 4
                    self.click_date()
                    self.click_book()
                self.logout()

# import auto_book
# import importlib
# importlib.reload(auto_book)
# a = auto_book.AutoBook(False)
# a.main()