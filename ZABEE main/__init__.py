
bl_info = {
    "name": "ZABEE",
    "author": "Jackson \"Lifeland\" S.",
    "version": (0, 1),
    "blender": (3, 5, 0),
    "description": "",
    "warning": "",
    "location": "File > Export",
    "wiki_url": "",
    "category": "Export"}

import bpy
from . import export

modules = [export]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
