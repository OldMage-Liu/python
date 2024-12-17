#创建空列表储存多行输入信息
textList = []
#创建关键字变量
keywords = '__end__'
#打印文字信息
print('文字多行输入，输入“{0}”即可停止。\n请在下方输入内容。\n'.format(keywords))
#嵌套循环
while True:
	#声明变量来储存输入信息
	text = input()
	#判断输入信息是否为结束输入的关键字
	if text == keywords:
		#跳出循环
		break
	else: #如果不是就添加到列表
		textList.append(text)

#打印输入的内容
for i in textList:
	print(i)
