
bl_info = {
    "name": "omUlete",
    "author": "Jackson \"Lifeland\" S.",
    "version": (0, 965),
    "blender": (3, 5, 0),
    "description": "",
    "warning": "",
    "location": "File > Export",
    "wiki_url": "https://github.com/lifelandman/omUlete",
    "category": "Export"}

import bpy
from . import omuExport
from . import quickprops

modules = [omuExport, quickprops]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
