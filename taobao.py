from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo


class Taobao(object):
    """docstring for Taobao"""

    def __init__(self):
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()
        # options.add_experimental_option("prefs",
        # {"profile.managed_default_content_settings.images": 2})  不加载图片,加快访问速度
        options.add_experimental_option(
            'excludeSwitches', ['enable-automation'])  # 设置为开发者模式

        self.browser = webdriver.Chrome(executable_path=chromedriver_path,
                                        options=options)

        self.wait = WebDriverWait(self.browser, 10)

    def login(self):

        self.browser.get(self.url)

        weibo_login = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_login.click()

        weibo_user = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.inp.username>.W_input')))

        weibo_pwd = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.inp.password>.W_input')))

        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_tip>a>span')))

        weibo_user.send_keys(weibo_username)
        weibo_pwd.send_keys(weibo_password)
        submit.click()

        taobao_name = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.user-info.oversea-head > .user-nick')))

        print('login successfully')
        print('User Name: ', taobao_name.text)

    def index_page(self, page):
        try:
            url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
            print('search :', KEYWORD)
            print('getting', page, 'page')
            self.browser.get(url)

            if page > 1:
                input = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
                submit = self.wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
                input.clear()
                input.send_keys(page)
                submit.click()
                self.wait.until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                '#mainsrp-itemlist div.m-itemlist div.items>.item')))
                print('jump to ', page, ' page')
                # get_products()
            print('got items successfully')
        except TimeoutException:
            print('Now at ', page, ' page')

    def get_products(self):
        html = self.browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist div.m-itemlist div.items>.item').items()
        for item in items:
            product = {
                'image': item.find('.pic .J_ItemPic.img').attr('data-src'),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text(),
                'title': item.find('.title').text(),
                'shop': item.find('.shop').text(),
                'location': item.find('.location').text(),
            }
            print(product)
            yield product


class MyMongoDB(object):

    def __init__(self):
        try:
            self.conn = pymongo.MongoClient(settings['ip'], settings['port'])
        except Exception as e:
            print(e)
        self.db = self.conn[settings['db_name']]
        self.collection = self.db[settings['collection_name']]

    def insert(self, dic):
        self.collection.insert_one(dic)
        print('insert successfully')
        # print('插入成功')

    def update(self, dic, newdic):
        self.collection.update_one(dic, newdic)
        # print('更新成功')
        print('update successfully')

    def delete(self, dic):
        self.collection.delete_one(dic)
        # print('删除成功')
        print('delete successfully')

    def dbFind(self, dic):
        data = self.collection.find(dic)
        for result in data:
            print(result)
        # print('查找成功')
        print('find successfully')

    def findAll(self):
        for i in self.collection.find():
            print(i)
        print('findAll successfully')

if __name__ == '__main__':
    settings = {
        'ip': '127.0.0.1',
        'port': 27017,
        'db_name': 'taobao',
        'collection_name': 'huawei phone'
    }
    mongo = MyMongoDB()
    KEYWORD = 'huawei'
    chromedriver_path = 'write your  absolute path of chromedriver'
    weibo_username = 'Write your weibo ID'
    weibo_password = 'Write your password'
    taobao = Taobao()
    taobao.login()
    for i in range(1, 11):
        taobao.index_page(i)
        items = taobao.get_products()
        for item in items:
            mongo.insert(item)
    print('Done!')
