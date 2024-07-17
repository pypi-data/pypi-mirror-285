# -*- coding: utf-8 -*- #
from sklearn.metrics import f1_score
import json
import os
pre=[]
true_=[]

json_res=[]
with open('test (1).csv','r') as fw:
    lines=fw.readlines()
    for idx,line in enumerate(lines):
        if idx==0:
            continue
        p_=line.strip().split(',')
        # if len(p_)%2==0:
        split_id=int(len(p_)/2)
        up=p_[0]
        down=p_[1]
        print(up,down,sep="-----")
        assi=[]

        assi.append({'from':'user','value':up})
        assi.append({'from':'assistant','value':down})

        json_res.append({'conversations':assi})


rr=json.dumps(json_res,indent=4,ensure_ascii=False)

with open(os.path.join('long', "test.json"), 'w',encoding='utf-8') as a:
    a.write(rr)



"""



jsonresults={}
with open('test11.csv','r',encoding='gbk') as fw:
    lines=fw.readlines()
    for idx,line in enumerate(lines):
        if idx==0:
            continue

        p_=line.strip().split(',')
        print(p_)

        # jsonresults[p_[0]]=p_[-1]
        jsonresults[p_[0]]=p_[-2]



res_=json.dumps(jsonresults,indent=4,ensure_ascii=False)

with open('result1.json','w',encoding='utf-8') as fw:
    fw.write(res_)





"""