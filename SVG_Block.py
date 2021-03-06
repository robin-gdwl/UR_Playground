from GlobalFunc import *
from Blocks import Block
from math import pi
from svgpathtools import *
import svg_parser
import time
import copy

"""def print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)"""


class svgBlock(Block):
    def __init__(self):
        super(svgBlock, self).__init__()

        self.filepath = ""
        self.scale = 1
        #self.origin = []  # (x,y,z,rx,ry,rz) csys
        self.tolerance = 5
        self.travel_z = 0
        self.depth = 0
        self.max_rotation = 1/8 * 360

        self.path_movements = []
        self.coordinates = []  # these will be the (x,y,z,rx,ry,rz) coordinates after all trnasformations from opacity and colour are applied
        self.coordinates_travel = []  # same as above but with the travel moves necessary to keep the same indices as the path_movements

        self.use_colour = True
        self.color_effect = 1

        self.use_opacity = True
        self.opacity_effect = 1

    def load(self):

        # loads an svg file, puts the movements into self.path_movements
        # translates color and opacity values into the corresponding transformations
        start_time = time.time()
        parsed_file = svg_parser.SVGParse(self.filepath, self.tolerance, self.scale)
        movements = parsed_file.convert_to_movements()

        self.path_movements = movements

        end_time = time.time() - start_time

        print(" loaded svg in ", end_time)
        #print(self.path_movements)
        #print(vars(self.path_movements[0])) #FIXME some files throw and error here

        self.add_values()
        self.scale_xy()
        self.apply_depth()
        self.apply_rotation()

        self.add_travel()

        print("coordinates_travel in SVG_BLOCK load()",self.coordinates_travel)

    def update(self):
        """used to update the block, mainly remakes self.coordinates_travel"""
        self.add_values()

        self.scale_xy()
        self.apply_depth()
        self.apply_rotation()
        self.add_travel()

    def add_values(self):
        """this function puts the coordinates of the path_movements into self.coordinates
            adds 4 zeros (z-value,3x rotation value)
            this should only be done once"""
        self.coordinates = []
        for m_idx, movement in enumerate(self.path_movements):

            full_coords = []
            for c_idx, coordinates in enumerate(movement.coordinates):
                x = coordinates[0]
                y = coordinates[1]
                full_coords.append([x,y,0,0,0,0])

            self.coordinates.append(full_coords)

    def scale_xy(self):
        for m_idx, movement in enumerate(self.path_movements):
            for c_idx, coordinates in enumerate(movement.coordinates):
                #print(type(self.scale))
                new_x = coordinates[0] * self.scale
                new_y = coordinates[1] * self.scale

                self.coordinates[m_idx][c_idx][0] = new_x
                self.coordinates[m_idx][c_idx][1] = new_y
        print(self.coordinates)

    def apply_rotation(self):

        if self.use_colour == False:
            rotation = [0,0,0]
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    #self.coordinates[m_idx][c_idx][3,4,5] = rotation[0,1,2]
                    insert_pos = [3,4,5]
                    for x, y in zip(insert_pos, rotation):
                        self.coordinates[m_idx][c_idx][x] = y
        else:
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    rotation = movement.colors[c_idx]
                    #rot_x = rotation[0] /255
                    #rot_y = rotation[1] /255
                    #rot_z = rotation[2] /255
                    #print(rot_x,rot_y,rot_z)

                    insert_pos = [3, 4, 5]
                    for x, rot in zip(insert_pos, rotation):
                        rot = (rot - 127.5) / 127.5
                        rot = rot * self.color_effect * self.max_rotation
                        rot = DegToRad(rot)

                        self.coordinates[m_idx][c_idx][x] = rot

    def apply_depth(self):
        if self.use_opacity == False:
            depth = -self.depth
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    self.coordinates[m_idx][c_idx][2] = depth

        else:
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    #print(vars(movement))
                    #depth = movement.opacities[c_idx]
                    #print("depth found, applying")
                    #print(depth)
                    depth = -self.depth * movement.opacities[c_idx] * self.opacity_effect

                    self.coordinates[m_idx][c_idx][2] = depth

    def add_travel(self):

        if len(self.coordinates) > 0 :
            #print("coordintates found adding travel")
            self.coordinates_travel = copy.copy(self.coordinates)

            for motion in self.coordinates_travel:
                start_coords = copy.copy(motion[0])
                end_coords = copy.copy(motion[-1])

                start_coords[2] += self.travel_z - start_coords[2]
                end_coords[2] += self.travel_z - end_coords[2]

                motion.insert(0, start_coords)
                motion.append(end_coords)
                # print(motion)
            #print(self.coordinates_travel)
        else:
            print("no coordinates yet, load a file first")

    def change_travel(self):
        pass





