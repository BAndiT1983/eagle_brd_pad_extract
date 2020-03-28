import drawSvg as draw
from PIL import Image

from data_structs import Pad, Element
from typing import List


def get_image_size(image_file_name):
    image = Image.open(image_file_name)
    return image.width, image.height


def create_svg(input_image_file, output_image_name, element_list):

    width, height = get_image_size(input_image_file)

    # Fixed size for PCB image
    d = draw.Drawing(width, height, origin='center')

    d.append(draw.Image(-(width / 2), -(height / 2),
                        width, height, input_image_file))
                        
    factor = 47.2
    for item in element_list.values():
        for pad in item.pads.values():

            pad_x = float(pad.x) * factor
            pad_y = float(pad.y) * factor

            pad_width = float(pad.width) * factor
            pad_height = float(pad.height) * factor

            #rotation = ""
            # if(int(pad.rotation) != 0):
            #   print("Rot: {0}", pad.rotation)
            #   rotation = str.format(
            #       "translate({1}, {2}) rotate({0}) ", str(-pad.rotation), str(pad_x), str(pad_y))

            #fill_color = 'slategray'

            # d.append(draw.Rectangle(-pad_width / 2, -pad_height / 2, pad_width,
            #                                  pad_height, fill=fill_color, transform= rotation))

            # Draw midpoint
            color = 'red'  # if item.rotation != 45 else 'yellow'
            radius = pad_width / 2 if pad_width < pad_height else pad_height / 2
            d.append(draw.Circle(pad_x, pad_y,
                                 radius / 2, fill=color, stroke_width=2, stroke='black'))

    d.setRenderSize(width, height)
    d.savePng(output_image_name + ".png")
    d.saveSvg(output_image_name + ".svg")
