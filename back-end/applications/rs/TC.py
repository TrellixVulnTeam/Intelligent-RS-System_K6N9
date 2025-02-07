from os import listdir
import os.path as osp
import paddlers as pdrs
from skimage.io import imsave
import numpy as np
import cv2

from applications.common.path_global import md5_name, generate_url


def get_lut():
    lut = np.zeros((256, 3), dtype=np.uint8)
    lut[0] = [255, 0, 0]  # 红
    lut[1] = [30, 255, 142]  # 浅绿
    lut[2] = [60, 0, 255]  # 蓝
    lut[3] = [255, 222, 0]  # 橙黄
    lut[4] = [0, 0, 0]  # 黑
    return lut


def execute(model_path, data_path, out_dir,test_names):
    image_list = [osp.join(data_path, name) for name in test_names]
    predictor = pdrs.deploy.Predictor(model_path, use_gpu=True)
    pred = predictor.predict(image_list)
    ims = [i['label_map'] for i in pred]
    lut = get_lut()
    temps = list()
    for idx, im in zip(range(len(image_list)), ims):
        if im.ndim == 3:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = lut[im]
        new_name = md5_name(test_names[idx])
        imsave(osp.join(out_dir,new_name), im)
        temps.append(generate_url + new_name)
    return temps
