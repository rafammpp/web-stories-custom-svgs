import argparse
import os
import xml.etree.ElementTree as ET
from utils import get_svgs


# get the arguments
parser = argparse.ArgumentParser(description='Normalize paths in SVG files.')
parser.add_argument('input_dir', metavar='input_dir', type=str, nargs='+',
                    help='input_dir file or folder')

args = parser.parse_args()
input_dir = args.input_dir[0]

# get the absolute path of the input_dir
input_dir = os.path.abspath(input_dir)

svg_export = []
for path in get_svgs(input_dir):
    with open(path) as svg:
        tree = ET.parse(svg)
        root = tree.getroot()
        # get the default namespace from the tag (it looks like {http://www.w3.org/2000/svg}svg)
        default_namespace = root.tag[root.tag.find('{')+1:root.tag.find('}')]
        
        # set the default namespace
        ET.register_namespace('', default_namespace)

        width = float(root.attrib["width"].replace("px", ""))
        height = float(root.attrib["height"].replace("px", ""))
        file_name = os.path.basename(path)
        file_name_without_extension = os.path.splitext(file_name)[0]

        # get only the first path, there should be only one
        svg_path = root.find(f"{{{default_namespace}}}path")
        path_data = svg_path.attrib["d"]
        
        # remove width and height attributes
        del root.attrib["width"]
        del root.attrib["height"]

        # add style attribute
        root.attrib["style"] = "{style}"
        output = f"""
const title = '{file_name_without_extension}';
function {file_name_without_extension} ({{ style }}) {{
  return (
    {ET.tostring(root, encoding='unicode', method='html').replace('"{style}"', '{style}')}
  );
}}

export default {{
    aspectRatio: {width} / {height},
    svg: {file_name_without_extension},
    title,
}};"""

        with open(f"{file_name_without_extension}.js", "w") as output_file:
            output_file.write(output)
        
        svg_export.append(f"export {{ default as {file_name_without_extension} }} from './{file_name_without_extension}.js';")

print("Paste the generated .js files in /packages/stickers/src/<your-template-name>/")
print("And paste the following code in the index.js file:")

for export in svg_export:
    print(export)