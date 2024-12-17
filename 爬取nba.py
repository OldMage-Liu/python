import requests
import time
import json
import pandas
url='https://api.nba.cn/sib/v2/team/standing/rank/list?app_key=tiKB2tNdncnZFPOi&app_version=1.1.0&channel=NBA&device_id=5f4591689f71924dbd1e95e47aec4ed7&install_id=3128231383&network=N%2FA&os_type=3&os_version=1.0.0&sign=sign_v2&sign2=A87B224A9EAF769E71EE935FE9CAC19AA9A840DD49AA901838C11F300DE6962C&t='+str(time.time())[:10]
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Referer':'https://china.nba.cn/'

}

resp=requests.get(url=url,headers=headers).text
print(resp)
js=json.loads(resp)
东部联盟=js['data'][0]['di']
西部联盟=js['data'][1]['di']
球队=[]
胜=[]
负=[]
胜率=[]
胜场差=[]
主场战绩=[]
客场战绩=[]
最近10场战绩=[]
连续成绩=[]
场均得分=[]
场均失分=[]
净胜分=[]
for i in 东部联盟:
    for i in i['t']:
        球队.append(i['tn'])
        胜.append(i['w'])
        负.append(i['l'])
        胜率.append(i['winPct'])
        胜场差.append(i['gb'])
        主场战绩.append(i['hr'])
        客场战绩.append(i['ar'])
        最近10场战绩.append(i['l10'])
        连续成绩.append(i['str'])
        场均得分.append(i['winpointspg'])
        场均失分.append(i['losspointspg'])
        净胜分.append(i['diffpointspg'])
东部联盟数据=pandas.DataFrame({
    '球队': 球队,
    '胜': 胜,
    '负': 负,
    '胜率': 胜率,
    '胜场差': 胜场差,
    '主场战绩': 主场战绩,
    '客场战绩': 客场战绩,
    '最近10场战绩': 最近10场战绩,
    '连续成绩': 连续成绩,
    '场均得分': 场均得分,
    '场均失分': 场均失分,
    '净胜分': 净胜分
})
球队=[]
胜=[]
负=[]
胜率=[]
胜场差=[]
主场战绩=[]
客场战绩=[]
最近10场战绩=[]
连续成绩=[]
场均得分=[]
场均失分=[]
净胜分=[]
for i in 西部联盟:
    for i in i['t']:
        球队.append(i['tn'])
        胜.append(i['w'])
        负.append(i['l'])
        胜率.append(i['winPct'])
        胜场差.append(i['gb'])
        主场战绩.append(i['hr'])
        客场战绩.append(i['ar'])
        最近10场战绩.append(i['l10'])
        连续成绩.append(i['str'])
        场均得分.append(i['winpointspg'])
        场均失分.append(i['losspointspg'])
        净胜分.append(i['diffpointspg'])
西部联盟数据=pandas.DataFrame({
    '球队': 球队,
    '胜': 胜,
    '负': 负,
    '胜率': 胜率,
    '胜场差': 胜场差,
    '主场战绩': 主场战绩,
    '客场战绩': 客场战绩,
    '最近10场战绩': 最近10场战绩,
    '连续成绩': 连续成绩,
    '场均得分': 场均得分,
    '场均失分': 场均失分,
    '净胜分': 净胜分
})
东部联盟数据.to_excel('东部联盟数据.xlsx',index=False,engine='openpyxl')
西部联盟数据.to_excel('西部联盟数据.xlsx',index=False,engine='openpyxl')

print(time.time())




