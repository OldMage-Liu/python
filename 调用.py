import requests
from lxml import etree
import time
import re
for i in range(10):
    url = 'http://www.2t58.com/list/cztop/'+str(i)+'.html'
    head = {
        'Cookie': 'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f=1718027661,1718028410; Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f=' + str(int(time.time())),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
    }
    resp = requests.get(url, headers=head).text
    html = etree.HTML(resp)
    name=html.xpath('/html/body/div[1]/div/div[2]/ul/li/div[1]/a/text()')
    hrefs = html.xpath('/html/body/div[1]/div/div[2]/ul/li/div[1]/a/@href')
    for i in range(len(hrefs)):
        if '/video' in hrefs[i]:
            pass
        else:
            pattern = r'g/(.*?).html'
            x = re.findall(pattern, hrefs[i])
            params = {
                'id': x[0],
                'type': 'music'
            }
            heads = {
                'Cookie': 'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f=1718027661,1718028410; Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f=' + str(
                    int(time.time())),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'Host': 'www.2t58.com',
                'X-Requested-With':'XMLHttpRequest',
                'Referer':'http://www.2t58.com/song/ZG54dmhkZG5o.html',
                'Origin':'http://www.2t58.com'
            }
            song_response = requests.post('http://www.2t58.com/js/play.php', data=params, headers=heads).text
            href=re.findall('"url":"(.*?)"}',song_response)
            try:
                resp=requests.get(url='http://www.2t58.com'+hrefs[i],headers=head).text
                html=etree.HTML(resp)
                name=html.xpath('/html/body/div[1]/div/div[1]/div[2]/div[2]/div[1]/h1[1]/text()')
                print(name[0])
                with open( r'C:\Users\ASUS\PycharmProjects\pythonProject\车载音乐\\'+name[0]+ '.mp3', 'ab') as f:
                    url=href[0].replace('\\','')
                    xxx=requests.get(url=url)
                    f.write(xxx.content)
            except:
                pass
