
number_map = {
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9
}
# 单位映射
unit_map = {
    "十": 10,
    "百": 100,
    "千": 1000,
    "万": 10000,
    "亿": 100000000
}

def backward_cn2an_one(inputs):
    
    output = 0
    unit = 3
    num = 0
    for index, cn_num in enumerate(reversed(inputs)):
        if cn_num in number_map:
            # 数字
            num = number_map[cn_num]
            # 累加
            output = output + num * unit
        elif cn_num in unit_map:
            # 单位
            unit = unit_map[cn_num]
        else:
            raise ValueError(f"{cn_num} 不在转化范围内")
    return output


print(backward_cn2an_one('十五'))

