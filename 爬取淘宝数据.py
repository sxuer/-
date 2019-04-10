from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random,os
import requests
from PIL import Image
from bs4 import BeautifulSoup

class TaoBao:

    def __init__(self,name,psw,shop_name):
        self.url='https://login.taobao.com/member/login.jhtml'
        self.name=name
        self.psw=psw
        self.shop_name=shop_name

        option=webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])  #开发者模式
        option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        self.browser=webdriver.Chrome(options=option)

        self.wait = WebDriverWait(self.browser, 10)  # 加载标签的时候可能需要等待，设置超时时长为10s
        print('请等待弹出验证码的图片，然后在此手动输入，回车确定')

    def get_captcha(self,src):
        try:
            r = requests.get(src)
        except:
            print('等待验证码时间过短，请重新运行，或者加长等待时间（默认15秒）（频繁登陆会加长验证码加载时间）')
            exit()
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jap'))
        captcha = input('请输入验证码\n')
        return captcha

    def login(self):
        # 1.打开页面
        self.browser.get(self.url)

        #2.等待对应标签的出现
            # 备注：
                # 1.标签=self.wait(浏览器实例，超时时间).until(方法)，其中，每隔一段时间调用一次方法直到该方法返回True
                # 2.EC.presence_of_element_located(args),args必须是元组,且一次只能判断一个

        #2.1直接等待“忘记密码”可以跳过扫码登陆
        password_login=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
        password_login.click()

        # 2.2等待微博登陆按钮并进入
        weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_login.click()

        #2.3等待微博用户名输入框
        weibo_name=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_login_logged > div > div:nth-child(2) > div > input')))

        #2.4等待微博密码输入框
        weibo_psw = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.password > input:nth-child(1)')))

        #2.5等待登陆按钮
        login_bt = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a')))

        #3 输入然后点击登陆
        weibo_name.send_keys(self.name)
        weibo_psw.send_keys(self.psw)
        sleep(0.2)
        login_bt.click()

        #如果有验证码，则需要下面的验证码验证，没有则注释
        #等待验证码
        sleep(15)
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.code > img')))
        src=img.get_attribute("src")

        #输入验证码
        captcha=self.get_captcha(src)
        captcha_bt = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.verify > input:nth-child(1)')))
        captcha_bt.send_keys(captcha)
        login_bt.click()

        #4 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name=self.wait.until((EC.presence_of_element_located((By.CSS_SELECTOR,'#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a'))))
        print(taobao_name.text,'登陆成功')

    #模拟人类滑动窗口
    def swipe_down(self,second):
        for i in range(int(second/0.1)):
            js = "var q=document.documentElement.scrollTop=" + str(300+200*i)
            self.browser.execute_script(js)
            sleep(0.2)
        #循环结束后，滑倒最底部
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)
        sleep(0.3)

    #实现翻页
    def next_page(self,page):
        #等待页码输入框加载完毕
        next_number=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > .m-page > .wraper > .inner > .form > .input')))
        #等待确认按钮加载完毕
        confirm_bt=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > .m-page > .wraper > .inner > .form > .btn')))
        #清除里面的数字
        next_number.clear()
        #输入页码
        next_number.send_keys(page)
        sleep(random.randint(1,2))
        #确认翻页
        confirm_bt.click()

    def crawl_data(self):
        self.browser.get("https://s.taobao.com/search?q="+self.shop_name)

        #1.获取总页数
        #等待页数标签出现
        page_num=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.total')))
        page_num=page_num.text.replace('共 ','').replace(' 页，','')
        print('总共%s页'%page_num)

        #遍历所有页,由于是通过输入页码进行翻页的，所以从2开始
        for page in range(2,int(page_num)):
            #2.等待商品全部加载完毕,.pic是商品div
            pic=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.pic')))
            #3.等待页码输入框，并获得当前页码
            present=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.form > input.input')))
            present_page=present.get_attribute('value')
            print('当前为第%s页'%present_page)

            #4.获取当前页面源码
            html = self.browser.page_source
            #解析
            soup=BeautifulSoup(html,'lxml')
            #获得数据标签
            raw_data=soup.select('.item.J_MouserOnverReq')
            for item in raw_data:
                price=item.select('.row.row-1.g-clearfix > .price')[0].get_text().strip()
                paied_num=item.select('.row.row-1.g-clearfix > .deal-cnt')[0].get_text().strip()
                name=item.select('.row.row-2.title')[0].get_text().strip()
                detail_url=item.select('.row.row-2.title > a')[0]['href']
                print(price+'\t'+paied_num+'\t'+name+'\t'+detail_url)

            #爬取一页之后，模拟人类滑动窗口
            self.swipe_down(random.randint(1,2))
            #然后翻页
            self.next_page(page)

if __name__ == '__main__':
    shop_name=input('输入需要爬取的数据商品名')
    weibo_name=input('请输入你的微博账号，确保微博已绑定淘宝')
    weibo_psw=input('请输入你的微博密码')
    taobaologin=TaoBao(weibo_name,weibo_psw,shop_name)
    taobaologin.login()
    taobaologin.crawl_data()
