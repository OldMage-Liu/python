import os
import 转化
def 文件批量操作(path):
    files=os.listdir(path)
    for i in files:
        old_name=i
        i=str(i).replace('.txt','').replace('第','').replace('章','')
        print(i)
        # print(old_name)
        # new_name=转化.backward_cn2an_one(i)
        # print(new_name)
        # os.rename(path+'/'+old_name,path+'/'+str(new_name)+'.txt')
文件批量操作('E:/52bqg小说/终极斗罗')