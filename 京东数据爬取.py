# Author:D.dw
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver import ActionChains   #执行动作链，多个动作放入一个队列顺序执行
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from random import randint

class JD:

    def __init__(self,jd_name,jd_psw,goods_name):
        self.jd_name=jd_name
        self.jd_psw=jd_psw
        self.goods_name=goods_name

        option=webdriver.ChromeOptions()
        #无头模式
        # option.add_argument('--headless')
        # option.add_argument('--disable-gpu')
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        self.browser=webdriver.Chrome(options=option)

        self.wait=WebDriverWait(self.browser,10)

        #商品总页数
        self.pages=0


    def login(self):
        pass


    #模拟滑动
    def swipe_down(self,second):
        for i in range(int(second/0.1)):  #注意强转，否则'float' object cannot be interpreted as an integer，float不允许迭代
            js = 'var q=document.documentElement.scrollTop='+str(300+200*i)
            self.browser.execute_script(js)
            sleep(0.2)
        #确保滑到底部
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)
        #下面的商品是动态加载的，等待一会，否则翻页会报错
        sleep(0.5)

    #实现翻页
    def next_page(self):
        # self.get_data()
        # print('第一页爬取成功！正在爬取下一页\n')
        for page in range(self.pages+1):

            #模拟滑动到最底部
            self.swipe_down(randint(1,2))

            #按键翻页失败
            # #使用→键翻页
            # action=ActionChains(self.browser)
            # #点击一次→键
            # action.key_down(Keys.RIGHT).key_up(Keys.RIGHT)

            #使用点击翻页
            #等待页码框
            page_div=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p-skip')))
            now_page=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p-skip > input')))

            now_page.clear()
            now_page.send_keys(page+1)

            submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p-skip > a')))
            sleep(1.1)
            submit.click()

            #翻页后获取数据
            self.get_data()
            print('第%d页爬取成功！正在爬取第%d页\n'%((page+1),(page+2)))

    def get_data(self):
        goods=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.gl-item')))
        #获取页面代码
        html=self.browser.page_source
        soup=BeautifulSoup(html,'lxml')
        raw_data=soup.select('li.gl-item')  #获取每个商品的外框div
        print('开始获取数据')
        for item in raw_data:
            price=item.select('.gl-i-wrap > .p-price')[0].get_text().strip()
            good_name=item.select('.gl-i-wrap > .p-name-type-2 > a')[0]['title'].strip()
            good_url=item.select('.gl-i-wrap > .p-name-type-2 > a')[0]['href'].strip()
            commit=item.select('.gl-i-wrap > .p-commit')[0].get_text().strip().replace('二手有售','')
            shop=item.select('.gl-i-wrap > .p-shop')[0].get_text().strip()
            print('商品：%s\n价格%s\n链接：%s\n评价总数：%s\n店家：%s\n\n'%(good_name,price,good_url,commit,shop))

    def main(self):
        url='https://www.jd.com/'
        #打开京东
        self.browser.get(url)
        print('已经进入京东页面，开始搜索')

        search=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.form > input')))
        search.send_keys(self.goods_name)
        search_btn=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.form > button')))
        sleep(1)
        search_btn.click()

        #确定页数
        page_nums=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p-skip')))
        page_nums=page_nums.text.replace('共','').replace('页  到第\n页\n确定','')
        self.pages=int(page_nums)
        print('搜索完毕，有关 %s 的商品总共%s页'%(self.goods_name,page_nums))

        self.next_page()


if __name__ == '__main__':
    goods_name=input('请输入搜索商品名称')
    #前两个参数是登陆账号和密码，但是爬取京东似乎用不着登陆
    jd=JD(None,None,goods_name)
    jd.main()
