import svgpathtools
import logging
from xml.dom import minidom


class SVGParse:

    """gets an svg file
    parses all paths
    creates gradient objects
    creates a movement-object for each path
        - Lines become
    returns list of movement objects
    """

    def __init__(self, filepath, tolerance, scale):
        self.scale = scale
        self.path = filepath
        self.tol = tolerance
        self.movements = []
        self.gradients = self.get_gradients()

    def convert_to_movements(self):
        logging.debug("starting conversion svg to movements")
        paths, attributes = svgpathtools.svg2paths(self.path)
        print(paths)
        logging.debug("Paths in SVG: " + str(paths))

        for p_index, p in enumerate(paths):
            #print("----"*45)
            #print(p_index, "th path: ", p)
            logging.debug("length: " + str(p.length()))

            if p.length() == 0:
                logging.debug("0-length path element found, no movement added")
                continue

            p_attributes = attributes[p_index]  # current path's attributes

            motion_object = self.interpolate_path(p,p_attributes)

            self.movements.append(motion_object)

        return self.movements

    def interpolate_path(self,path,attributes):
        print("interpolate path ",path )
        logging.debug("interpolating path: ",path )
        movement = MoveColOpa() # each path has one movement object
        length = path.length(error = self.tol)
        # TODO: if tolerance is very high amount = 0 and div throws an error
        amount = int(length / self.tol * self.scale)
        if amount == 0:
            amount = 2
        div = 1 / amount

        movement.coordinates = self.get_pts_on_path(path,div)
        movement.colors = self.color_on_path(path, attributes, div, amount)
        movement.opacities = self.opacities_on_path(path, attributes, div, amount)

        return movement

    def get_pts_on_path(self,path,stepsize):
        coords = []
        j = 0
        while j <= 1:
            print(j)
            point = path.point(j)
            x =  - point.real
            y = point.imag

            xy_coord = [x, y]

            coords.append(xy_coord)
            j += stepsize
        return coords

    def color_on_path(self,path, attributes, stepsize, amount):
        colors = []
        coltype, value = self.get_color(attributes)

        if coltype == "stroke":
            value = value.lstrip("#")
            color = tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # converts the Hex color value to rgb
            # TODO: find out why you need to add 1 to the amount
            colors = [color] * (amount+1)

        elif coltype == "gradient":
            gradient_id = value
            for g in self.gradients:  # find which gradient is used in the stroke
                if g.id == gradient_id:
                    gradient = g
                    break
            j = 0
            while j <= 1:
                color = self.color_at_param(gradient, j)
                colors.append(color)
                j += stepsize

        else:  # what to do if there is neither a stroke color nor a gradient
            default_color = [0,0,0]
            colors = [default_color for x in range(amount)]
            #colors = [default_color] * amount
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
            p_stroke = ""

        # check if there is a gradient
        if "url" in p_stroke:
            grad_bool = True
            #print("gradient in p")
            gradient_id = p_stroke[p_stroke.find("(") + 1: p_stroke.find(")")]
            gradient_id = gradient_id.strip("#")

        else:
            grad_bool = False
            #print("no gradient")

        if grad_bool:
            return "gradient",gradient_id
        elif p_stroke_bool:
            return "stroke",p_stroke
        else:
            return "nocolor",0
        # movement.stroke = p_stroke

    def color_at_param(self,gradient, param):
        print("---"*25)
        #print("looking for color at param ")
        color = []
        stops = gradient.stop_offsets
        print("stops:  ", stops)

        clrs = gradient.colors
        for idx, offset in enumerate(stops) :
            #print("parsing all offsets.... current offset: ", offset, "at index:  ", idx, "of: ", len(stops)-1)
            #print("offset: ", offset)
            #print("param: ", param)
            #print(len(gradient.opacities))
            #print(len(clrs))
            #print(len(stops))

            if idx < (len(stops) - 1):
                #print("next offset: ", stops[idx + 1])
                pass

            # TODO:add case if param is smaller than first stop
            if param == offset :
                #print("param = offset")
                return clrs[idx]
            elif param >= offset and param >= stops[idx + 1]:
                continue

            elif param >= offset and param <= stops[idx + 1]:
                para_1 = offset
                para_2 = stops[idx +1]
                position = (param - para_1) / (para_2 - para_1)
                #print("pos: ", position)

                col_1 = clrs[idx]
                col_2 = clrs[idx + 1]

                for val, rgb_val in enumerate(col_1):
                    startval = rgb_val
                    endval = col_2[val]
                    interm_val = ((endval - startval) * position) + startval
                    #print(interm_val)
                    color.append(interm_val)
                #print("param", param)
                #print("colour at param: ", color)
                return color

            elif param == stops[idx + 1]:
                #print("param = next offset")
                return clrs[idx + 1]

    def opacities_on_path(self, path, attributes, stepsize, amount):

        overall_opa = self.get_path_opacity(path, attributes)
        opacities =[]
        coltype, value = self.get_color(attributes)  # simply checks again  if the path has a gradient
        # TODO: avoid checking gradient twice

        if coltype == "gradient":
            gradient_id = value
            for g in self.gradients:  # find which gradient is used in the stroke
                if g.id == gradient_id:
                    gradient = g
                    break
            j = 0

            while j <= 1:
                opacity = self.opacity_at_param(gradient, j)

                opacities.append(opacity)
                j += stepsize
        else:
            print("applying opacities this many times:  ", amount)
            # TODO: find out why you need to add 1 to the amount
            opacities = [1] * (amount+1)

        adjusted_opa = [i * overall_opa for i in opacities]
        #print(adjusted_opa)
        return adjusted_opa

    def get_path_opacity(self,path,attributes): # get the overall opacity of a path
        if "opacity" in attributes.keys():
            opacity = float(attributes["opacity"])
            print("opacity value present: ", opacity)
        else:
            print("no opacity value for path")
            opacity = 1
        return opacity

    def opacity_at_param(self,gradient, param):
        #print("---" * 19)
        #print("looking for opacity at param ")

        stops = gradient.stop_offsets
        opas = gradient.opacities

        for idx, offset in enumerate(stops):
            #print("parsing all offsets.... current offset: ", offset, "at index:  ", idx, "of: ", len(stops) - 1)
            #print("offset: ", offset)
            #print("param: ", param)

            if idx < (len(stops) - 1):
                #print("next offset: ", stops[idx + 1])
                pass
            if param == offset:
                #print("param = offset")
                return opas[idx]
            elif param >= offset and param >= stops[idx + 1]:
                continue
            elif offset <= param <= stops[idx + 1]:
                para_1 = offset
                para_2 = stops[idx + 1]
                position = (param - para_1) / (para_2 - para_1)
                #print("pos: ", position)

                opa_1 = opas[idx] # this is one float
                opa_2 = opas[idx + 1]
                #print(type(opa_1))
                #print(type(opa_2))

                opacity = ((opa_2 - opa_1) * position) + opa_1

                #print(type(opacity))
               # print("current param opacity:  ", opacity)

                return opacity

            elif param == stops[idx + 1]:
                #print("param = next offset")
                return opas[idx + 1]

    def get_gradients(self):
        # TODO: add possibility for radial gradients
        xml_file = minidom.parse(self.path)
        lin_gradients = xml_file.getElementsByTagName("linearGradient")
        rad_gradients = xml_file.getElementsByTagName("radialGradient")

        gradient_instances = []

        if len(lin_gradients) > 0:
            for g in lin_gradients:
                #print("g:", g)
                id = g.attributes["id"].value
                grad = Gradient(id)

                stops = g.getElementsByTagName("stop")
                for i, stop in enumerate(stops):
                    offset = stop.attributes["offset"].value
                    offset = float(offset)

                    style = stop.attributes["style"].value

                    col_desc = "stop-color:"
                    if style.find(col_desc) != -1:
                        color_ind = style.index(col_desc) + len(col_desc)
                        color_val = style[color_ind: color_ind + 7]
                        color_val= color_val.lstrip("#")
                    else:  # not sure if this is necessary, as a gradient stop should always have color
                        color_val = 000000

                    color_rgb = tuple(int(color_val[i:i + 2], 16) for i in (0, 2, 4))

                    grad.stop_offsets.append((offset))
                    grad.colors.append(color_rgb)
                    print("color  ", color_rgb)


                    opa_desc = "stop-opacity:"
                    if style.find(opa_desc) != -1:
                        opa_ind = style.index(opa_desc) + len(opa_desc)
                        opa_val = style[opa_ind: opa_ind + 7]
                        opa_val = float(opa_val)
                    else:
                        opa_val = 1
                    grad.opacities.append(opa_val)
                    print("opacity  ",opa_val)

                    if i == 0 and offset != 0:
                        print("first offset not at 0")
                        grad.stop_offsets.append(0)
                        grad.colors.append(color_rgb)
                        grad.opacities.append(opa_val)

                    if i == (len(stops)-1) and offset < 1:
                        print("last stop offset is not at 100% ")

                        grad.stop_offsets.append(1)
                        grad.opacities.append(opa_val)
                        grad.colors.append(color_rgb)

                print(grad.check_lengths())
                print("s: ", stops)


                #stop = g.childNodes
                print(g.attributes)

                gradient_instances.append(grad)
                print(gradient_instances)

        if len(rad_gradients) > 0:
            """Radial gradients are parsed similarly to linear ones, with the difference that they mirrored once:
            If a radial gradient has 3 stops they will be saved in this manner: stop3,stop2,stop1,stop1,stop2,stop3
            """
            # make this a nice function so that it does not need to be repeated form above.
            for g in rad_gradients:
                print("g:", g)
                id = g.attributes["id"].value
                grad = Gradient(id)

                stops = g.getElementsByTagName("stop")
                for i, stop in enumerate(stops):
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
                        opa_val = float(opa_val)
                    else:
                        opa_val = 1
                    grad.opacities.append(opa_val)
                    print("opacity  ",opa_val)

                    if i == (len(stops)-1) and offset < 1:
                        print("last stop offset is not at 100% ")

                        grad.stop_offsets.append(1)
                        grad.opacities.append(opa_val)
                        grad.colors.append(color_rgb)

                """the following is horribly unpythonic.
                all of this should be done in the functions above."""

                mir_stops = grad.stop_offsets
                mir_opac = grad.opacities
                mir_colors = grad.colors

                mir_stops.reverse()
                mir_opac.reverse()
                mir_colors.reverse()

                for i, stop_off in enumerate(mir_stops):
                    mir_stops[i] = (1 - stop_off) / 2

                mir_stops_reverse = mir_stops[::-1]
                for i, stop_off in enumerate(mir_stops_reverse):
                    mir_stops_reverse[i] = 1 - stop_off

                mir_stops.extend(mir_stops_reverse)
                mir_opac.extend(mir_opac[::-1])
                mir_colors.extend(mir_colors[::-1])

                grad.stop_offsets = mir_stops
                grad.opacities = mir_opac
                grad.colors = mir_colors

                print(grad.check_lengths())
                print("s: ", stops)

                #print(g.attributes)

                gradient_instances.append(grad)
                #print(gradient_instances)
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

"""testfile = "gradient07.svg"
parsed_file = SVGParse(testfile,20)
movements = parsed_file.convert_to_movements()

for movement in movements:
    print("coordinates  ", movement.coordinates)
    print("colors  ", movement.colors)
    print("opacities  ", movement.opacities)
    print("stroke  ", movement.strokewidth)

    print(movement.check_lengths())

print(movements)
x = []
y = []
"""

'''for path in coords:
    for subpath in path:
        x.append(subpath[0])
        y.append(subpath[1])

plt.scatter(x, y)
plt.show()
'''