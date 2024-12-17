import time
import requests
from lxml import etree
import json
import re

url='https://api.nba.cn/sib/v2/players/list?app_key=tiKB2tNdncnZFPOi&app_version=1.1.0&channel=NBA&device_id=c28c178f7fc01e92a5161b6c80153add&install_id=3550222763&network=N%2FA&os_type=3&os_version=1.0.0&page_no=1&page_size=50&retireStat=A&sign=sign_v2&sign2=FC1F225E2CB98BA0E05B5EC72DE0F6CBF07B7E527E715560958CBDE1260710CB&t='+str(time.time())[0:10]
header={
    'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Origin':'https://china.nba.cn',
    'Referer':'https://china.nba.cn/'
}
html=requests.get(url=url,headers=header).text
js=json.loads(html)
x=js['data']
中文姓=[]
中文名=[]
英文姓=[]
英文名=[]
所属球队=[]
球衣号码=[]
位置=[]
身高=[]
体重=[]
NBA经验=[]
国籍=[]
for i in x:
    中文姓.append(i['firstName'])
    中文名.append(i['lastName'])
    英文姓.append(i['firstNameEn'])
    英文名.append(i['lastNameEn'])
    所属球队.append(i['teamName'])
    球衣号码.append(i['jerseyNo'])
    位置.append(i['position'])
    身高.append(i['heightMetric'])
    体重.append(i['weightMetric'])
    NBA经验.append(i['experience'])
    国籍.append(i['country'])
concat_names_cn = lambda 中文姓, 中文名: ''.join([中文姓[i] + 中文名[i]+' ' for i in range(min(len(中文姓), len(中文名)))])
concat_names_en = lambda 英文姓, 英文名: ''.join([英文姓[i] + 英文名[i]+' ' for i in range(min(len(英文姓), len(英文名)))])
print(concat_names_en(英文姓,英文名))
print(concat_names_cn(中文姓,中文名))

