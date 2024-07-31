from unittest import skip
import bpy
from . import omuAnims
from .props import *

skippingUvs = False

def process_mesh(mesh, name, mats, useTex, boneNames, vgroups, anim_check, boneDict, indent = 1):#should return egg string for this mesh without hierarchy indentation
    newliner = "\n" + (" "* indent)
    
    
    #create vertecies.
    #We have several duplicate verticies so the same point can coorispond to multiple uv coordinates.
    #TODO:: We have duplicates where they are not needed.

    loop_id_lookup = {}#This is gonna be a dictionary where a loop id coorisponds to one of the vertexpool's verticies.
                       #This is so when we're making polygons, we can look up verticie ids by loop, if need be.

    uv_match_check = {}#ex of what this will look like: {vertex_id: {uv_cor, eggvertid}}
    
    egg_data = newliner + "<VertexPool> " + name + "_pool {"

    idNum = 0
    for loop in mesh.loops:#Generate verticies and lookup table(s)
        #Please note that in bpy loops refer to more or less the "triangles" of a mesh.

        vertex_id = loop.vertex_index
        loop_id = loop.index
        

        vert = mesh.vertices[vertex_id]

        if ((not useTex) and skippingUvs) or len(mesh.uv_layers) == 0:#no textures? then skip the uvs which lead to excess verts.
            uv_cor_str = 'null'#TODO:: give users the option to toggle this behavior
        else:
            uvLoop = mesh.uv_layers[0]
            uv_cor = uvLoop.uv[loop_id].vector
            uv_cor_str = str(uv_cor.x) +' '+ str(uv_cor.y)#Stupid hack because something hasn't been working
        if vertex_id in uv_match_check:#TODO:: Test that this works
            if uv_cor_str in uv_match_check[vertex_id]:
                loop_id_lookup[loop_id] = uv_match_check[vertex_id][uv_cor_str]
                continue
            
        co = vert.undeformed_co
        egg_data += (newliner + " <Vertex> " + str(idNum) + ' { ' + str(co[0]) + ' ' + str(co[1]) + ' ' + str(co[2])
        + newliner + "  <Normal> { " + str(vert.normal.x) + ' ' + str(vert.normal.y) + ' ' + str(vert.normal.z) + '}' + newliner)
        if useTex and len(mesh.uv_layers) != 0: egg_data += "  <UV> { " + uv_cor_str + " }"
        egg_data += '}'

        if not vertex_id in uv_match_check:
            uv_match_check[vertex_id] = {}

        uv_match_check[vertex_id][uv_cor_str] = idNum
        loop_id_lookup[loop_id] = idNum


        if anim_check:
            for card in vert.groups:#iterate through vertex group membership
                groupName = vgroups[card.group]
                if groupName in boneNames:#this v group coorisponds to a bone
                    #print("recognised bone name!")

                    if groupName not in boneDict:#we don't have a dict for this group
                        boneDict[groupName] = {}#We create a dict for this bone
                        #print("created dict for bone refs")
                        

                    if name + "_pool" not in boneDict[groupName]:#no reference to this mesh's vert pool yet
                        boneDict[groupName][name + "_pool"] = {}#We create a dict to hold membership strength values
                        #print("created ref dict")

                    if card.weight not in boneDict[groupName][name + "_pool"]:
                        boneDict[groupName][name + "_pool"][card.weight] = []
                        #print("created list for storing verts of given weight")

                    if idNum not in boneDict[groupName][name + "_pool"][card.weight]:#We don't have this ID number yet, so let's add it for refrence during bone definition.
                        boneDict[groupName][name + "_pool"][card.weight].append(idNum)
                        #print("added vert ID")
        #Create entries for bones without geometry to avoid a crash. Yes this causes a memory leak.
            for bname in boneNames:
                if bname not in boneDict:
                    boneDict[bname] = {}

        idNum +=1#counter for how many vertices we've made
                
    
    egg_data += '\n}'

    idNum = 0
    for poly in mesh.polygons:
        egg_data += newliner + "<Polygon> " + str(idNum) + " { "
        
        if useTex:
            egg_data += "<TRef> { " + mats[poly.material_index] + " }" + newliner
        
        egg_data += " <VertexRef> { "#now for a bunch of shit that might not even be nessicary.
        for loop in poly.loop_indices:
            egg_data += str(loop_id_lookup[loop]) + ' '
        egg_data += "<ref> { " + name + "_pool }}}"

        idNum += 1

    return egg_data
    
from math import degrees

def childKnowLoop(known_objects, child):##Super hacky, eyuk.
    for i in child.children:
        known_objects.append(i)
        childKnowLoop(known_objects, i)
    
def childProcess(objects, known_objects, known_names, texture_path, using_anim, armDict, armMemDict, genDart, indent = 0):
    newliner = "\n" + (" "* indent)
    egg_string = "\n"
    
    for obj in objects:
        if not obj in known_objects:
            arm = obj.find_armature()#get once, use thrice for both check and bones
            
            if obj.parent != None and not obj.parent in known_objects and arm == None:
                continue
            known_objects.append(obj)
            if obj.type == "ARMATURE":
                continue
            
            #Armature Logic. #if this is the static pass, we add children to known_objects and continue. Otherwise, we build boneDict and generate
            if (arm != None) and using_anim:
                if not arm.name in armDict:
                    armDict[arm.name] = {}                

                if not genDart:
                    if arm.name not in armMemDict:
                        armMemDict[arm.name] = []
                    if obj not in armMemDict[arm.name]:#extra check since this object will be processed again during armature generation
                        armMemDict[arm.name].append(obj)
                    childKnowLoop(known_objects, obj)
                    continue
                    

                anim_check = True
                #Gather armature Bone Names
                arm = arm.data#go from object to armature
                boneNames = []

                for bone in arm.bones:
                    boneNames.append(bone.name)
                #Gather Mesh vertex groups
                vgroups = {}
                for i in obj.vertex_groups:
                    vgroups[i.index] = i.name
                    
                boneDict = armDict[arm.name]

                #We have everything we need
            else:
                boneNames = []
                vgroups = {}
                boneDict = {}
                anim_check = False

            mats = []

            ##################################Possibly not nessicary
            name = obj.name.replace(" ", "_")
            nameinc = 0
            nameTest = name
            while nameTest in known_names:
                nameinc += 1
                nameTest = name + str(nameinc)
            if nameinc > 0:
                name = nameTest
            known_names.append(name)
            ###################################
            

            egg_string += (newliner + "<Instance> %s {" % name + newliner)#Todo:: Use group where it's more appropriate.... likely best to do group creation on a per-object level

            #Apply Transforms
            is_transformed = False
            transform_string =" <Transform> {"
            mat = obj.matrix_local#Hopefully the manual isn't lying and this really is parent-relative
            transdata = obj.scale#scale cannot be determined from matrix alone if negative
            if (transdata[0] != 0) or (transdata[1] != 0) or (transdata[2] != 0):
                transform_string += newliner + '  <Scale> { ' + str(transdata[0]) + ' ' + str(transdata[1]) + ' ' + str(transdata[2]) + ' }'
                is_transformed = True

            transdata = mat.to_euler()
            if (transdata[0] != 0):
                transform_string += newliner + '  <RotX> { ' + str(degrees(transdata[0])) + ' }'
                is_transformed = True
            if (transdata[1] != 0):
                transform_string += newliner + '  <RotY> { ' + str(degrees(transdata[1])) + ' }'
                is_transformed = True
            if (transdata[2] != 0):
                transform_string += newliner + '  <RotZ> { ' + str(degrees(transdata[2])) + ' }'
                is_transformed = True

            transdata = mat.to_translation()
            if (transdata[0] != 0) or (transdata[1] != 0) or (transdata[2] != 0):
                transform_string += newliner + '  <Translate> { ' + str(transdata[0]) + ' ' + str(transdata[1]) + ' ' + str(transdata[2]) + '}'
                is_transformed = True


            if is_transformed:
                transform_string += newliner + '  }'
                egg_string += transform_string
            del transdata
            del transform_string
            del is_transformed
            ##End transform application

            for key in obj.keys():
                if key.lower() in propDict:
                    egg_string += newliner + ' ' + propDict[key.lower()](obj)
                elif issubclass(type(obj[key]), str):
                    egg_string += newliner + ' <Tag> ' + key.replace(' ', '_') + ' { "' + obj[key] + '" }'


            child_addition = ''
            children = obj.children
            if len(children) > 0:
                child_addition = childProcess(children, known_objects, known_names, texture_path, using_anim, armDict, armMemDict, genDart, indent= indent + 1)
            if obj.type == "MESH":
                thisMesh = obj.to_mesh(preserve_all_data_layers=True, depsgraph= bpy.context.evaluated_depsgraph_get())
                useTex = False
                #Add texture references, and calculate the slot data for materials
                picnum = len(thisMesh.materials)
                if picnum != 0:
                    for i in range(picnum):
                        mat = thisMesh.materials[i]
                        img_name = None
                        tex_name = None
                        for x in mat.node_tree.nodes:
                            if x.bl_static_type=='TEX_IMAGE':##THIS IS APPARENTLY DEPRICATED; and for some f*****g reason the only alternative I can find is as well. good luck, future me!
                                img_name = x.image.name
                                tex_name = img_name.replace(' ', '_')
                                useTex = True
                                mats.append(tex_name)
                                egg_string += "\n<Texture> " + tex_name + " { " + texture_path + img_name + " }"
                                #TODO:: add alpha support
                                break

                    egg_string += newliner

                    
                    
                #Process the mesh, and apply texture stuff in necissary
                print(obj.name)    
                new_addition = process_mesh(thisMesh, name, mats, useTex, boneNames, vgroups, anim_check, boneDict, indent + 1)
                egg_string += new_addition
                obj.to_mesh_clear()
                
            egg_string += child_addition
                
            egg_string += newliner + "}"
    return egg_string
                
                
######################## MAIN FUNCTION #####################################################

def write_egg_string(texture_path, all_or_something, using_anim, skip_UUV, collapse_nodes, actionProps, filepath):
    known_objects = []
    known_names = []#necissary so we can tell when we need to add an incrementing digit if multiple objects share a name.
    armDict = {}
    armMemDict = {}
    
    skippingUvs = skip_UUV

    
    egg_string = "<CoordinateSystem> { Z-Up }\n\n"
    

    if not all_or_something:
        obs = bpy.data.objects
    else:
        obs = bpy.context.selected_objects
        for obj in obs:
            if obj.parent != None:
                if obj.parent in obs:
                    continue
                else:
                    known_objects.append(obj.parent)


    child_addition = childProcess(obs, known_objects, known_names, texture_path, using_anim, armDict, armMemDict, False)#This should be happening after mesh definition.
    egg_string += child_addition

    ##Generate group data to hand to armString
    armMems = {}
    #print(armMemDict)
    if using_anim:
        for arm in bpy.data.armatures:
            armMems[arm.name] = childProcess(armMemDict[arm.name], [], known_names, texture_path, True, armDict, armMemDict, True, indent = 1)
        armString = omuAnims.gen_anim_egg_string(armDict, bpy.data.armatures, armMems, collapse_nodes) if using_anim == True else ''
    
        egg_string += armString

    if using_anim:
        egg_string += omuAnims.action2anim(bpy.data.armatures, actionProps, filepath, bpy.context.scene.render.fps)
    
    return egg_string
                    