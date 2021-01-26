import pandas as pd
import numpy as np
from selenium import webdriver
import time

class LOGIN:
    def __init__(self, make_user):
        self.make_user = make_user #自動的に作成するかどうか．
        self.USER = "admin"
        self.driver = ""
        self.username_list = []
        self.last_name_list = []
        self.first_name_list = []
        self.email_list = []
    
    def setup(self):
        self.driver = webdriver.Chrome(executable_path = '.\\chromedriver_win32\\chromedriver.exe')
        self.driver.implicitly_wait(3)
        url_login = "http://jay-yoga.club/login/"
        self.driver.get(url_login)
        time.sleep(1)
        print("ログインページにアクセスしました")

    def input(self):
        USER = self.USER
        print(USER)
        element = self.driver.find_element_by_name('username')
        element.clear()
        element.send_keys(USER)
        print("フォームを送信")

    def click(self, x_path):
        lg_box = self.driver.find_element_by_xpath(x_path)
        time.sleep(1)
        lg_box.click()
        # print("クリック完了．")

    def input_signup(self, username, last_name, first_name, email="#"):
        element = self.driver.find_element_by_name('username')
        element.clear()
        element.send_keys(username)
        element = self.driver.find_element_by_name('lastname')
        element.clear()
        element.send_keys(last_name)
        element = self.driver.find_element_by_name('firstname')
        element.clear()
        element.send_keys(first_name)
        element = self.driver.find_element_by_name('email')
        element.clear()
        element.send_keys(email)

    def add_zero(self, num):
        if num < 10:
            add_zero_num = "0" + str(num)
        else:
            add_zero_num = str(num)
        return add_zero_num

    def get_list(self):
        NUM = 50
        self.username_list = ['guest' + self.add_zero(i+1) for i in range(NUM)]
        self.last_name_list = ['ゲスト' + self.add_zero(i+1) for i in range(NUM)]
        self.first_name_list = ['太郎'] * NUM
        self.email_list = ['###'] * NUM

    def main(self):
        self.setup()
        self.input()
        self.click('/html/body/form/div[3]/button[2]')
        self.click('/html/body/nav/div/ul/li[4]/a')

        if self.make_user == True: #自動的にユーザー名を作成する．
            self.get_list()

        if len(self.username_list) == len(self.first_name_list) and len(self.username_list) == len(self.last_name_list) and len(self.username_list) == len(self.email_list):
            for username, last_name, first_name, email in zip(self.username_list, self.last_name_list, self.first_name_list, self.email_list):
                self.input_signup(username, last_name, first_name, email)
                self.click('/html/body/div/form/div/button[2]')
        else:
            print("ユーザーネームとファーストネーム，ラストネームの長さが異なっています．")