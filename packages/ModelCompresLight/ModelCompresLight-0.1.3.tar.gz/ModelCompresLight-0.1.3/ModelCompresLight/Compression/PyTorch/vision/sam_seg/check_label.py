import json
import os
import glob
import os.path as osp


def labelme2yolov2Seg(jsonfilePath="", resultDirPath="", classList=["buds"]):
    """
    此函数用来将labelme软件标注好的数据集转换为yolov5_7.0sege中使用的数据集
    :param jsonfilePath: labelme标注好的*.json文件所在文件夹
    :param resultDirPath: 转换好后的*.txt保存文件夹
    :param classList: 数据集中的类别标签
    :return:
    """

    jsonfileList = glob.glob(osp.join(jsonfilePath, "*.json"))
    print(jsonfileList)  # 打印文件夹下的文件名称


    # 2.遍历json文件，进行转换


    for jsonfile in jsonfileList:
        # 3. 打开json文件
        labels = []
        with open(jsonfile, "r") as f:
            file_in = json.load(f)

            shapes = file_in["shapes"]


            for shape in shapes:


                label=shape['label']
                if label not in labels:
                    labels.append(label)

        print(labels)


if __name__ == "__main__":
    #ds

    jsonfilePath = "datas"  # 要转换的json文件所在目录
    labelme2yolov2Seg(jsonfilePath=jsonfilePath)  # 更改为自己的类别名
