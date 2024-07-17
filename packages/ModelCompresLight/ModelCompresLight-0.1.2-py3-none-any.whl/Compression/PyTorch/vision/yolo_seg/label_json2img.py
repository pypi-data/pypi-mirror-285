#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import os
import os.path as osp
import sys
from multiprocessing import Process
import imgviz
import numpy as np
import cv2
import labelme
"""
"""

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )


    parser.add_argument("--input_dir", default='datas',
                        help="input annotated directory")
    parser.add_argument("--output_dir", default='out',
                        help="output dataset directory")

    parser.add_argument("--labels",
                        default="label.txt",
                        help="labels file", )

    parser.add_argument("--noviz", help="no visualization", action="store_true")


    args = parser.parse_args()


    os.makedirs(args.output_dir,exist_ok=True)
    os.makedirs(osp.join(args.output_dir, "JPEGImages"),exist_ok=True)
    os.makedirs(osp.join(args.output_dir, "SegmentationClass"),exist_ok=True)
    os.makedirs(osp.join(args.output_dir, "SegmentationClassPNG"),exist_ok=True)
    if not args.noviz:
        os.makedirs(
            osp.join(args.output_dir, "SegmentationClassVisualization"),exist_ok=True
        )
    os.makedirs(osp.join(args.output_dir, "SegmentationObject"),exist_ok=True)
    os.makedirs(osp.join(args.output_dir, "SegmentationObjectPNG"),exist_ok=True)
    if not args.noviz:
        os.makedirs(
            osp.join(args.output_dir, "SegmentationObjectVisualization"),exist_ok=True
        )
    print("Creating dataset:", args.output_dir)

    class_names = []
    class_name_to_id = {}
    for i, line in enumerate(open(args.labels).readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        class_name_to_id[class_name] = class_id
        if class_id == -1:
            assert class_name == "__ignore__"
            continue
        elif class_id == 0:
            assert class_name == "_background_"
        class_names.append(class_name)
    class_names = tuple(class_names)
    print("class_names:", class_names)
    out_class_names_file = osp.join(args.output_dir, "class_names.txt")
    with open(out_class_names_file, "w") as f:
        f.writelines("\n".join(class_names))
    print("Saved class_names:", out_class_names_file)

    files=glob.glob(osp.join(args.input_dir, "*.json"))


    def fun(filenames):
        for filename in filenames:
            print("Generating dataset from:", filename)

            label_file = labelme.LabelFile(filename=filename)

            base = osp.splitext(osp.basename(filename))[0]
            out_img_file = osp.join(args.output_dir, "JPEGImages", base + ".jpg")
            out_cls_file = osp.join(
                args.output_dir, "SegmentationClass", base + ".npy"
            )
            out_clsp_file = osp.join(
                args.output_dir, "SegmentationClassPNG", base + ".png"
            )
            if not args.noviz:
                out_clsv_file = osp.join(
                    args.output_dir,
                    "SegmentationClassVisualization",
                    base + ".jpg",
                )
            out_ins_file = osp.join(
                args.output_dir, "SegmentationObject", base + ".npy"
            )
            out_insp_file = osp.join(
                args.output_dir, "SegmentationObjectPNG", base + ".png"
            )
            if not args.noviz:
                out_insv_file = osp.join(
                    args.output_dir,
                    "SegmentationObjectVisualization",
                    base + ".jpg",
                )

            img = labelme.utils.img_data_to_arr(label_file.imageData)
            imgviz.io.imsave(out_img_file, img)

            cls, ins = labelme.utils.shapes_to_label(
                img_shape=img.shape,
                shapes=label_file.shapes,
                label_name_to_value=class_name_to_id,
            )
            # ins[cls == -1] = 0  # ignore it.

            # class label
            # labelme.utils.lblsave(out_clsp_file, cls)
            cv2.imwrite(out_clsp_file,cls)
            np.save(out_cls_file, cls)

            # instance label
            labelme.utils.lblsave(out_insp_file, ins)
            np.save(out_ins_file, ins)

    # ins=112
    # for ii in range(45):
    #
    #     if (ii*ins+ins)>len(files):
    #         p = Process(target=fun, args=(files[ii*ins:-1],))
    #         p.start()
    #     else:
    #         p = Process(target=fun,args=(files[ii*ins:ii*ins+ins],))
    #         p.start()
    # for fir in files:

    fun(files)


if __name__ == "__main__":
    main()
