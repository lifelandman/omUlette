import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class makeButtonOperator(Operator):
    """Add a custom property"""
    bl_idname = "omulete.add_quick_property"
    bl_label = "omUleteQuickProperty"
    
    propToAdd: StringProperty(default = "")

    def execute(self, context):
        context.object[self.propToAdd] = True
        return {'FINISHED'}

from .props import propDict, colPropList
class quickPropsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "OmUlete quick properties"
    bl_idname = "OBJECT_PT_omuquickprops"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Add Property:")
        for prop in propDict:
            row = layout.row()
            row.operator(makeButtonOperator.bl_idname, text = prop).propToAdd = prop

        row = layout.row()
        row.label(text="Additional collision props", icon='MATCUBE')
        for prop in colPropList:
            row = layout.row()
            row.operator(makeButtonOperator.bl_idname, text = prop).propToAdd = prop



def register():
    bpy.utils.register_class(quickPropsPanel)
    bpy.utils.register_class(makeButtonOperator)


def unregister():
    bpy.utils.unregister_class(quickPropsPanel)
    bpy.utils.unregister_class(makeButtonOperator)


if __name__ == "__main__":
    register()
