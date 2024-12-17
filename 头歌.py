import requests
from lxml import etree
import re

head={
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130",
    'cookie':'bid=_FTB1MUwrLs; ap_v=0,6.0; _pk_id.100001.3ac3=3437e69ee8e49dee.1733963817.; __utmc=30149280; __utma=81379588.76944857.1733963817.1733963817.1733963817.1; __utmc=81379588; __utmz=81379588.1733963817.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); dbcl2="285330498:3DEYC3dw9vg"; ck=O2Et; ll="118281"; __utma=30149280.1452847422.1733963817.1733963817.1733966543.2; __utmz=30149280.1733966543.2.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; _vwo_uuid_v2=D51F0189816DC873061620A972A92DB6C|d475ed1029fe378bf5f3837847013cb4; frodotk_db="89bb4440d44aba3f9d31ccc27ce02ebd"'
}
x=[]
xx=[]
xxx=[]
for i in range(10):
    html=requests.get(url='https://book.douban.com/top250?start='+str(i*25),headers=head).text
    x.append(re.findall('''; title="(.*?)"''',html))
    xx.append(re.findall('href="(.*?)" onclick',html)[1::])
    xxx.append(re.findall(r'''\<p class\=\"pl\"\>(.*?)<\/p\>''', html))
with open('xxx.txt', 'w', encoding='utf-8') as f:
    for ii in range(len(x)):
        for i in range(len(x[ii])):
            print(str({x[ii][i]:xx[ii][i]+xxx[ii][i]}))
            f.write(str({x[ii][i]:xx[ii][i]+xxx[ii][i]}))

