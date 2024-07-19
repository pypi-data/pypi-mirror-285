# -*-coding: utf-8 -*-
"""
    @Author : PKing
    @E-mail :
    @Date   : 2024-02-05 18:19:18
    @Brief  :
"""
import os
import cv2
import numpy as np
import random
from tqdm import tqdm
from pybaseutils import image_utils, file_utils, json_utils, base64_utils, time_utils
from pybaseutils.cvutils import video_utils
from pybaseutils.transforms import transform_utils
from pybaseutils.converter import build_voc, build_labelme
from pybaseutils.dataloader import parser_labelme
import xmltodict


def read_xml2json(file):
    """
    import xmltodict
    :param file:
    :return:
    """
    with open(file, encoding='utf-8') as fd:  # 将XML文件装载到dict里面
        content = xmltodict.parse(fd.read())
    return content


def maker_cvat(xml_file, points, labels, image_name, image_size):
    """
    制作label数据格式
    :param xml_file: 保存json文件路径
    :param points: (num_labels,num_points,2), points = image_utils.boxes2polygons(boxes)
    :param labels: (num_labels,)
    :param image_name: 图片名称，如果存在则进行拷贝到json_file同一级目录
    :param image_size: (W,H)
    :param image_bs64: 图片base64编码，可为None
    :return:
    """
    assert len(points) == len(labels)
    file_utils.create_file_path(xml_file)
    objects = []
    for point, label in zip(points, labels):
        if isinstance(point, np.ndarray): point = point.tolist()
        if not isinstance(point[0], list): point = [point]
        pt = [{'x': p[0], 'y': p[1]} for p in point]
        item = {'name': label,
                'deleted': '0',
                'verified': '0',
                'occluded': 'no',
                'date': None,
                'id': '0',
                'parts': {'hasparts': None, 'ispartof': None},
                'polygon': {'pt': pt, 'username': None},
                'attributes': None}
        objects.append(item)
    data_info = {
        "annotation": {
            'filename': os.path.basename(image_name),
            'folder': "",
            'source': {'sourceImage': None, 'sourceAnnotation': 'Datumaro'},
            'imagesize': {'nrows': image_size[1], 'ncols': image_size[0]},
            'object': objects
        }}
    if os.path.exists(image_name): file_utils.copy_file_to_dir(image_name, os.path.dirname(xml_file))
    data_info = xmltodict.unparse(data_info)
    with open(xml_file, 'w') as xml_file:
        xml_file.write(data_info)
    return data_info


if __name__ == '__main__':
    video_file = "/media/PKing/Elements SE/NVR/NVR_ch2_main_20240716143915_20240716153215.dav"
    save_video = "/home/PKing/Downloads/NVR_ch2_main_20240716143915_20240716153215.mp4"
    video_cap = video_utils.video_iterator(video_file, save_video, speed=1)
    for data_info in video_cap:
        frame = data_info["frame"]
        image_utils.cv_show_image("image", frame, delay=5)
