import json
import os
import glob
import os.path as osp


def labelme2yolov2Seg(jsonfilePath="", resultDirPath="", classList=["buds"]):

    if (not os.path.exists(resultDirPath)):
        os.mkdir(resultDirPath)

    jsonfileList = glob.glob(osp.join(jsonfilePath, "*.json"))
    print(jsonfileList)

    for jsonfile in jsonfileList:
        with open(jsonfile, "r") as f:
            file_in = json.load(f)


            shapes = file_in["shapes"]


            with open(resultDirPath + "/" + jsonfile.split("/")[-1].replace(".json", ".txt"), "w") as file_handle:

                for shape in shapes:

                    file_handle.writelines(str(classList.index(shape["label"])) + " ")

                    # 8. 遍历shape轮廓中的每个点，每个点要进行图像尺寸的缩放，即x/width, y/height
                    for point in shape["points"]:
                        x = point[0] / file_in["imageWidth"]  # mask轮廓中一点的X坐标
                        y = point[1] / file_in["imageHeight"]  # mask轮廓中一点的Y坐标
                        file_handle.writelines(str(x) + " " + str(y) + " ")  # 写入mask轮廓点

                    # 9.每个物体一行数据，一个物体遍历完成后需要换行
                    file_handle.writelines("\n")
            # 10.所有物体都遍历完，需要关闭文件
            file_handle.close()
        # 10.所有物体都遍历完，需要关闭文件
        f.close()


if __name__ == "__main__":
    #ds

    jsonfilePath = "/datasjson"
    resultDirPath = ""
    labelme2yolov2Seg(jsonfilePath=jsonfilePath, resultDirPath=resultDirPath, classList=["0","1","2","3"])
