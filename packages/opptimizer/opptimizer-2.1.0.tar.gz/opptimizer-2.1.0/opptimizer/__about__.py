import os

__all__ = [
    "__version__",
]


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   as described in https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


# def get_version(rel_path: str) -> str:
#     for line in read(rel_path).splitlines():
#         if line.startswith("__version__"):
#             # __version__ = "0.9"
#             delim = '"' if '"' in line else "'"
#             return line.split(delim)[1]
#     raise RuntimeError("Unable to find version string.")

def get_version(rel_path: str) -> str:
    lines = read(rel_path).splitlines()
    if len(lines)>0:
        return lines[0]
    raise RuntimeError("Unable to find version string.")

__version__ = get_version("version.txt")