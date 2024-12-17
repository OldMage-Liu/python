import requests
from lxml import etree
import re
import os
url='https://www.3bqg.cc/top/'
head={
    'cookie':'Hm_lvt_985c57aa6304c183e46daae6878b243b=1729259164,1730891627; Hm_lpvt_985c57aa6304c183e46daae6878b243b=1730891627; HMACCOUNT=204D95E8B58CEC79',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
}
html_text=requests.get(url=url,headers=head).text
href_list=re.findall('<a href="(.*?)">',html_text)
text_name_list=re.findall('<a href="(.*?)">(.*?)</a>',html_text)
for i in range(len(href_list[12:-5])):
    name=text_name_list[12:-5][i]
    url='https://www.3bqg.cc'+href_list[12:-5][i]
    Chapter=requests.get(url=url,headers=head).text
    Chapter_text_href_list=re.findall('<dd><a href ="(.*?)">',Chapter)
    Chapter_name=re.findall('<a href ="(.*?)">(.*?)</a></dd>',Chapter)
    for i in range(len(Chapter_text_href_list)):

        url = 'https://www.3bqg.cc' + Chapter_text_href_list[i]
        text = requests.get(url=url, headers=head).text
        txt = re.findall(
            '<div id="chaptercontent" class="Readarea ReadAjax_content">(.*?)请收藏本站：https://www.3bqg.cc。笔趣阁手机版：ht',
            text)
        txt=txt[0].replace('　　aplt♂<br /><br />　　','')
        txt=txt.replace('<br /><br />　　','')
        print(Chapter_name[i][1])
        try:
            os.mkdir('D:\笔趣阁' +'\\'+ name[1])
            with open('D:\笔趣阁' +'\\'+ name[1] +'\\'+Chapter_name[i][1]+ '.txt', 'w',encoding='utf-8') as f:
                f.write(txt)
        except:
            with open('D:\笔趣阁' + '\\' + name[1] + '\\' + Chapter_name[i][1] + '.txt', 'w',encoding='utf-8') as f:

                f.write(txt)


