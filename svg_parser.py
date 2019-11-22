import svgpathtools
import numpy as np
import matplotlib.pyplot as plt
from xml.dom import minidom

class Movement:

    """Movement objects have:
    List of coordinate
    List of corresponding colour for each coordinate (R,G,B)
    List of corresponding opacities  """


    def __init__(self):
        self.coordinates = []
        self.colors = []
        self.opacities = []

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

    def color_at_param(self, param):
        color = []
        # here I need a function which finds between which indexes of the stop-offset list the param lies
        # 0, 1, 2, 3.5, 6.8, 20
        # 2.3
        stops = self.stop_offsets
        clrs = self.colors
        for idx, offset in enumerate(stops) :
            print("offset: ", offset)
            print("param: ", param)
            print("next offset: ", stops[idx + 1])

            if param == offset :
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
                return clrs[idx + 1]








        return color

    def opacity_at_param(self, param):
        opacity = None
        return opacity

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


    # make this a staticmethod ??
    def convert_to_coords(self):

        ob_list = []
        paths, attributes = svgpathtools.svg2paths(self.path)

        i = 0
        print("paths:", paths)
        for p in paths:

            coords = []

            p_attributes = attributes[i]
            print(p_attributes)

            length = p.length(error=self.tol)
            #print("length:", length)
            amount = length / self.tol
            #print(amount)
            div = 1 / amount
            print(p_attributes)

            # TODO: check if these two if statements need .value or something
            if "opacity" in p_attributes.values() :
                print("opacity detected")
                opacity = p_attributes["opacity"]
            else:
                print("no opacity")

            if "stroke" in p_attributes.keys() :
                stroke = p_attributes["stroke"]
            else:
                stroke = ""

            print("stroke: ", stroke)

            if "url" in stroke:
                print("gradient in p")
                gradient_id = stroke[stroke.find("(") + 1:stroke.find(")")]
                gradient_id = gradient_id.strip("#")
                print("grad id:  ",gradient_id)
                gradient = self.get_gradients()

                rand_params = [0,0.1,0.5,0.7,0.8,0.99]
                gra = gradient[0]
                for para in rand_params:
                    gra.color_at_param(para)
                # TODO: color at param here

            else:
                print("no gradient")

            j = 0
            while j <= 1:
                point = p.point(j)

                x = point.real
                y = point.imag

                xy_coord = [x, y]

                coords.append(xy_coord)
                # print("point parsed")
                # print(point)
                # print(j)
                j += div


            ob_list.append(coords)
            #print("ob_list: ", ob_list)
            #print("i: ", i)


            i += 1

        # np_paths = svg_to_np(self.filepath)

        # print("np:  ", np_paths)

        # TODO: nicely package the different things you need from a gradient:
        # id, params, colours, opacities

        return ob_list

        #return list
        '''
        list includes:
        [[(x,y),param,colour,opacity]]
        '''

    def get_color(self, param, colour):
        pass

    def get_opacity(self, param, opacity):
        pass

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


testfile = "gradient08.svg"
coords = SVGParse(testfile,20)
coords = coords.convert_to_coords()

print(coords)
x = []
y = []

for path in coords:
    for subpath in path:
        x.append(subpath[0])
        y.append(subpath[1])

plt.scatter(x, y)
plt.show()
