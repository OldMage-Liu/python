with open('F:/小说网.txt','r') as f:
    href=f.read()
    href_list=href.split()
import requests
import re
import time
head={
    'referer':'https://www.3bqg.cc/top/',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'cookie':'Hm_lvt_985c57aa6304c183e46daae6878b243b=1724569950; HMACCOUNT=027A2AA250323DBD; Hm_lpvt_985c57aa6304c183e46daae6878b243b=1724571691'
}

for i in href_list:
    time.sleep(60)
    url = 'https://www.3bqg.cc' + i
    print(url)
    小说=requests.get(url=url,headers=head).text
    xxx='<span class="title">(.*?)</span>'
    小说名=re.findall(xxx,小说)
    xx='<a href ="(.*?)">(.*?)<'
    小说章节_网址=re.findall(xx,小说)
    with open('f:/小说章节/' + 小说名[0] + '.txt', 'w') as f:
        print(小说名)
        for i in 小说章节_网址:
            f.write(str(小说章节_网址))





















#
#
# import requests
# import re
# import os
#
# # Make sure the directory exists
# if not os.path.exists('f:/小说章节/'):
#     os.makedirs('f:/小说章节/')
#
# head = {
#     'referer': 'https://www.3bqg.cc/top/',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
#     'cookie': 'Hm_lvt_985c57aa6304c183e46daae6878b243b=1724569950; HMACCOUNT=027A2AA250323DBD; Hm_lpvt_985c57aa6304c183e46daae6878b243b=1724571691'
# }
#
# with open('F:/小说网.txt', 'r') as f:
#     href = f.read()
#     href_list = href.split()
#
# for i in href_list:
#     url = 'https://www.3bqg.cc' + i
#     response = requests.get(url=url, headers=head)
#     小说 = response.text
#     小说名 = re.findall(r'<span class="title">(.*?)</span>', 小说)
#     小说章节_网址 = re.findall(r'<a href ="(.*?)">(.*?)</a>', 小说)
#
#     if 小说名:
#         with open(f'f:/小说章节/{小说名[0]}.txt', 'w', encoding='utf-8') as f:
#             for chapter in 小说章节_网址:
#                 f.write(f'{chapter[1]}\n{chapter[0]}\n\n')
