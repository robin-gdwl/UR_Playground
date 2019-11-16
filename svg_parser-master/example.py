# -*- coding:utf-8 -*-

from __future__ import division
from svg.path import parse_path

import numpy as np
from xml.dom import minidom
import time

def svg_to_np(svg_file_name, sample_len=20, original_flag=False):
    """Parse the svg file to coordinate sequence.
    Args:
        svg_file_name: The path of the svg file.
        sample_len: dot sample parameter, the larger sample_len is, the less dot will get. Only works when original_flag is Fasle.
        original_flag: If True, get the original coordinates. If False, get the sampled coordinates.
    Returns:
        image_coord: numpy.ndarray with shape [n_dot, 3], coordinate sequence. Each line denotes the location for a dot [x, y, is_end]
        if is_end == 1, the dot is the end of a stroke.
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


if __name__ == '__main__':
    tic = time.time()
    svg_file = 'data/airplane/1.svg'
    coord = svg_to_np(svg_file, original_flag=True)
    print('Time cost {}s'.format(time.time() - tic))
    print(coord.shape)
    print(coord)
