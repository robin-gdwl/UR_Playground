from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
from sklearn import preprocessing
import numpy as np
from xml.dom import minidom
from scipy import ndimage
import glob
from subprocess import call
import random
from shutil import copyfile

from skimage import io, color, img_as_ubyte
import sys

import xml.etree.ElementTree as ET

from svgpathtools import parse_path
from svgpathtools import wsvg


def get_path_strings(svgfile):
    """
    This function gets the list of paths from svgFile
    It needs: import xml.etree.ElementTree as ET
    """

    tree = ET.parse(svgfile)
    p = []
    for elem in tree.iter():
        if elem.attrib.has_key('d'):
            p.append(elem.attrib['d'])
    return p


def folder2files(dataDir, format='.png'):
    """
    Function: It creates a list of all the files present in all the
              subfolders of dataDir.
    Input:
        dataDir: folder path containing the subfolders where the
                 files of interest are present.
    Output:
        dataList: list of files in the subfolders of dataDir.
    N.B.: It needs import os.
    """
    dataList = []
    for dirName, subdirList, fileList in os.walk(dataDir):
        # print('Found directory: %s' % dirName)
        dataList = dataList + sorted(glob.glob(dirName + '/*' + format))

    """ OLD VERSION
    dataList = []
    subdirs = [x[0] for x in os.walk(dataDir)]
    for subdir in subdirs[1:]:
        dataList = dataList + glob.glob(subdir+"/*"+format)
    """
    return dataList


def list2dic(dataList):
    """
    Function: It creates a dictionary with keys = folder/class names
                and values = all file paths for the corresponding keys.
    Input:
        dataList: list of file paths containing subfolders which
                    represent classes.
    Output:
        dataDic: dictionary of keys = classes and values = filepaths.
    """
    dataDic = {}
    for dataFile in dataList:
        try:
            dataDic[dataFile.split('/')[-2]].append(dataFile)
        except:
            dataDic[dataFile.split('/')[-2]] = [dataFile]
    return dataDic


def folder2dic(dataDir, format='.png'):
    return list2dic(folder2files(dataDir, format))


def labelNumTxtCreation(dataDic, saveTxtPath):
    labelEncoder = preprocessing.LabelEncoder()
    labelEncoder.fit(dataDic.keys())

    f = open(saveTxtPath, "w+")
    for dataKey in dataDic.keys():
        f.write("%s: %04d \n" % (str(dataKey), int(labelEncoder.transform(str(dataKey)))))

    f.close()


def label2numDic(dataDic, labelNumFile):
    with open(labelNumFile) as f:
        for line in f:
            dataDic[str(int(line.split(':')[1]))] = dataDic.pop(str(line.split(':')[0]))

    return dataDic


def num2labelDic(dataDic, labelNumFile):
    with open(labelNumFile) as f:
        for line in f:
            dataDic[str(line.split(':')[0])] = dataDic.pop(str(int(line.split(':')[1])))

    return dataDic


def listRandomN(dataList, elementsN):
    """
    Function: It extracts randomly N elements from the input list.
    Input:
        dataList: list of elements.
        elementsN: number of elements to be extracted from the list.
    Output:
        list of randomly selected N elements from the input list.
    N.B: It needs import random.
    """
    return [dataList[x] for x in sorted(random.sample(xrange(len(dataList)), elementsN))]


def dicRandomNValues(dataDic, elementsN):
    """
    Function: It creates a dictionary where randomly N elements are
                extracted from each value (list of elements)
                corresponding to each key of the input dictionary.
    Input:
        dataDic: input dictionary containing values (list of elements)
                    and keys.
        elementsN: number of elements to be extracted from each
                    value (list of elements) of each key in the input
                    dictionary.
    Output:
        dictionary containing updated values (N extracted elements) and
        keys.
    N.B: It needs listRandomN function.
    """
    return {key: listRandomN(value, elementsN) for key, value in dataDic.items()}


def l1removel2(mainList, removeList):
    """
    Function: It removes the elements in removeList from mainList.
    Input:
        mainList: list of reference.
        removeList: list containing elements which are removed from
            the reference list.
    Output:
        [mainList without the elements of removeList]
    """
    return [x for x in mainList if x not in removeList]


def d1removed2(mainDic, removeDic):
    """
    Function: mainDic and removeDic are two dictionaries containing
                the same keys but different values (which are lists of
                elements). This function removes the elements in lists
                (values) of removeDic from the lists of mainDic.
    Input:
        mainDic: dictionary of reference.
        removeDic: dictionary containing lists of elements (each list =
                    value) which are removed from the reference
                    dictionary lists.
    Output:
        [mainDic without the elements in the lists (values) of
        removeDic]
    """
    return {key: l1removel2(value, removeDic.get(key)) for key, value in mainDic.items()}


def dataSplit(dataDic, trainN, validN, testN):
    """
    Function: It splits the data in the dataDic randomly into training
                set dictionary - trainDic, validation set dictionary -
                validDic and testing set dictionary - testDic.
    Input:
        dataDic: dictionary containing the whole data.
        trainN:
    Output:

    """
    trainDic = dicRandomNValues(dataDic, trainN)
    dataDic = d1removed2(dataDic, trainDic)
    validDic = dicRandomNValues(dataDic, validN)
    dataDic = d1removed2(dataDic, validDic)
    testDic = dicRandomNValues(dataDic, testN)

    return trainDic, validDic, testDic


# Temporart tools - start

def pngList2svgList(pngFilesList, srcDirName, desDirName):
    """
    Function: Its a auxiliary function to create the list of svg files
                from the png files. Its needed since I don't have the
                160 class TU Berlin DB in svg format. So I get the list
                of 160 class TU Berlin DB in png format and then modify
                that list to extract svg files from 250 class TU Berlin
                DB in svg fomat.
    Input:
        pngFilesList: list of png file paths.
    Output:
        svgFilesList: list of corresponding svg file paths in svg folder.
    """

    return [f.replace(srcDirName, desDirName).replace('png', 'svg') \
            for f in pngFilesList]


def dbClassFolderCreation(mainDic, desDir):
    [os.makedirs(desDir + key) for key in mainDic.keys() if not os.path.exists(desDir + key)]


def list2folder(dataList, desDir):
    [copyfile(fileName, desDir + os.path.basename(fileName)) for fileName in dataList]


def dic2folder(dataDic, desDir):
    [list2folder(dataDic.get(key), desDir + key + "/") for key in dataDic.keys()]


def strokesSrc2Des(srcDir, desDir):
    """
    Function: It creates the sequential images of the accumulated
                strokes of the sketches.
    Input:
        srdDir: folder path containing the svg files of skteches.
        desDir: folder path where the output svg files will be saved.
    Output:
        None [Svg files are saved in the desDir]
    N.B: It needs import glob, from xml.dom import minidom.
    """
    svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    for svgFileName in svgFiles:
        svgFile = minidom.parse(svgFileName)
        _name = svgFile.getElementsByTagName("g")[0]
        _name = _name.getElementsByTagName("g")[0]
        strokes = _name.getElementsByTagName("path")
        idx_tot = len(strokes)

        for idx, removeStroke in enumerate(reversed(strokes)):
            with open(desDir
                              + ("%05d" % int(svgFileName.split("/")[-1].split(".")[0]))
                              + "-"
                              + ("%04d" % (idx_tot - idx - 1)) + ".svg", "w") as f:
                f.write(svgFile.toxml())
            parentNode = removeStroke.parentNode
            parentNode.removeChild(removeStroke)


def separateStrokesSrc2Des(srcDir, desDir):
    """
    Function: It creates the separate image for each stroke.
    Input:
        srdDir: folder path containing the svg files of skteches.
        desDir: folder path where the output svg files will be saved.
    Output:
        None [Svg files are saved in the desDir]
    N.B: It needs import glob, from xml.dom import minidom.
    """
    svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    for svgFileName in svgFiles:

        if not os.path.exists(desDir + svgFileName.split('/')[-1][:-4]):
            os.makedirs(desDir + svgFileName.split('/')[-1][:-4])

        svgFile1 = minidom.parse(svgFileName)
        _name1 = svgFile1.getElementsByTagName("g")[0]
        _name1 = _name1.getElementsByTagName("g")[0]
        strokes1 = _name1.getElementsByTagName("path")

        svgFile2 = minidom.parse(svgFileName)
        _name2 = svgFile2.getElementsByTagName("g")[0]
        _name2 = _name2.getElementsByTagName("g")[0]
        strokes2 = _name2.getElementsByTagName("path")

        idx_tot = len(strokes1)

        for idx, removeStroke2 in enumerate(reversed(strokes2)):
            parentNode2 = removeStroke2.parentNode
            parentNode2.removeChild(removeStroke2)

        for idx, extractStroke1 in enumerate(strokes1):
            parentNode2.appendChild(extractStroke1)
            with open(desDir + svgFileName.split('/')[-1][:-4]
                              + "/"
                              + str(idx + 1) + ".svg", "w") as f:
                f.write(svgFile2.toxml())
            parentNode2.removeChild(extractStroke1)


def compoundPath2simplePath(srcDir, desDir):
    svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    svg_attribute = {u'height': u'256px', u'width': u'256px'}

    for svgFileName in svgFiles:
        svgFile = get_path_strings(svgFileName)
        svgMList = svgFile[0].split('M')
        svgMList = svgMList[1:]
        svgMList = ['M' + MEle for MEle in svgMList]
        svgPathList = [parse_path(MEle) for MEle in svgMList]
        wsvg(svgPathList, svg_attributes=svg_attribute, filename=desDir + '/' + svgFileName)


# from svgpathtools import parse_path
# from svgpathtools import wsvg
# path_alt = parse_path(svgMList[2])
# doc = ET.Element('svg', width='256', height='256', version='1.1', xmlns='http://www.w3.org/2000/svg')

def addTansformAtt(svgFiles, desDir, imgSize, scaleFac):
    """
    adding transform attribute to the sencond g in svg file. The transform attribute will have scale component of value scaleFac
    """
    # svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    for svgFileName in svgFiles:

        if not os.path.exists(desDir + svgFileName.split('/')[-2]):
            os.makedirs(desDir + svgFileName.split('/')[-2])

        svgFile = minidom.parse(svgFileName)
        # modifiying an attribute value
        _name = svgFile.getElementsByTagName("svg")[0]
        _name.attributes['viewBox'].value = u'0 0 ' + str(imgSize) + ' ' + str(imgSize)
        # creating a new attribute
        _name = svgFile.getElementsByTagName("g")[1]
        _name.setAttribute("transform", "scale(" + str(scaleFac) + ")")

        with open(desDir + svgFileName.split('/')[-2] + '/' + svgFileName.split('/')[-1], "w") as f:
            f.write(svgFile.toxml())


def removeAStyle(svgFiles, desDir, attrRem, valRem):
    """
    it removes all the paths containg the attribute (attrRem) with value (valRem)
    """
    # svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    for svgFileName in svgFiles:
        svgFile = minidom.parse(svgFileName)
        pathList = svgFile.getElementsByTagName("path")

        for pathIdx, pathEle in enumerate(pathList):
            if pathEle.attributes[attrRem].value == valRem:
                parent = pathEle.parentNode
                parent.removeChild(pathEle)
                # else:
                #     pathList[pathIdx].removeAttribute("style")

        with open(desDir + '/' + svgFileName.split('/')[-1], "w") as f:
            f.write(svgFile.toxml())


def svg1M1Path(svgFiles, desDir):
    """
    creates one path for each M.
    """
    # svgFiles = sorted(glob.glob(srcDir + "*.svg"))

    for svgFileName in svgFiles:
        svgFile = minidom.parse(svgFileName)
        pathList = svgFile.getElementsByTagName("path")

        for pathIdx, pathEle in enumerate(pathList):

            if len(pathEle.attributes["d"].value.split("M")) > 2:
                pathStyle = pathEle.attributes["style"].value

                parent = pathEle.parentNode
                parent.removeChild(pathEle)

                for pathVal in pathEle.attributes["d"].value.split("M")[1:]:
                    newPath = svgFile.createElement("path")
                    newPath.setAttribute("d", u"M" + str(pathVal))
                    newPath.setAttribute("style", pathStyle)
                    parent.appendChild(newPath)

        with open(desDir + '/' + svgFileName.split('/')[-1], "w") as f:
            f.write(svgFile.toxml())


def strokeImageSequenceCreation(dataDic, desDir):
    [strokesSrc2Des((os.path.dirname(dataDic.get(key)[0]) + "/"), (desDir + key + "/")) for key in dataDic.keys()]


def separateStrokeImageSequenceCreation(dataDic, desDir):
    [separateStrokesSrc2Des((os.path.dirname(dataDic.get(key)[0]) + "/"), (desDir + key + "/")) for key in
     dataDic.keys()]


def svgList2pngDir(svgList, pngDir):
    [cairosvg.svg2png(url=fileName, write_to=pngDir + os.path.basename(fileName).split('.')[0] + '.png') for fileName in
     svgList]


def svgDic2pngDir(svgDic, pngDir):
    [svgList2pngDir(svgDic.get(key), pngDir + key + "/") for key in svgDic.keys()]


def svgList2pngResizeDir(svgList, pngDir, pngSize):
    print(pngDir)
    [call(["convert", svgFileName, "-resize", pngSize, pngDir + os.path.basename(svgFileName).split('.')[0] + '.png'])
     for svgFileName in svgList]


def svgDic2pngResizeDir(svgDic, pngDir, pngSize):
    [svgList2pngResizeDir(svgDic.get(key), pngDir + key + "/", pngSize) for key in svgDic.keys()]


# Temporart tools - start

def imagePreProcessing(inputImage):
    # convert to grey scale and type uint8
    inputImage = img_as_ubyte(color.rgb2grey(inputImage))
    # dilatrion of radius 5
    struct = ndimage.generate_binary_structure(2, 2)

    # return ndimage.binary_dilation(inputImage, structure=struct, iterations=5).astype(inputImage.dtype)
    return ndimage.grey_dilation(inputImage, structure=struct, iterations=5).astype(inputImage.dtype)


def main():
    ######################## Data initalization ########################
    # Variables defined here: dataDir, dataList, dataDic

    dataDir = '/import/vision-ephemeral/urm30/TUBerlin-svg-250-80/'
    dataList = folder2files(dataDir, ".png")
    dataList = pngList2svgList(dataList, "TUBerlin-png-160", "TUBerlin-svg-260-80")
    dataDic = list2dic(dataList)

    labelNumEncoder = preprocessing.LabelEncoder()
    labelNumEncoder.fit(dataDic.keys())

    dataDic = label2num(dataDic, labelNumEncoder)
    dataDic = num2label(dataDic, labelNumEncoder)

    dataDic = dicRandomNValues(dataDic, 56)

    dataDir = "../data/TUBerlin-svg-160-56/"
    dbClassFolderCreation(dataDic, dataDir)

    dic2folder(dataDic, dataDir)

    # Read dataDic from this new folder containg 56 images for each of 160 classes.
    # convert svg files to png and save them

    # convert svg files to svg stroke files
    dataDir = "../data/TUBerlin-svg-160-56-strokes/"
    dataStrokeDic = strokeImageSequenceCreation(dataDic, dataDir)

    dataDir = "../data/TUBerlin-svg-160-56/"
    dataList = folder2files(dataDir, "svg")
    dataDic = list2dic(dataList)
    pngDir = "../data/TUBerlin-png-160-56/"
    svgDic2pngDir(dataDic, pngDir)

    dataDir = "../data/TUBerlin-svg-160-56-strokes/"
    dataList = folder2files(dataDir, "svg")
    dataDic = list2dic(dataList)
    pngDir = "../data/TUBerlin-png-160-56-strokes/"
    svgDic2pngDir(dataDic, pngDir)

    dataDir = "../data/TUBerlin-svg-160-56-strokes/"
    dataList = folder2files(dataDir, "svg")
    dataDic = list2dic(dataList)
    pngDir = "../data/TUBerlin-png-160-56-strokes/"
    svgDic2pngResizeDir(dataDic, pngDir, "250x250")

    [strokesSrc2Des((os.path.dirname(dataDic.get(key)[0]) + "/"), (desDir + key + "/")) for key in dataDic.keys()]

    key = "airplane"
    separateStrokesSrc2Des((os.path.dirname(dataDic.get(key)[0]) + "/"), (desDir + key + "/"))

    separateStrokeImageSequenceCreation(dataDic, dataDir)

    # creating 54 training images, and the rest as testing set.
    training_set = []
    testing_set = []
    for key, val in dataDic.items():
        first_ele = int(sorted(val)[0].split("/")[-1][0:5])
        for img in sorted(val):
            if int(img.split("/")[-1][0:5]) < first_ele + 55:
                training_set.append(img)
            else:
                testing_set.append(img)

    labels = sorted(dataDic.keys())
    training_set = sorted(training_set)
    # labels = range(250)

    for idx, ele in enumerate(training_set):
        with open('training.txt', 'a') as f:
            f.write(training_set[idx] + ' ' + str(labels.index(ele.split('/')[-2])) + "\n")

    # saveDic(dataDic, outputMailfolder)
    # - it should first create the folder name with class name and then save files.
    # - it should save the files with two counters...first with the file number and secondo with zeros.

    # read again the folder....creating the dictionaries of classes with relative images.
    # now use this dictionary to save stroke images.

    # here I have to generate strokes for each image, and save them, along with the class folders.
    # save the strokes images with two counters.....one for the main image...other for its strokes

    # create dictionary of dictionaries to handel data

    trainDic, validDic, testDic = dataSplit(dataDic, 32, 10, 14)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='./data',
                        help='Directory for storing data')
    FLAGS = parser.parse_args()
    tf.app.run()
