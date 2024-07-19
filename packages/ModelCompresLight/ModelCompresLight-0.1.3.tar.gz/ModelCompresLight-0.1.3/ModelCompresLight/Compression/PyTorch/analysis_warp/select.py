# -*- coding: utf-8 -*- #
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
"""
if you want to edit in this jupyter you should edit follow
 %matplotlib inline
 import seaborn as sns
sns.set_style('whitegrid')

"""
def ordiam_(train_path:str,drop_ed_collom,out_label):
    """
    show imgs in_demo   lr.score(x_train, y_train))
    :param train_path:
    :param drop_ed_collom:
    :param out_label:
    :return:
    """
    train = pd.read_csv(train_path)
    x = train.drop(drop_ed_collom, axis=1)
    y=train['out_label']
    x_train, x_test, y_train,  y_test = train_test_split(x,y, test_size=.1, random_state=42)
    lr = LogisticRegression(solver='liblinear')
    lr.fit(x_train,y_train)
    return lr,x_train

def ordiam_with_selct(train_path:str,drop_ed_collom,s,k_nb):
    """
    :param train_path:
    :return:
    """
    train = pd.read_csv(train_path)

    x = train.drop(drop_ed_collom, axis=1)
    y=train['out_label']
    x_train, x_test, y_train,  y_test = train_test_split(x,y, test_size=.1, random_state=42)
    select_k_best = SelectKBest(chi2, k=k_nb)
    X_train_selected = select_k_best.fit_transform(x_train, y_train)
    lr = LogisticRegression(solver='saga', class_weight={0: 1, 1: 15})
    # lr = LogisticRegression(solver='liblinear')
    lr.fit(x_train,y_train)
    return lr,x_train


def save_pic(train,out_name):
    """
    save what you want
    :param train:
    :param out_name:
    :return:
    """
    import seaborn
    import matplotlib.pyplot as plt
    train.hist(figsize=(20, 12))
    plt.figure(figsize=(20, 12))
    seaborn.heatmap(train.corr(), annot=True)
    plt.savefig('out_name.png')

    return

def writexmlsorjson(lr,test_path:str,clume,out_name):
    import json

    test = pd.read_csv(test_path)
    test__x = test.drop(clume, axis=1)
    test__y = test['y']
    arr = test['array'].array
    p_label = lr.predict(test__x)
    rr_ = {}

    for e in zip(arr, p_label):
        rr_[str(e[0])]=int(e[1])
        # rr_[str(e[0])] = 1
    res_ = json.dumps(rr_, indent=4)
    with open(out_name, 'w', encoding='utf-8') as fw:
        fw.write(res_)


if __name__=="__main__":
    fiter_,x_test=ordiam_('train.csv',['cli1','col2'],'y')

















