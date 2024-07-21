import os
import json
import numpy as np
json_dir = r'C:\Users\Administrator\Desktop\transport\分割数据集\all\json'
save_dir = r'C:\Users\Administrator\Desktop\transport\分割数据集\all\labels'

def txt_write(x, img_x, img_y, txt):
    data = x['points']
    n = 1
    for x in data:
        for i in x:
            if n % 2 == 0:
                txt.write(' ' + str(round(i / img_x, 6)))
                n += 1
            else:
                txt.write(' ' + str(round(i / img_y, 6)))
                n += 1
    txt.write('\n')


def json2txt(json_path, save_path):
    txt = open(save_path, 'w')
    with open(json_path, "r") as f:
        data = f.read()
    data = json.loads(data)
    img_x = data['imageHeight']
    img_y = data['imageWidth']
    shapes = data['shapes']

    for x in shapes:

        if x['label'] == 'car':  # 标签名
            txt.write('0')  # 标签类别
            txt_write(x, img_x, img_y, txt)

        if x['label'] == 'biao':  # 同上
            txt.write('1')
            txt_write(x, img_x, img_y, txt)

        if x['label'] == 'pai':  # 同上
            txt.write('2')
            txt_write(x, img_x, img_y, txt)
    txt.close()

files = os.listdir(json_dir)
os.makedirs(save_dir, exist_ok=True)
num = 1
for file in files:
    name = file[0:-5]
    json_path = json_dir + '/' + name + '.json'
    save_path = save_dir + '/' + name + '.txt'
    json2txt(json_path, save_path)
    print(num, '/', len(files), ':', name)
    num += 1