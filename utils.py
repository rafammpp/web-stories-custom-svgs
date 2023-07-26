import os

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

