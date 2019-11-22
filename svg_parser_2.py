import svgpathtools
import numpy as np
import matplotlib.pyplot as plt
from xml.dom import minidom



class SVGParse:
    '''
    gets an svg file
    parses all paths
    creates gradient objects
    creates a movement-object for each path
        - Lines become
    returns list of movement objects
    '''

    def __init__(self, filepath, tolerance):
        self.path = filepath
        self.tol = tolerance
        self.gradients = self.get_gradients()
        self.movements = []

    def convert_to_movements(self):

        paths, attributes = svgpathtools.svg2paths(self.path)

        for p_index, p in enumerate(paths):

            p_attributes = attributes[p_index]  # current path's attributes

            motion_object = self.interpolate_path(p,p_attributes)

            self.movements.append(motion_object)



    def interpolate_path(self,path,attributes):

        movement = MoveColOpa() # each path has one movement object
        length = path.length(error=self.tol)
        amount = length / self.tol
        div = 1 / amount

        movement.coordinates = self.get_pts_on_path(path,div)

        movement.colors = self.color_on_path(path, attributes, div, amount)

        # TODO: implement opacities on path
        movement.opacities = self.opacities_on_path(path, attributes, div, amount)



    def get_pts_on_path(self,path,stepsize):


        coords = []
        j = 0
        while j <= 1:
            point = path.point(j)

            x = point.real
            y = point.imag

            xy_coord = [x, y]

            coords.append(xy_coord)
            # print("point parsed")
            # print(point)
            # print(j)
            j += stepsize

        return coords

    def color_on_path(self,path, attributes, stepsize, amount):


        colors = []
        coltype, value = self.get_color(attributes)

        if coltype == "stroke":
            color = tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # converts the Hex color value to rgb

            colors = [color] * amount

        elif coltype == "gradient":
            gradient_id = value

            for g in self.gradients:  # find which gradient is used in the stroke
                if g.value == gradient_id:
                    gradient = g
                    break
            j = 0
            while j <= 1:
                color = self.color_at_param(gradient, j)

                colors.append(color)
                j += stepsize

        else:  # what to do if there is neither a stroke color nor a gradient
            colors = [[0,0,0]] * amount

        return colors


    def get_color(self,attributes):
        # finds out what defines the color of the path, returns the type of color (stroke-color or gradient or none)

        # TODO: make this more pythonic

        # check if a stroke color or gradient is defined
        if "stroke" in attributes.keys():
            p_stroke_bool = True
            p_stroke = attributes["stroke"]

        else:
            p_stroke_bool = False
            p_stroke = None

        # check if there is a gradient
        if "url" in p_stroke:
            grad_bool = True
            print("gradient in p")
            gradient_id = p_stroke[p_stroke.find("(") + 1: p_stroke.find(")")]
            gradient_id = gradient_id.strip("#")

        else:
            grad_bool = False
            print("no gradient")

        if grad_bool:
            return "gradient",gradient_id
        elif p_stroke_bool:
            return "stroke",p_stroke
        else:
            return "nocolor",0




        # movement.stroke = p_stroke



    def color_at_param(self,gradient, param):

        color = []
        # here I need a function which finds between which indexes of the stop-offset list the param lies
        # 0, 1, 2, 3.5, 6.8, 20
        # 2.3
        stops = gradient.stop_offsets
        clrs = gradient.colors
        for idx, offset in enumerate(stops) :
            print("offset: ", offset)
            print("param: ", param)
            if idx < (len(stops) - 1):
                print("next offset: ", stops[idx + 1])

            if param == offset :
                print("param = offset")
                return clrs[idx]
            elif param >= offset and param >= stops[idx + 1]:
                continue
            elif param >= offset and param <= stops[idx + 1]:
                para_1 = offset
                para_2 = stops[idx +1]
                position = (param - para_1) / (para_2 - para_1)
                print("pos: ", position)

                col_1 = clrs[idx]
                col_2 = clrs[idx + 1]

                for val, rgb_val in enumerate(col_1):
                    startval = rgb_val
                    endval = col_2[val]
                    interm_val = ((endval - startval) * position) + startval
                    print(interm_val)
                    color.append(interm_val)
                print("param", param)
                print("colour at param: ", color)
                return color

            elif param == stops[idx + 1]:
                print("param = next offset")
                return clrs[idx + 1]

    def get_gradients(self):
        xml_file = minidom.parse(self.path)
        gradients = xml_file.getElementsByTagName("linearGradient")

        gradient_instances = []

        for g in gradients:
            print("g:", g)
            id = g.attributes["id"].value
            grad = Gradient(id)

            stops = g.getElementsByTagName("stop")
            for stop in stops:
                offset = stop.attributes["offset"].value
                offset = float(offset)
                grad.stop_offsets.append((offset))

                style = stop.attributes["style"].value

                col_desc = "stop-color:"
                if style.find(col_desc) != -1:
                    color_ind = style.index(col_desc) + len(col_desc)
                    color_val = style[color_ind: color_ind + 7]
                    color_val= color_val.lstrip("#")
                else:  # not sure if this is necessary, as a gradient stop should always have color
                    color_val = 000000

                color_rgb = tuple(int(color_val[i:i + 2], 16) for i in (0, 2, 4))
                grad.colors.append(color_rgb)
                print("color  ", color_rgb)


                opa_desc = "stop-opacity:"
                if style.find(opa_desc) != -1:
                    opa_ind = style.index(opa_desc) + len(opa_desc)
                    opa_val = style[opa_ind: opa_ind + 7]
                else:
                    opa_val = 1
                grad.opacities.append(opa_val)
                print("opacity  ",opa_val)

            print(grad.check_lengths())
            print("s: ", stops)


            #stop = g.childNodes
            print(g.attributes)

            gradient_instances.append(grad)
            print(gradient_instances)


        return gradient_instances








class MoveColOpa:

    """Movement objects have:
    List of coordinate
    List of corresponding colour for each coordinate (R,G,B)
    List of corresponding opacities  """

    def __init__(self):
        self.coordinates = []
        self.colors = []
        self.opacities = []
        self.strokewidth = None

    def check_lengths(self):
        a = len(self.coordinates)
        b = len(self.colors)
        c = len(self.opacities)

        if a == b and b == c:
            return True
        else:
            print("different lengths detected")
            print("coordinates: ", len(self.coordinates))
            print("colors: ", len(self.colors))
            print("opacities: ", len(self.opacities))
            return False


class Gradient:

    def __init__(self, id):
        self.id = id
        self.stop_offsets = []
        self.colors = []
        self.opacities = []

    def check_lengths(self):
        a = len(self.stop_offsets)
        b = len(self.colors)
        c = len(self.opacities)

        if a ==b and b == c:
            return True
        else:
            return False

