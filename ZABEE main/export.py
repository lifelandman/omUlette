import bpy
from . import parse

def write_egg(context, filepath, egg_string):
    print("running write_egg...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write(egg_string)
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class export_egg(Operator, ExportHelper):
    """This function generates and exports an EGG file intended for use with panda3d."""
    bl_idname = "export_egg.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Egg File"

    # ExportHelper mixin class uses this
    filename_ext = ".egg"

    filter_glob: StringProperty(
        default="*.egg",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    imageDir: StringProperty(
        default="images\\",
        description="The path to this model's textures relative\nto the config file's model path"
    )

    def execute(self, context):##Put egg generating code here:
        egg_string = parse.write_egg_string(self.imageDir)
        return write_egg(context, self.filepath, egg_string)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(export_egg.bl_idname, text="Egg (Panda3D)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(export_egg)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(export_egg)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
