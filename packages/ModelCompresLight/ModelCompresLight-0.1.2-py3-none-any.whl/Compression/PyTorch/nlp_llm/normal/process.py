# -*- coding: utf-8 -*- #
import csv
import json


csv_file_path ="test.csv"
json_file_path ="test.json"
dic_list = []
with open(csv_file_path, 'r', encoding='gbk') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i != 0:
            dic = {}
            dic["sentence1"] = row[1]
            dic["sentence2"] = row[2]
            dic["label"] = row[3]
            dic["id"] = row[0]
            print(dic)
            dic_list.append(dic)

with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(dic_list, f, ensure_ascii=False)



