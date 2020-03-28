import drawSvg as draw

from data_structs import Pad, Element
from typing import List


def create_svg(element_list):
    # Fixed size for PCB image
    d = draw.Drawing(4797, 2697, origin='center')

    d.append(draw.Image(-(4797 / 2), -(2697 / 2),
                        4797, 2697, "BetaPB/axiom_beta_power_board_v0.34_top.png"))
    factor = 47.2
    for item in element_list.values():
        for pad in item.pads.values():

            pad_x = float(pad.x) * factor
            pad_y = float(pad.y) * factor

            pad_width = float(pad.width) * factor
            pad_height = float(pad.height) * factor

            #rotation = ""
            #if(int(pad.rotation) != 0):
             #   print("Rot: {0}", pad.rotation)
             #   rotation = str.format(
             #       "translate({1}, {2}) rotate({0}) ", str(-pad.rotation), str(pad_x), str(pad_y))

            #fill_color = 'slategray'
            
            #d.append(draw.Rectangle(-pad_width / 2, -pad_height / 2, pad_width,
            #                                  pad_height, fill=fill_color, transform= rotation))

            # Draw midpoint
            color = 'red'  # if item.rotation != 45 else 'yellow'
            radius = pad_width / 2 if pad_width < pad_height else pad_height / 2
            d.append(draw.Circle(pad_x, pad_y,
                                           radius / 2, fill=color, stroke_width=2, stroke='black'))

    d.setRenderSize(4797, 2697)
    d.savePng('brd_pad_preview.png')
    d.saveSvg('brd_pad_preview.svg')
