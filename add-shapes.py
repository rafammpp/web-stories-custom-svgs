import argparse
import os
import re
import xml.etree.ElementTree as ET

# get the arguments
parser = argparse.ArgumentParser(description='Normalize paths in SVG files.')
parser.add_argument('input', metavar='input', type=str, nargs='+',
                    help='input file or folder')

args = parser.parse_args()
input = args.input[0]

# get the absolute path of the input
input = os.path.abspath(input)


def normalize_svg_path(x: float, y: float, path: str) -> str:
    coords = re.split(' ', path)
    coords = [re.split(r'\s*([A-Za-z,])\s*', coord) for coord in coords]
    coords = [coord for sublist in coords for coord in sublist if coord]
    coord_index = 0
    result = ""
    for value in coords:
        try:
            parsed = float(value)
            scaled = parsed / x if coord_index % 2 == 0 else parsed / y
            result += f"{scaled:.6f} "
            coord_index += 1
        except ValueError:
            result += f"{value} "
            coord_index = 0
    return result.strip()


# get the svgs from path
def get_svgs(path: str) -> list:
    svgs = []
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".svg"):
                    svgs.append(os.path.join(root, file))
    elif os.path.isfile(path):
        if path.endswith(".svg"):
            svgs.append(path)
    return svgs


svg_objs = []

# normalize the paths in the svg
for path in get_svgs(input):
    with open(path) as svg:
        tree = ET.parse(svg)
        root = tree.getroot()
        width = float(root.attrib["width"].replace("px", ""))
        height = float(root.attrib["height"].replace("px", ""))
        # get the file name
        file_name = os.path.basename(path)
        # get the file name without extension
        file_name_without_extension = os.path.splitext(file_name)[0]

        # get only the first path, there should be only one
        svg_path = root.find("{http://www.w3.org/2000/svg}path")
        # get the path data
        path_data = svg_path.attrib["d"]
        # normalize the path
        normalized_path = normalize_svg_path(width, height, path_data)

        svg_objs.append({'name':file_name_without_extension, 'path':normalized_path, 'width':width, 'height':height})

# sort the svgs by name
svg_objs.sort(key=lambda x: x['name'])

for svg in svg_objs:
    print('{')
    print(f'\ttype: \'{svg["name"]}\',')
    print('\tshowInLibrary: true,')
    print(f'\tname: \'{svg["name"]}\',')
    print(f'\tpath: \'{svg["path"]}\',')
    print(f'\tratio: {svg["width"]} / {svg["height"]},')
    print('},')

print("Paste everything in packages/masks/src/constants.ts:MASKS")
