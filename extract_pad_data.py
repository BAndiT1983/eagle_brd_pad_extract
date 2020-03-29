#!/usr/bin/python3

from collections import defaultdict
import csv
import math
import os
import re
import sys
from typing import Dict
from xml.etree import ElementTree

from data_structs import Element, Package, Pad
import svg_output


def get_pad_info(smd) -> Pad:
    x = float(smd.attrib["x"])
    y = float(smd.attrib["y"])
    width = float(smd.attrib["dx"])
    height = float(smd.attrib["dy"])

    if width > height:
        width, height = height, width

    pad = Pad(x, y, width, height)

    if("rot" in smd.attrib):
        rotation = smd.attrib["rot"]

        digit_position = re.search(r"\d", rotation)
        rotation = int(rotation[digit_position.start():])

        # if(rotation > 180):
        #    rotation -= 180

        pad.rotation = int(rotation)

    return pad


def get_available_packages(xml_root):
    available_packages = dict()

    package_list = xml_root.findall(".//package")
    for item in package_list:
        package_name = item.attrib["name"]

        # Extract pad data, positions are offsets
        smd_list = item.findall("smd")
        pad_list = dict()
        for smd in smd_list:
            pad = get_pad_info(smd)
            pad_name = smd.attrib["name"]
            pad_list[pad_name] = pad

        package = Package(pad_list)
        available_packages[package_name] = package

    return available_packages


def extract_element_info(root, available_packages, layer="top"):

    available_elements = dict()

    element_list = root.findall(".//element")
    for item in element_list:
        # Skip bottom layer for now
        rotation_angle = 0
        if("rot" in item.attrib):
            rotation_angle = item.attrib["rot"]
            if((rotation_angle.startswith("MR") and layer == "top") or (rotation_angle.startswith("R") and layer == "bottom")):
                continue
            # else:
                # Find first digit position
            digit_position = re.search(r"\d", rotation_angle)
            rotation_angle = rotation_angle[digit_position.start():]
        elif(layer == 'bottom'):
            continue

        package_name = item.attrib["package"]
        x = float(item.attrib["x"]) 
        if (layer == "bottom"):
            x = -x 
        y = float(item.attrib["y"])
        element = Element(
            package_name, defaultdict(), x, y)
        element_name = item.attrib["name"]

        # Temporal limit to certain element for testing
        # if(element_name != "U25"):
        #    continue

        available_elements[element_name] = element

        element.rotation = int(rotation_angle)

        element_package = available_packages[package_name]

        pad_list = dict()
        for name, pad_item in element_package.pads.items():
            pad_x = float(pad_item.x)
            pad_y = float(pad_item.y)

            angle_degree = int(element.rotation)  # int(pad_item.rotation)
            # if(element.rotation != 0):
            #    angle_degree += int(element.rotation)

            angle_rad = math.radians(angle_degree)
            rot_x = pad_x * math.cos(angle_rad) - \
                pad_y * math.sin(angle_rad)
            rot_y = pad_x * math.sin(angle_rad) + \
                pad_y * math.cos(angle_rad)

            pad_x = rot_x
            pad_y = rot_y

            pad_x += element.x
            pad_y += element.y

            pad_width = pad_item.width
            pad_height = pad_item.height

            # if("rot" in pad_item.attrib):
            #    rot = pad_item.attrib["rot"]
            #    if(rot == "R90" or rot == "R270"):
            #        pad_width, pad_height = pad_height, pad_width

            pad = Pad(pad_x, pad_y,
                      pad_width, pad_height, angle_degree + pad_item.rotation)

            pad_list[name] = pad
        element.pads = pad_list

    return available_elements


def output_csv(file_name, element_list: Dict[str, Element]):

    f = open("./" + file_name, "w")

    with f:

        writer = csv.writer(f, delimiter=";")

        # Write CSV header
        header = ["INDEX", "PART_NAME", "PACKAGE_NAME", "PIN_INDEX", "PAD_NAME", "CENTER_X",
                  "CENTER_Y", "LONG_SIDE_LENGTH", "SHORT_SIDE_LENGTH", "ANGLE_DEGREE", "NET"]
        writer.writerow(header)

        # Write data rows
        overall_index = 0
        for element_name, element in element_list.items():
            pad_index = 0
            for pad_name, pad in element.pads.items():
                writer.writerow([overall_index, element_name, element.package,
                                 pad_index, pad_name, round(pad.x, 3), round(pad.y, 3), pad.width, pad.height, pad.rotation, pad.net])

                pad_index += 1
                overall_index += 1


def extract_nets(xml_root, elements):
    signal_root = xml_root.find(".//signals")
    signals = signal_root.findall("signal")

    for signal in signals:
        signal_name = signal.attrib["name"]
        contacts = signal.findall("contactref")

        for contact in contacts:
            element_name = contact.attrib["element"]
            pad_name = contact.attrib["pad"]

            if(element_name in elements):
                element = elements[element_name]
                if(pad_name in element.pads):
                    element.pads[pad_name].net = signal_name


def get_board_dimensions(xml_root):
    dimensions = xml_root.findall(".//wire[@layer=\"20\"]")

    min_x = 0.0
    min_y = 0.0
    max_x = 0.0
    max_y = 0.0

    for dimension in dimensions:
        if float(dimension.attrib["x1"]) < min_x:
            min_x = float(dimension.attrib["x1"])
        if float(dimension.attrib["y1"]) < min_y:
            min_y = float(dimension.attrib["y1"])
        if float(dimension.attrib["x2"]) > max_x:
            max_x = float(dimension.attrib["x2"])
        if float(dimension.attrib["y2"]) > max_y:
            max_y = float(dimension.attrib["y2"])

    return max_x - min_x, max_y - min_y


def main():

    # Check argument count
    if (len(sys.argv) != 2):
        print("Wrong argument count. Usage: extract_data_pad.py <eagle .brd>")
        sys.exit(1)

    brd_file_name = sys.argv[1]
    brd_file_path = os.path.dirname(brd_file_name)
    os.chdir(brd_file_path)
    brd_file_name = os.path.basename(brd_file_name)
    file_name_without_ext = os.path.splitext(brd_file_name)[0]

    tree = ElementTree.parse(brd_file_name)
    xml_root = tree.getroot()

    # Find board dimensions for visualization
    board_width, board_height = get_board_dimensions(xml_root)

    # Make list of available packages
    available_packages = get_available_packages(xml_root)

    # Iterate through elements on the board
    available_elements_top = dict()
    available_elements_top = extract_element_info(
        xml_root, available_packages, "top")

    available_elements_bottom = dict()
    available_elements_bottom = extract_element_info(
        xml_root, available_packages, "bottom")

    extract_nets(xml_root, available_elements_top)
    extract_nets(xml_root, available_elements_bottom)

    # Check if PCB image layer file exists, if yes create output
    if(os.path.isfile(file_name_without_ext + "_top.png")):
        svg_output.create_svg(file_name_without_ext + "_top.png",
                              file_name_without_ext + "_top_preview", available_elements_top, board_width, board_height)

    output_csv(file_name_without_ext + "_top.csv", available_elements_top)

    if(os.path.isfile(file_name_without_ext + "_bottom.png")):
        svg_output.create_svg(file_name_without_ext + "_bottom.png",
                              file_name_without_ext + "_bottom_preview", available_elements_bottom, board_width, board_height)

    output_csv(file_name_without_ext + "_bottom.csv", available_elements_bottom)


main()
