import bpy
from . import omuParse

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator

def write_egg(context, filepath, egg_string):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(egg_string)
    f.close()

    return {'FINISHED'}


#Custom property group/whatever for action export
class animProps(bpy.types.PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action)#With this, we can just have a list of exporting actions via the collectionproperty
    
    export: BoolProperty(name = 'export',
        description = 'export this action.',
        default = True)
    
    filePlace: EnumProperty(name= 'location',
        description= 'choose whether this animation is saved in a file seprate from the rest of the export or included at the bottom',
        items =[('OP1', 'same file', "include this animation in the \"main\" file"), ('OP2', 'new file', "include this animation in it's own file")])





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

    all_or_selected: BoolProperty(
        name="Export only selected objects and children",
        description="If this is set to true, then only the objects currently selected and their children will be exported.",
        default=False,
    )

    expt_animations: BoolProperty(
        name="Export Armatures and Animations",
        description="If this is set to true, then the armature will be exported. (animation export is not yet implemented.)\nthis will be ignored if no armatures are detected in the selected objects.",
        default=False,
    )
    
    collapse_nodes: BoolProperty(
        name="Collapse Character Nodes",
        description="If this is set to true, node structure of aniamted characters will be flattened.",
        default=True,
    )
    
    
    def invoke(self, context, event):#Generate list of Actions so user can select what gets exported and how
        parentRet = ExportHelper.invoke(self, context, event)#call exportHelper's invoke first
        bpy.types.Scene.actionData = CollectionProperty(type = animProps)
        context.scene.actionData.clear()
        for action in bpy.data.actions:
            for f in action.fcurves:##Filter through actions so we only have those that affect bones
                if "pose.bones" in f.data_path:
                    newAction = context.scene.actionData.add()
                    newAction.action = action
                    break
            continue
        return parentRet
    
    def draw(self, context):#Organise and beutify the options
        
        ##Crate a box for basic options
        box = self.layout.box()        

        row = box.row()
        row.label(text= "basic options")
        row = box.row()
        row.prop(context.active_operator, "imageDir")
        row = box.row()
        row.prop(context.active_operator, "all_or_selected")
        
        ##Create a box for animation stuff
        box = self.layout.box()
        
        row = box.row()
        row.prop(context.active_operator, "expt_animations")
        if self.expt_animations:
            row = box.row()
            row.prop(context.active_operator, "collapse_nodes")
            row = box.row()
            ##Add action selection
            subBox = box.box()
            for item in context.scene.actionData:
                row = subBox.row()
                col = row.column()
                col.label(text=item.action.name)
                col = row.column()
                col.prop(item, "export")
                if item.export:
                    col = row.column()
                    col.prop(item, 'filePlace')

    def execute(self, context):##Put egg generating code here:
        if self.all_or_selected and self.expt_animations:
            hasMesh = False
            for i in bpy.context.selected_objects:
                if i.type == "MESH":
                    hasMesh = True
                    break
            if not hasMesh:
                self.report({"ERROR"}, "Cannot export only selected objects and armatures if no mesh is selected!")
                return {"CANCELLED"}
        
        egg_string = omuParse.write_egg_string(self.imageDir, self.all_or_selected, self.expt_animations, self.collapse_nodes, context.scene.actionData, self.filepath)
        del bpy.types.Scene.actionData
        return write_egg(context, self.filepath, egg_string)




# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(export_egg.bl_idname, text="Egg (Panda3D)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(animProps)
    bpy.utils.register_class(export_egg)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(export_egg)
    bpy.utils.unregister_class(animProps)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
