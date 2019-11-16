# -*- coding:utf-8 -*-

from __future__ import division
import os
import tools as myTools
from svg.path import parse_path

import numpy as np
from xml.dom import minidom
from multiprocessing import Pool
import time

import logging.handlers

"""Parse the tu-berlin svg dataset to coordinate sequences.
Get the tu-berlin svg dataset: http://cybertron.cg.tu-berlin.de/eitz/projects/classifysketch/sketches_svg.zip
"""

LOG_FILE = 'parser.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger('svg_to_np')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

svg_fold = './tuberlinsvg/'


def svg_to_np(svg_file_name, sample_len=20, original_flag=False):
    """Parse the svg file to coordinate sequence.
    Args:
        svg_file_name: The path of the svg file.
        sample_len: dot sample parameter, the larger sample_len is, the less dot will get. Only works when original_flag is Fasle.
        original_flag: If True, get the original coordinates. If False, get the sampled coordinates.
    Returns:

    """
    xml_file = minidom.parse(svg_file_name)
    paths = xml_file.getElementsByTagName("path")
    xcoords = []
    ycoords = []
    pcoords = []
    for path_idx, path_element in enumerate(paths):
        mypath = parse_path(path_element.attributes["d"].value)
        # len(mypath)...number of offsets/segments
        try:
            mypath_len = int(mypath.length())  # strokeLen...natural length of the whole stroke
        except ZeroDivisionError:
            mypath_len = 0
        if original_flag | (mypath_len < sample_len):
            xcoords.append(mypath[0].start.real)
            ycoords.append(mypath[0].start.imag)
            pcoords.append(0.0)
            for offset_idx in range(len(mypath)):
                xcoords.append(mypath[offset_idx].end.real)
                ycoords.append(mypath[offset_idx].end.imag)
                pcoords.append(0.0)
            pcoords[-1] = 1.0
        else:
            # Divide a stroke into max_iter dots.
            # The larger sample_len is, the less dot will get.
            max_iter = mypath_len / sample_len
            x = 0.0
            for i in range(int(max_iter)):
                xcoords.append(mypath.point(x).real)
                ycoords.append(mypath.point(x).imag)
                pcoords.append(0.0)
                x = np.float32(x + (1 / max_iter))
            xcoords.append(mypath.point(1.0).real)
            ycoords.append(mypath.point(1.0).imag)
            pcoords.append(1.0)
    image_coord = np.column_stack((np.asarray(xcoords), np.asarray(ycoords), np.asarray(pcoords)))
    return image_coord


def convert_function(category_name):
    category_flod = svg_fold + category_name
    npy_fold = category_flod.replace('svg', 'npy')
    if not os.path.exists(npy_fold):
        os.makedirs(npy_fold)
    # sampleLen can me modified in a way that it changes its values according to segment length
    datas = myTools.folder2files(category_flod, format='.svg')
    for svg_file_path in datas:
        print(svg_file_path)
        try:
            image_coord = svg_to_np(svg_file_path)
            # putting imageCord in the allDataset npy
            npy_file_path = svg_file_path.replace('svg', 'npy')
            np.save(npy_file_path, image_coord)
        except Exception as e:
            logger.info('Error: file_name= {}'.format(svg_file_path))
            logger.info(e.message)


def main():
    tic = time.time()
    p = Pool()
    svg_folder_list = os.listdir(svg_fold)
    p.map(convert_function, svg_folder_list)
    p.close()
    p.join()
    print('Finished, time cost {}s'.format(time.time() - tic))


if __name__ == '__main__':
    main()
