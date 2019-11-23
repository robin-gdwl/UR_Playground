from Blocks import Block
from svgpathtools import *
import svg_parser
import time


def print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)

class svgBlock(Block):

    def __init__(self):

        self.filepath = "path"
        self.scale = 0.5
        self.origin = []  # (x,y,z,rx,ry,rz) csys
        self.tolerance = 1
        self.travel_z = 0.05
        self.depth = 0.05

        self.path_movements = []
        self.coordinates = [] # these will be the (x,y,z,rx,ry,rz) coordinates after all trnasformations from opacity and colour are applied

        self.use_colour = True
        self.color_effect = 1

        self.use_opacity = True
        self.opacity_effect = 1

    def load(self):
        # loads an svg file, puts the movements into self.path_movements
        # translates color and opacity values into the corresponding transformations

        start_time = time.time()
        parsed_file = svg_parser.SVGParse(self.filepath, 20)
        movements = parsed_file.convert_to_movements()

        self.path_movements = movements

        end_time = time.time() - start_time

        print(" loaded in ", end_time)
        print(self.path_movements)
        print(vars(self.path_movements[0]))

        self.add_values()

        self.scale_xy()
        self.apply_depth()
        self.apply_rotation()

        print("final coords:  ",self.coordinates)

        print(len(self.coordinates))
        x= 0
        for path in self.coordinates:
            print(len(path))
            x+= len(path)
        print(x)
        #return paths


    def add_values(self):
        """this function puts the coordinates of the path_movements into self.coordinates
            adds 4 zeros (z-value,3x rotation value)
            this should only be done once"""
        for m_idx, movement in enumerate(self.path_movements):
            full_coords = []
            for c_idx, coordinates in enumerate(movement.coordinates):
                x = coordinates[0]
                y = coordinates[1]
                full_coords.append([x,y,0,0,0,0])

            self.coordinates.append(full_coords)

    def scale_xy(self):
        for m_idx, movement in enumerate(self.path_movements):
            #move_coords = []
            for c_idx, coordinates in enumerate(movement.coordinates):
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
                    # TODO: convert from RGB to rad-rotation
                    insert_pos = [3, 4, 5]
                    for x, y in zip(insert_pos, rotation):
                        self.coordinates[m_idx][c_idx][x] = y


    def apply_depth(self):
        if self.use_opacity == False:
            depth = self.depth
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    self.coordinates[m_idx][c_idx][2] = depth

        else:
            for m_idx, movement in enumerate(self.path_movements):
                for c_idx, coordinates in enumerate(movement.coordinates):
                    depth = movement.opacities[c_idx]
                    # TODO: convert from opacity value to depth value depending on self.depth
                    self.coordinates[m_idx][c_idx][2] = depth


    def add_travel(self):
        #TODO: how to add travel coordinates without destroying the indices of the self.coordinates in comparison to the movement object?

        pass

    def change_travel(self):
        pass



    """def internalise(self):
        # IDEA: internalise the file somehow to make it independant from the filepath when loading the program
        pass"""


testblock = svgBlock()
testblock.filepath = "gradient11.svg"

paths = testblock.load()

#parse = bezier2polynomial(paths[2])
#print(poly)




