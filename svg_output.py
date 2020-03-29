import os
from typing import List

import drawSvg as draw
from PIL import Image


def get_image_size(image_file_name):
    image = Image.open(image_file_name)
    return image.width, image.height


def create_svg(input_image_file, output_image_name, element_list, board_width, board_height):

    image_width, image_height = get_image_size(input_image_file)

    # Fixed size for PCB image
    d = draw.Drawing(image_width, image_height, origin="center")

    # Remove path from image file name
    d.append(draw.Image(-(image_width / 2), -(image_height / 2),
                        image_width, image_height, input_image_file))

    factor_x = image_width / board_width
    factor_y = image_height / board_height
    for item in element_list.values():
        for pad_name, pad in item.pads.items():

            pad_x = float(pad.x) * factor_x
            pad_y = float(pad.y) * factor_y

            pad_width = float(pad.width) * factor_x
            pad_height = float(pad.height) * factor_y

            rotation = ""
            # rotation = str.format(
            #    "translate({0} {1})", str(pad_x), str(pad_y))
            #if(int(pad.rotation) != 0):
            #    rotation = str.format(
            #        "translate({1}, {2}) rotate({0}) ", str(pad.rotation - 90), str(pad_x), str(pad_y))

            fill_color = "slategray"

            d.append(draw.Rectangle(-pad_height / 2, -pad_width / 2, pad_height,
                                    pad_width, fill=fill_color, transform=rotation))

            # Draw midpoint
            color = "red"  # if item.rotation != 45 else "yellow"
            radius = pad_width / 2 if pad_width < pad_height else pad_height / 2
            d.append(draw.Circle(pad_x, pad_y,
                                 radius / 2, fill=color, stroke_width=1, stroke="black"))
            d.append(draw.Text(pad_name, 30, pad_x, pad_y,
                               fill="yellow", stroke="orange"))

    d.setRenderSize(image_width, image_height)
    d.savePng(output_image_name + ".png")
    d.saveSvg(output_image_name + ".svg")
