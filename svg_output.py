import drawSvg as draw
from PIL import Image


def get_image_size(image_file_name):
    image = Image.open(image_file_name)
    return image.width, image.height


def draw_legend(d):
    d.append(draw.Circle(250, 320, 20, fill="yellow", stroke="orange"))
    d.append(draw.Line(0, 0, 0, 200, stroke_width=2, stroke="red",
                       fill="yellow", transform="translate(250, -320) rotate(-80)"))

    d.append(draw.Circle(550, 320, 20, fill="yellow", stroke="orange"))
    d.append(draw.Line(0, -100, 0, 100, stroke_width=2, stroke="green",
                       fill="yellow", transform="translate(550, -320) rotate(-30)"))


def draw_via_pads(d, via_list, factor_x, factor_y):
    for via_name, via in via_list:
        via_x = float(via.x) * factor_x
        via_y = float(via.y) * factor_y

        via_length = float(via.length) * factor_x
        via_drill = float(via.drill) * factor_y

        rotation = str.format(
            "translate({1}, {2}) rotate({0}) ", str(-via.rotation), str(via_x), str(-via_y))

        color = "lightgreen"
        d.append(draw.Circle(via_x, via_y,
                             via_drill / 2, fill=color, stroke_width=1, stroke="black", opacity="0.7"))
        d.append(draw.Rectangle(-via_drill / 2, 0,
                                via_drill, via_length, fill=color, stroke_width=1, stroke="black", opacity="0.7",
                                transform=rotation))


def draw_smd_pads(d, smd_list, factor_x, factor_y):
    for pad_name, pad in smd_list:
        pad_x = float(pad.x) * factor_x
        pad_y = float(pad.y) * factor_y

        pad_width = float(pad.width) * factor_x
        pad_length = float(pad.length) * factor_y

        # rotation=str.format(
        #    "translate({0}, {1})", str(pad_x), str(-pad_y))
        rotation = str.format(
            "translate({1}, {2}) rotate({0})", str(-pad.rotation), str(pad_x), str(-pad_y))

        fill_color = "lightskyblue"

        d.append(draw.Rectangle(-pad_width / 2, -pad_length / 2, pad_width,
                                pad_length, stroke_width=1, stroke="black", fill=fill_color, transform=rotation))

        # Draw midpoint
        color = "red"  # if item.rotation != 45 else "yellow"
        radius = pad_width / 2 if pad_width < pad_length else pad_length / 2
        d.append(draw.Circle(pad_x, pad_y,
                             radius / 2, fill=color, stroke_width=1, stroke="black"))
        d.append(draw.Text(pad_name, 30, pad_x, pad_y,
                           fill="yellow", stroke="orange"))


def create_svg(input_image_file, output_image_name, element_list, board_x, board_y, board_width, board_height):
    image_width, image_height = get_image_size(input_image_file)

    factor_x = image_width / board_width
    factor_y = image_height / board_height

    # Fixed size for PCB image
    d = draw.Drawing(image_width, image_height, origin=(board_x * factor_x, board_y * factor_y))

    # Draw background
    d.append(draw.Image(board_x * factor_x, board_y * factor_y,
                        image_width, image_height, input_image_file))

    #draw_legend(d)

    for item in element_list.values():
        draw_via_pads(d, item.via_pads.items(), factor_x, factor_y)
        draw_smd_pads(d, item.smd_pads.items(), factor_x, factor_y)

    d.setRenderSize(image_width, image_height)
    d.savePng(output_image_name + ".png")
    d.saveSvg(output_image_name + ".svg")
