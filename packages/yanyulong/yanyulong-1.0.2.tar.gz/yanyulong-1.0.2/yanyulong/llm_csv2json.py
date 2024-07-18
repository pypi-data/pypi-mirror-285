
csv_file_path = r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\Allegro\train.csv'  # 请替换为你的Excel文件路径
json_file_path= r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\Allegro\train.json'

import pandas as pd
import json

df = pd.read_csv(csv_file_path)

print(df.head())
# 初始化一个空列表来存储JSON对象
json_data = []

# 遍历DataFrame的每一行
for index, row in df.iterrows():
    # 构造JSON对象
    json_obj = {
        "instruction": "将输入内容的含义简化总结后输出",
        "input": row['source'],
        "output": row['target']
    }
    # 将构造的JSON对象添加到列表中
    json_data.append(json_obj)

# 将列表转换为JSON字符串，并写入文件
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("JSON文件已生成。")


with open(json_file_path, 'r', encoding='utf-8') as json_file:
    # 使用json.load()读取文件内容到Python数据结构
    data = json.load(json_file)[:10]
    # 打印数据以预览
    #print(data)
    print(json.dumps(data, indent=4, ensure_ascii=False))