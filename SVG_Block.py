from Blocks import Block
from svgpathtools import *
from svg_to_coord import svg_to_np
import ezdxf
import svg.path

def print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)

class svgBlock(Block):

    def __init__(self):

        self.filepath = "path"
        self.scale = 1
        self.origin = []
        self.tolerance = 0.1

        self.paths = []

    def load(self):
        # loads an svg file, puts the points into self.coordinates

        ob_list = []
        paths, attributes= svg2paths(self.filepath)

        print("paths: ",paths)
        print(attributes)
        #print(file_att)


        i = 0
        for p in paths:
            coords = []
            print(p)
            mid = p.point(0.5)
            print(mid)
            length = p.length(error= self.tolerance)
            print("length:", length)
            amount = length / self.tolerance
            print(amount)
            div = 1 / amount

            j = 0
            while j <= 1:
                point = p.point(j)
                coords.append(point)
                print("point parsed")
                print(point)
                print(j)
                j += div

            ob_list.append(coords)
            print("ob_list: ", ob_list)
            print("i: ",i)

            i += 1




        np_paths = svg_to_np(self.filepath)

        print("np:  ", np_paths)

        return paths

    def internalise(self):
        # IDEA: internalise the file somehow to make it independant from the filepath when loading the program
        pass


testblock = svgBlock()
testblock.filepath = "Test05.svg"



paths = testblock.load()

#parse = bezier2polynomial(paths[2])
#print(poly)




