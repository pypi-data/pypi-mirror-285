txt_file_path = r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\LCQMC\train.txt'
csv_file_path = r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\LCQMC\train.csv'
json_file_path= r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\LCQMC\train.json'
import pandas as pd
import json
# 创建一个空列表来存储转换后的行
rows = []

# 打开txt文件并逐行读取
with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
    for line in txt_file:
        # 去除每行末尾的换行符，并按空格分割成列表
        features = line.strip().split()
        # 确保有足够的特征（在这个例子中是3个）
        if len(features) == 3:
            # 将特征添加到行列表中，注意列名的对应关系
            rows.append({'source1': features[0], 'source2': features[1], 'target': features[2]})

        # 使用pandas将字典列表转换为DataFrame


df = pd.DataFrame(rows)

# 合并第一列和第二列，中间用';'区分，并将新列命名为'source'
df['source'] = df['source1'].astype(str) + ';' + df['source2'].astype(str)

# 如果不再需要原始的'source'和'source2'列，可以删除它们
df.drop(['source1', 'source2'], axis=1, inplace=True)

# 将修改后的DataFrame保存为新的CSV文件
df.to_csv(csv_file_path, index=False)

# 查看新CSV文件的前五行（实际上，这里是在DataFrame中查看）
print(df.head())
# 初始化一个空列表来存储JSON对象
json_data = []

# 遍历DataFrame的每一行
for index, row in df.iterrows():
    # 构造JSON对象
    json_obj = {
        "instruction": "判断输入的两句话（以冒号为分隔符）表达的含义是否类似,如果类似或相同则输出1，如果不同则输出0",
        "input": row['source'],  # 假设CSV中的第一列名为'sour'
        "output": row['target']  # 假设CSV中的第二列名为'tar'
    }
    # 将构造的JSON对象添加到列表中
    json_data.append(json_obj)

# 将列表转换为JSON字符串，并写入文件
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("JSON文件已生成。")

# 使用with语句打开文件，确保文件在操作完成后正确关闭
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    # 使用json.load()读取文件内容到Python数据结构
    data = json.load(json_file)[:10]
    #print(data)
    print(json.dumps(data, indent=4, ensure_ascii=False))

'''
#提取json前100条数据
import json
def read_and_save_first_100_entries(input_file_path, output_file_path):
      with open(input_file_path, 'r', encoding='utf-8') as file:
          data = json.load(file)
      # 提取前100条数据
      first_100_entries = data[:1000]
      # 将前100条数据写入新的JSON文件
      with open(output_file_path, 'w', encoding='utf-8') as file:
          json.dump(first_100_entries, file, ensure_ascii=False, indent=4)
      print(f"已成功将前100条数据保存到 {output_file_path}")
input_file_path = r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\Allegro\test.json'  # 请替换为你的输入文件路径
output_file_path = r'C:\Users\Administrator\Desktop\人工智能训练师\大模型数据集\数据集二\Allegro\test1.json'  # 请替换为你的输出文件路径
read_and_save_first_100_entries(input_file_path, output_file_path)
'''