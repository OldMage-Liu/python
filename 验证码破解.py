import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from PIL import Image
from selenium.webdriver import ActionChains
import random
import requests
from hashlib import md5
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
# 日志输出配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# 初始化一个webdriver.Chrome()对象
browser=webdriver.Edge()
# print(driver.get_window_size())
# 2.访问网站
browser.get('https://www.bilibili.com/')
browser.maximize_window()
# 登录函数   访问页面->输出账号、密码->点击登录
def login():
    elment = browser.find_element(by=By.CSS_SELECTOR, value='.bili-header .header-login-entry')
    # 现在你可以对element进行操作了，比如点击它
    elment.click()
    # 延时
    time.sleep(4)
    # 4.输入账号密码，点击登录
    # 定位账号输入框以及密码输入框/登录按钮位置
    # 账号
    browser.find_element(by=By.CSS_SELECTOR, value='div.login-pwd-wp>form>div:nth-child(1)>input').send_keys(
        '13710685314')
    # 密码
    browser.find_element(by=By.CSS_SELECTOR, value='div.login-pwd-wp>form>div:nth-child(3)>input').send_keys(
        '0si2wei5fu')
    # 点击登录
    browser.find_element(by=By.CSS_SELECTOR, value='div.btn_primary').click()
def save_img():
    # save_screenshot：将当前页面进行截图并保存下来
    time.sleep(3)
    code_img_ele = browser.find_element(by=By.CSS_SELECTOR,value='div.geetest_panel_next > div')
    code_img_ele.screenshot('page.png')
    return code_img_ele
def narrow_img():
    # 缩小图片
    code = Image.open('page.png')
    small_img = code.resize((169, 216))
    small_img.save('./small_img.png')
    print(code.size, small_img.size)
def submit_img():
    # 将验证码提交给超级鹰进行识别
    # 用户中心->软件ID 生成你的软件ID->替换掉96001  绑定微信可以得到1000积分 免费使用
    chaojiying = Chaojiying_Client('fwsdglg', 'fwsdglg2024', '962435')
    with open('./small_img.png', 'rb') as f:
        im = f.read()
    # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    result = chaojiying.PostPic(im, 9004)['pic_str']
    logging.info(result)
    return result
def parse_data(result):
    node_list = []  # 存储即将被点击的点的坐标  [[x1,y1],[x2,y2]]
    print(result)
    if '|' in result:
        nums = result.split('|')
        for i in range(len(nums)):
            x = int(nums[i].split(',')[0])
            y = int(nums[i].split(',')[1])
            xy_list = [x, y]
            node_list.append(xy_list)
    else:
        print(result.split(',')[0])
        print(result.split(',')[1])
        x = int(result.split(',')[0])
        y = int(result.split(',')[1])
        xy_list = [x, y]
        node_list.append(xy_list)
    return node_list
def scroll_into_view(element):
    browser.execute_script("arguments[0].scrollIntoView(true);", element)
def click_codeImg(all_list, code_img_ele):
    # 确保元素可见
    scroll_into_view(code_img_ele)
    for item in all_list:
        x = item[0] * 1.6
        y = item[1] * 1.6
        sleep(random.random() * 2)
        # 使用绝对坐标点击
        browser.execute_script("window.scrollTo(arguments[0], arguments[1]);", x, y)
        browser.execute_script("document.elementFromPoint(arguments[0], arguments[1]).click();", x, y)
        sleep(random.random())
        logging.info('点击成功！')
    sleep(random.random() * 2)
    # 定位确认按钮并点击
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.login-pwd-wp > div.btn_wp > div.btn_primary'))
    ).click()
# -*- coding: UTF-8 -*-
"""
@File    ：demo.py
@Author  ：叶庭云
@CSDN    ：https://yetingyun.blog.csdn.net/
"""
def main():
    # 进入登录界面，输入账号密码
    login()
    # 保存页面截图，并根据坐标裁剪获取验证码图片
    code_img_ele = save_img()
    # 缩小图片
    narrow_img()
    # 将图片提交给超级鹰,获取返回的识别结果
    result = submit_img()
    # 解析返回结果,将数据格式化
    all_list = parse_data(result)
    # 在页面验证码上完成点击操作并登录
    click_codeImg(all_list, code_img_ele)
main()
