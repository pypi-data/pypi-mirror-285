# -*- coding: utf-8 -*- #
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# %matplotlib inline
# import seaborn as sns
# sns.set_style('whitegrid')
from sklearn.model_selection import train_test_split
# import warnings
# warnings.filterwarnings("ignore")
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score

def analyse_lr(train_path:str):


    train = pd.read_csv(train_path)

    x = train.drop(['PatientID', 'target'], axis=1)
    y=train['target']
    x_train, x_test, y_train,  y_test = train_test_split(x,y, test_size=.1, random_state=42)


    lr = LogisticRegression(solver='liblinear')
    lr.fit(x_train,y_train)
    print('Training score:', lr.score(x_train, y_train))
    print('*' *20)
    print('Test score:',lr.score(x_test, y_test))
    print('*' *20)
    print('f1_score:', f1_score(y_test, lr.predict(x_test)))
    print('*' *20)

    print(confusion_matrix(y_test, lr.predict(x_test)))
    print('*' *20)
    # print(classification_report(xxxxxxxx_y, lr.predict(xxxxxxxx)))
    # print(f1_score(xxxxxxxx_y, lr.predict(xxxxxxxx)))
    # arr=test['PatientID'].array
    # p_label=lr.predict(xxxxxxxx)
    #
    #
    # rr_={}
    #
    # for e in zip(arr,p_label):
    #     rr_[str(e[0])]=int(e[1])
    #
    # print(rr_)
    return lr,x_train
def save_pic(train):
    import seaborn
    # train.hist(figsize=(20, 12))
    # print('down')
    import matplotlib.pyplot as plt
    # train.plot(kind='bar')
    #train.drop(['PatientID', 'target'], axis=1)
    """


    """
    # seaborn.heatmap(train[['HighBP','BMI','Fruits']],annot=True,fmt=".1f",cmap='coolwarm')
    #(1)  各个变量数据直方图

    train.hist(figsize=(20, 12))
    plt.savefig('hist.png')

    ## 各变量之间的train.corr()相关系数的直观表示——热力图
    plt.figure(figsize=(20, 12))
    seaborn.heatmap(train.corr(), annot=True)
    plt.savefig('heatmap.png')


def save2json(lr,test_path:str):
    import json

    test = pd.read_csv(test_path)
    xxxxxxxx = test.drop(['PatientID', 'target'], axis=1)
    xxxxxxxx_y = test['target']
    print(f1_score(xxxxxxxx_y, lr.predict(xxxxxxxx)))
    arr = test['PatientID'].array
    p_label = lr.predict(xxxxxxxx)
    rr_ = {}

    for e in zip(arr, p_label):
        rr_[str(e[0])]=int(e[1])
        # rr_[str(e[0])] = 1

    res_ = json.dumps(rr_, indent=4)

    with open('result.json', 'w', encoding='utf-8') as fw:
        fw.write(res_)



if __name__=="__main__":
    fiter_,x_test=analyse_lr('train.csv')
    save_pic(x_test)
    save2json(fiter_,'test.csv')
















