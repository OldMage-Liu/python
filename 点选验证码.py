import requests
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from hashlib import md5
from selenium.webdriver.common.action_chains import ActionChains #动作链
import json
#1.打开浏览器

driver=webdriver.Edge()
print(driver.get_window_size())
# 2.访问网站
driver.get('https://www.bilibili.com/')
driver.maximize_window()
# 3.点击登录按钮
# """如何才能让程序知道登录按钮在什么地方呢？
# 通过元素定位，登录按钮标签位置，进行点击操作"""
# 通过CSS选择器查找元素

# driver.find_element_by_css_selector('.bili-header .header-login-entry')
# driver.find_element(by=cssselect,'.bili-header .header-login-entry')
time.sleep(3)
# 使用CSS选择器来定位“登录”按钮元素，模拟人点击该“登录”按钮后，弹出账号和密码的输入框
elment=driver.find_element(by=By.CSS_SELECTOR,value='.bili-header .header-login-entry')

# 现在你可以对element进行操作了，比如点击它
elment.click()

# 延时
time.sleep(4)

# 4.输入账号密码，点击登录
# 定位账号输入框以及密码输入框/登录按钮位置
# 账号
driver.find_element(by=By.CSS_SELECTOR,value='div.login-pwd-wp>form>div:nth-child(1)>input').send_keys('13710685314')
# 密码
driver.find_element(by=By.CSS_SELECTOR,value='div.login-pwd-wp>form>div:nth-child(3)>input').send_keys('0si2wei5fu')
# 点击登录
driver.find_element(by=By.CSS_SELECTOR,value='div.btn_primary').click()
time.sleep(5000)

# """验证码识别
# 1.获取验证码图片
# 2."""

# 获取验证码图片标签
imglabel=driver.find_element(By.CSS_SELECTOR,'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_table_box > div.geetest_window > div > div.geetest_item_wrap')
imglabel1=driver.find_element(By.CSS_SELECTOR,'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_head > div.geetest_tips > div.geetest_tip_img')

# selenium截图保存图片
imglabel.screenshot('yzm.png')
imglabel1.screenshot('yangban.png')
requests.get(url='https://upload.chaojiying.net/Upload/Processing.php')

time.sleep(10000)


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def PostPic_base64(self, base64_str, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
            'file_base64': base64_str
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    chaojiying = Chaojiying_Client('fwsdglg', 'fwsdglg2024', '962435')
    im = open('yzm.png', 'rb').read()
    im1 = open('yangban.png', 'rb').read()

    验证坐标 = chaojiying.PostPic(im, 9501)
    需要验证的文字 = chaojiying.PostPic(im1, 2005)
    文字坐标 = 验证坐标['pic_str']
    文字坐标=文字坐标.split('|')
    文字 = list(需要验证的文字['pic_str'])
    print(文字坐标,文字)
    x={}
    for i in 文字坐标:
        x.update({i[0]:i[2::]})
    for i in range(len(文字)):
        zuobia=x[文字[i]]
        print(zuobia)






