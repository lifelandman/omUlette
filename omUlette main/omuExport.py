import bpy
from bpy_extras import anim_utils
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
class omuAnimProps(bpy.types.PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action)#With this, we can just have a list of exporting actions via the collectionproperty
    
    export: BoolProperty(name = 'export',
        description = 'export this action.',
        default = True)
    
    filePlace: EnumProperty(name= 'location',
        description= 'choose whether this animation is saved in a file seprate from the rest of the export or included at the bottom',
        items =[('OP1', 'same file', "include this animation in the \"main\" file"), ('OP2', 'new file', "include this animation in it's own file")])


class omuCollectionProps(bpy.types.PropertyGroup):
    collectionPointer: bpy.props.PointerProperty(type=bpy.types.Collection)#With this, we can just have a list of exporting collections via the collectionproperty
    
    useObjects: BoolProperty(name = 'export',
        description = 'export the objects from this collection..',
        default = False)





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
        default="images/",
        description="The path to this model's textures relative\nto the config file's model path"
    ) # type: ignore

    export_objects: EnumProperty(
        items = (("all", "export all objects", "export all objects in the scene"), ("selected_only", "export only selected objects", ""), ("collections", "export from specific collection(s)", "choose collections you'd like to export from.")),
        name="export from",
        description="select an option to choose what objects get exported.",
        default="all",
    ) # type: ignore
    
    skip_UUV: BoolProperty(#skip unneeded UVs
        name="Skip UVs for meshes with no texture",
        description="If this is set to true, then uvs will not be exported unless the relevant mesh has a texture applied. \nIn egg files, a vert cannot use two uv coords at once, so we generate multiple vertecies corisponding to each uv coordinate.",
        default=True,
    ) # type: ignore

    skip_cNormals: BoolProperty(#skip unneeded UVs
        name="Ignore custom normals",
        description="If this is set to true, then the model will be exported using only default normals. \nThis can reduce the vertex count on the exported model.",
        default=False,
    ) # type: ignore

    expt_animations: BoolProperty(
        name="Armatures and Animations",
        description="If this is set to true, then the armature will be exported. (animation export is not yet implemented.)\nthis will be ignored if no armatures are detected in the selected objects.",
        default=False,
    ) # type: ignore

    expt_rest_pose: BoolProperty(
        name="Export rest pose as animation",
        description='''Shortcut for exporting all armatures rest poses as a one-frame animation. Will always be in the same file.
        This may be used for advanced animation blending.
        The end result will be named <ARMATURE_NAME>_rest_pose''',
        default=False,
    ) # type: ignore
    
    collapse_nodes: BoolProperty(
        name="Collapse Character Nodes",
        description="If this is set to true, node structure of aniamted characters will be flattened.",
        default=True,
    ) # type: ignore


    

    '''
    You know something I noticed?
    It is INCREDIBLY dumb to go "Ohhhh so now we're adding this thing called action slots
    and their whole thing is they let you drag and drop actions while animating multiple objects
    and to make things easier we're going to make each action slot have a type so it can only animate one kind of property"
    and then make it so whenever a user makes an action and slot on an armature that slot gets the generic type "OBJECT"

    You wanna know what's even dumber?
    Breaking countless addons because you think that the API isn't complecated and frusturating to work with enough already.
    '''

    def invoke(self, context, event):#Generate list of Actions so user can select what gets exported and how
        parentReturn = ExportHelper.invoke(self, context, event)#call exportHelper's invoke first

        bpy.types.Scene.omuActionData = CollectionProperty(type = omuAnimProps)
        context.scene.omuActionData.clear()
        for action in bpy.data.actions:
            for slot in action.slots:
                channelbag = anim_utils.action_get_channelbag_for_slot(action, slot)#I don't like you I don't wanna be your friend
                #Make accessing stuff follow a natural logical flow.
                #If I need to use an entire different module to get what I need in a simple manner,
                #insults
                for f in channelbag.fcurves:##Filter through actions so we only have those that affect bones
                    if "pose.bones" in f.data_path:
                        newAction = bpy.context.scene.omuActionData.add()
                        newAction.action = action
                        break

        bpy.types.Scene.omuCollectionPropCollection = CollectionProperty(type = omuCollectionProps)
        context.scene.omuCollectionPropCollection.clear()
        for collection in bpy.data.collections:
            newCollection = bpy.context.scene.omuCollectionPropCollection.add()
            newCollection.collectionPointer = collection


        return parentReturn
    
    def draw(self, context):#Organise and beutify the options
        
        ##Crate a box for basic options
        box = self.layout.box()        

        row = box.row()
        row.label(text= "Export Options")
        row = box.row()
        row.prop(context.active_operator, "export_objects")
        if self.export_objects == "collections":
            row = box.row()
            ##Add action selection
            subBox = box.box()
            for item in context.scene.omuCollectionPropCollection:
                row = subBox.row()
                col = row.column()
                col.label(text=item.collectionPointer.name)
                col = row.column()
                col.prop(item, "useObjects")

        row = box.row()
        row.prop(context.active_operator, "imageDir")
        row = box.row()
        row.prop(context.active_operator, "skip_UUV")
        row = box.row()
        row.prop(context.active_operator, "skip_cNormals")
        
        ##Create a box for animation stuff
        box = self.layout.box()
        
        row = box.row()
        row.prop(context.active_operator, "expt_animations")
        if self.expt_animations:
            row = box.row()
            row.prop(context.active_operator, "collapse_nodes")
            row = box.row()
            row.prop(context.active_operator, "expt_rest_pose")
            row = box.row()
            ##Add action selection
            subBox = box.box()
            for item in context.scene.omuActionData:
                row = subBox.row()
                col = row.column()
                col.label(text=item.action.name)
                col = row.column()
                col.prop(item, "export")
                if item.export:
                    col = row.column()
                    col.prop(item, 'filePlace')

    def execute(self, context):##Put egg generating code here:
        if self.export_objects == "selected_only" and self.expt_animations:
            hasMesh = False
            for i in bpy.context.selected_objects:
                if i.type == "MESH":
                    hasMesh = True
                    break
            if not hasMesh:
                self.report({"ERROR"}, "Cannot export only selected objects and armatures if no mesh is selected!")
                return {"CANCELLED"}
        if self.export_objects == "collections" and not any(coll.useObjects for coll in context.scene.omuCollectionPropCollection):
            self.report({"ERROR"}, "Please select (a) collection(s) to export from.")
            return {"CANCELLED"}
        
        egg_string = omuParse.write_egg_string(self.imageDir, self.export_objects, self.expt_animations, self.expt_rest_pose, self.skip_UUV, self.skip_cNormals, self.collapse_nodes, context.scene.omuActionData, context.scene.omuCollectionPropCollection, self.filepath)
        del bpy.types.Scene.omuActionData
        del bpy.types.Scene.omuCollectionPropCollection
        return write_egg(context, self.filepath, egg_string)




# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(export_egg.bl_idname, text="Egg (Panda3D)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(omuAnimProps)
    bpy.utils.register_class(omuCollectionProps)
    bpy.utils.register_class(export_egg)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(export_egg)
    bpy.utils.unregister_class(omuAnimProps)
    bpy.utils.unregister_class(omuCollectionProps)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
