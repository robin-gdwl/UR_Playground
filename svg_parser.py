import svgpathtools
import numpy as np
import matplotlib.pyplot as plt

class SVGParse:

    def __init__(self, filepath, tolerance):
        self.path = filepath
        self.tol = tolerance



    # make this a staticmethod ??
    def convert_to_coords(self):

        ob_list = []
        paths, attributes = svgpathtools.svg2paths(self.path)

        #print("paths: ", paths)
        #print(attributes)
        # print(file_att)


        i = 0
        for p in paths:
            coords = []

            p_attributes = attributes[i]

            length = p.length(error=self.tol)
            #print("length:", length)
            amount = length / self.tol
            #print(amount)
            div = 1 / amount
            print(p_attributes)

            if "opacity" in p_attributes.values() :
                print("opacity detected")
            else:
                print("no opacity")

            stroke = p_attributes["stroke"]
            if "url" in stroke:
                print("gradient in p")
                gradient_id = stroke[stroke.find("(") + 1:stroke.find(")")]
                gradient_id = gradient_id.strip("#")
                print(gradient_id)
                gradient = get_gradient(gradient_id)

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

        return ob_list

        #return list


    def get_color(self, param, colour):
        pass

    def get_opacity(self, param, opacity):
        pass

    def get_gradient(self, url):
        xml_file = minidom.parse(filepath)
        gradients = xml_file.getElementsByTagName("linearGradient")
        print(gradients)

testfile = "gradient05.svg"
coords = SVGParse(testfile,20).convert_to_coords()

print(coords)
x = []
y = []

for path in coords:
    for subpath in path:
        x.append(subpath[0])
        y.append(subpath[1])

plt.scatter(x, y)
plt.show()
