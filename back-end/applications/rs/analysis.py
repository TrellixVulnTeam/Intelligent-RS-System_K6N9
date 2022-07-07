import copy
import json

from applications.common.path_global import generate_dir, fun_type_1, fun_type_2, fun_type_3, fun_type_4, fun_type_5, \
    fun_type_6, fun_type_7, generate_url, fun_type_8, up_url
from applications.common.utils.upload import img_url_handle
from applications.extensions import db
from applications.image_processing import histogram_match
from applications.image_processing.CLAHE import CLAHE
from applications.image_processing.GaussianBlur import Gaussian_Blur
from applications.image_processing.MedianBlur import Median_Blur
from applications.image_processing.Resize import Resize
from applications.image_processing.XuanRan import bitch_xuanran
from applications.image_processing.hole import hole_fill
from applications.image_processing.ruihua import RuiHua
from applications.image_processing.xuanran_seg import bitch_xuanran_seg
from applications.models.admin_analysis import AdminAnalysis
from applications.rs import CD, OD, Seg, TC


def saveAnalysis(uid, type_, pic1, retPic, pic2="", data="{}", is_hole=False, checked="0,0"):
    analysis = AdminAnalysis()
    analysis.uid = uid
    analysis.type = type_
    analysis.before_img = pic1
    analysis.before_img1 = pic2
    analysis.after_img = retPic
    analysis.data = data
    analysis.is_hole = is_hole
    analysis.checked = checked
    db.session.add(analysis)
    db.session.commit()


def change_detection(model_path, data_path, out_dir, names, step1, step2, uid, type_):
    """
    变化检测
    :param modir_path: 静态图模型路径
    :param data_path: 图片数据路径，路径中有名称为A和B的两个文件夹分别存储不同时相的图片（1024，1024），且相应图片名称相同
    :param out_dir:图片保存路径
    :return:
    """
    print("变化检测----------------->start")
    imgs = list()
    imgs1 = list()
    temp_names = copy.deepcopy(names)
    for pair in names:
        pair["first"] = img_url_handle(pair["first"])
        pair['second'] = img_url_handle(pair['second'])
        imgs.append(pair["first"])
        imgs1.append(pair["second"])

    # 1.直图or锐化
    if step1 != 0:
        if step1 == fun_type_1:
            imgs = handle(step1, names, data_path, data_path)
        else:
            imgs = handle(step1, imgs, data_path, data_path)
            imgs1 = handle(step1, imgs1, data_path, data_path)
    # 2.平滑or滤波
    if step2 != 0:
        imgs = handle(step2, imgs, data_path, data_path)
        imgs1 = handle(step2, imgs1, data_path, data_path)

    # 3.resize
    resizes = Resize(data_path, data_path, imgs, mode=0)
    resizes1 = Resize(data_path, data_path, imgs1, mode=0)
    i = 0
    for pair in names:
        pair["first"] = resizes[i]
        pair["second"] = resizes1[i]
        i += 1
    # 3.检测对比，带地址的文件名，纯文件名
    retPics, temps1 = CD.execute(model_path, data_path, out_dir, names)
    # 4.检测渲染
    res = handle(fun_type_6, temps1, out_dir, out_dir)
    # 5.入库
    i = 0
    for pair in temp_names:
        #first_ = pair["first"]
        first_= up_url+resizes[i]
        second_ = pair['second']
        retPic = retPics[i]
        data = json.dumps(res[i])
        saveAnalysis(uid, type_, first_, retPic, pic2=second_, data=data, checked=str(step1) + "," + str(step2))
        i += 1
        pass
    print("变化检测----------------->end")


def hole_handle(data_path, out_dir, names):
    url_handle(names)
    # 1.孔洞处理
    res = handle(fun_type_8, names, data_path, out_dir)
    # 4.检测渲染
    res1 = handle(fun_type_6, res, out_dir, out_dir)
    return generate_url+res[0], json.dumps(res1[0])
    pass


def url_handle(imgs):
    j = 0
    for pair in imgs:
        imgs[j] = img_url_handle(pair)
        j += 1
    pass


def object_detection(model_path, data_path, out_dir, names, step1, step2, uid, type_):
    """
    目标检测
    :param model_path:
    :param data_path:
    :param out_dir:
    :return:
    """
    print("目标检测----------------->start")
    imgs = list()
    temp_names = copy.deepcopy(names)
    for j, pair in enumerate(names):
        names[j] = img_url_handle(pair)
        imgs.append(names[j])

    # 3.resize
    resizes = Resize(data_path, data_path, imgs, mode=3)
    for i, pair in enumerate(imgs):
        imgs[i] = resizes[i]

    # 1.CLAHE or 锐化
    if step1 != 0:
        imgs = handle(step1, imgs, data_path, data_path)
    # 2.平滑or滤波
    if step2 != 0:
        imgs = handle(step2, imgs, data_path, data_path)

    # 4. 目标检测
    retPics = OD.execute(model_path, data_path, out_dir, imgs)
    # 5.入库
    for i, pair in enumerate(resizes):
        first_ = up_url+pair
        retPic = retPics[i]
        saveAnalysis(uid, type_, first_, retPic, pic2="", data="", checked=str(step1) + "," + str(step2))
        pass
    print("目标检测----------------->end")


def segmenter(model_path, data_path, out_dir, names, step1, step2, uid, type_):
    """
    目标提取
    :param model_path:
    :param data_path:
    :param out_dir:
    :return:
    """
    print("目标提取----------------->start")
    imgs = list()
    temp_names = copy.deepcopy(names)
    for j, pair in enumerate(names):
        names[j] = img_url_handle(pair)
        imgs.append(names[j])
    # 3.resize
    resizes = Resize(data_path, data_path, imgs, mode=1)
    for i, pair in enumerate(imgs):
        imgs[i] = resizes[i]
    # 1.CLAHE or 锐化
    if step1 != 0:
        imgs = handle(step1, imgs, data_path, data_path)
    # 2.平滑or滤波
    if step2 != 0:
        imgs = handle(step2, imgs, data_path, data_path)


    # 4. 目标提取
    retPics, temps1 = Seg.execute(model_path, data_path, out_dir, imgs)
    # 4.检测渲染
    res = handle(fun_type_7, temps1, out_dir, out_dir)
    # 5.入库
    for i, pair in enumerate(resizes):
        first_ = up_url+pair
        retPic = retPics[i]
        data = json.dumps(res[i])
        saveAnalysis(uid, type_, first_, retPic, pic2="", data=data, checked=str(step1) + "," + str(step2))
        pass
    print("目标提取----------------->end")


def terrain_classification(model_path, data_path, out_dir, names, step1, step2, uid, type_):
    """
    地物分类
    :param model_path:
    :param data_path:
    :param out_dir:
    :return:
    """
    print("地物分类----------------->start")
    imgs = list()
    temp_names = copy.deepcopy(names)
    for j, pair in enumerate(names):
        names[j] = img_url_handle(pair)
        imgs.append(names[j])
    # 3.resize
    resizes = Resize(data_path, data_path, imgs, mode=2)
    for i, pair in enumerate(imgs):
        imgs[i] = resizes[i]

    # 1.CLAHE or 锐化
    if step1 != 0:
        imgs = handle(step1, imgs, data_path, data_path)
    # 2.平滑or滤波
    if step2 != 0:
        imgs = handle(step2, imgs, data_path, data_path)

    # 4. 地物分类
    retPics = TC.execute(model_path, data_path, out_dir, imgs)
    # 5.入库
    for i, pair in enumerate(resizes):
        first_ = up_url+pair
        retPic = retPics[i]
        saveAnalysis(uid, type_, first_, retPic, pic2="", data="", checked=str(step1) + "," + str(step2))
        pass
    print("地物分类----------------->end")


def handle(fun_type, imgs, src_dir, save_dir):
    """

    :param fun_type:
            1=变化检测渲染，
            2=对比度自适应直方图均衡化(CLAHE)，
            3=平滑(中值滤波)，
            4=目标提取渲染，
            5=直方图匹配，
            6=锐化，
            7=高斯滤波

            1=直方图匹配，
            2=对比度自适应直方图均衡化(CLAHE)，
            3=平滑(中值滤波)，
            4=锐化，
            5=高斯滤波
            6=变化检测渲染，
            7=目标提取渲染，
            8=孔洞填充(用于变化检测结果图处理)
    """
    temps = list()
    if fun_type == fun_type_1:
        temps = histogram_match.gram_match(imgs, src_dir, save_dir, False)
    elif fun_type == fun_type_2:
        temps = CLAHE(src_dir, save_dir, imgs)
    elif fun_type == fun_type_3:
        temps = Median_Blur(src_dir, save_dir, imgs)
    elif fun_type == fun_type_4:
        temps = RuiHua(src_dir, save_dir, imgs)
        pass
    elif fun_type == fun_type_5:
        temps = Gaussian_Blur(src_dir, save_dir, imgs)
    elif fun_type == fun_type_6:
        temps = bitch_xuanran(src_dir, save_dir, imgs)
    elif fun_type == fun_type_7:
        temps = bitch_xuanran_seg(src_dir, save_dir, imgs)
    elif fun_type == fun_type_8:
        temps = hole_fill(src_dir, save_dir, imgs)
        pass
    return temps
