import os
path='E:/52bqg小说/终极斗罗'
files=os.listdir(path)
for i in files:
    old_name=i
    i=i.split(' ')
    new_name=i[0]+'.txt'
    print(new_name)
    os.rename(path+'/'+old_name,path+'/'+new_name)





