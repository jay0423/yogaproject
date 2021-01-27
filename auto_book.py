import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
import time
import random

class AutoBook:

    driver = webdriver.Chrome(executable_path = '.\\chromedriver_win32\\chromedriver.exe')
    max_plan_list = [2,2,4,3,4] #曜日ごとのプランの最大数
    max_tr = 5 #縦の最大長さ
    th = 1

    def __init__(self, make_user):
        self.make_user = make_user #自動的に作成するかどうか．
        self.month = 0
        self.username_list = []
        self.FROM_NUM = 32
        self.TO_NUM = 33
    
    def setup(self):
        self.driver.implicitly_wait(2)
        url_login = "https://jay-yoga.club/login/"
        self.driver.get(url_login)
        time.sleep(1)
        print("ログインページにアクセスしました")

    def click(self, x_path):
        click_box = self.driver.find_element_by_xpath(x_path)
        # time.sleep(1)
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
        time.sleep(1)

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
        self.username_list = ['guest' + self.add_zero(i+1) for i in range(self.FROM_NUM-1, self.TO_NUM)]


    def main(self):
        self.setup() #セットアップ

        if self.make_user == True: #自動的にユーザー名を作成する．
            self.get_list()
        
        if self.username_list == []:
            return
        else:
            month_list = [0, 100]
            max_tr_list = [5, 4]
            for username in self.username_list:
                self.login(username)
                for month, max_tr in zip(month_list, max_tr_list):
                    self.month = month
                    book_num = random.choice([1,2,3,4,5,6,7,8,9,10])
                    print(book_num)
                    for i in range(book_num):
                        self.access_calendar_month(self.month)
                        self.max_tr = max_tr
                        self.click_date()
                        self.click_book()
                    self.logout()

if __name__ == "__main__":
    a = auto_book.AutoBook(True)
    a.FROM_NUM = input("FROM_NUM")
    a.TO_NUM = input("TO_NUM")
    a.main()

# import auto_book
# import importlib
# importlib.reload(auto_book)
# a = auto_book.AutoBook(True)
# a.FROM_NUM = 34
# a.TO_NUM = 35
# a.main()