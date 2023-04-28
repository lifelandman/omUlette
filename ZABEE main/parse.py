import bpy

accepted_types = ('MESH')

def process_mesh(mesh, name, mats, useTex, indent = 1):#should return egg string for this mesh without hierarchy indentation
    newliner = "\n" + (" "* indent)
    
    
    #create vertecies.
    #We have several duplicate verticies so the same point can coorispond to multiple uv coordinates.

    loop_id_lookup = {}#This is gonna be a dictionary where a loop id coorisponds to one of the vertexpool's verticies.
                       #This is so when we're making polygons, we can look up verticie ids by loop, if need be.

    uv_match_check = {}#ex of what this will look like: {vert.id, {(uxx, uvy), eggvertid}}
    
    egg_data = newliner + "<VertexPool> " + name + "_pool {"

    idNum = 0

    for loop in mesh.loops:#Generate verticies and lookup table(s)

        vertex_id = loop.vertex_index
        loop_id = loop.index
        uvLoop = mesh.uv_layers[0]
        uv_cor = uvLoop.uv[loop_id]

        vert = mesh.vertices[vertex_id]

        if vertex_id in uv_match_check:
            if uv_cor in uv_match_check[vertex_id]:
                loop_id_lookup[loop_id] = uv_match_check[vertex_id][uv_cor]
                continue

        egg_data += (newliner + " <Vertex> " + str(idNum) + ' { ' + str(vert.co[0]) + ' ' + str(vert.co[1]) + ' ' + str(vert.co[2])
        + newliner + "  <Normal> { " + str(vert.normal[0]) + ' ' + str(vert.normal[1]) + ' ' + str(vert.normal[2]) + '}' + newliner
        + "  <UV> { " + str(uv_cor.vector.x) + ' ' + str(uv_cor.vector.y) + " }"
        )
        egg_data += '}'

        if not vertex_id in uv_match_check:
            uv_match_check[vertex_id] = {}

        uv_match_check[vertex_id][uv_cor] = vert
        loop_id_lookup[loop_id] = idNum
        idNum +=1#counter for how many vertices we've made
                
    
    egg_data += '\n}'

    idNum = 0
    for poly in mesh.polygons:
        egg_data += newliner + "<Polygon> " + str(idNum) + " { "
        
        if useTex:
            egg_data += "<TRef> { " + mats[poly.material_index] + " }" + newliner
        
        egg_data += " <VertexRef> { "
        for loop in poly.loop_indices:
            egg_data += str(loop_id_lookup[loop]) + ' '
        egg_data += "<ref> { " + name + "_pool }}}"

        idNum += 1

    return egg_data
    
from math import degrees
    
def childProcess(objects, known_objects, known_names, texture_path, indent = 0):
    newliner = "\n" + (" "* indent)
    egg_string = "\n"
    
    for obj in objects:
        if not obj in known_objects:
            known_objects.append(obj)

            mats = []

            name = obj.name.replace(" ", "_")
            nameinc = 0
            nameTest = name
            while nameTest in known_names:
                nameinc += 1
                nameTest = name + str(nameinc)
            if nameinc > 0:
                name = nameTest
            known_names.append(name)
            
            if obj.type in accepted_types:

                egg_string += (newliner + "<Instance> %s {" % name + newliner)#Todo:: Use group where it's more appropriate.... likely best to do group creation on a per-object level

                #Apply Transforms
                is_transformed = False
                transform_string =" <Transform> {"

                transdata = obj.scale
                if (transdata[0] != 0) or (transdata[1] != 0) or (transdata[2] != 0):
                    transform_string += newliner + '  <Scale> { ' + str(transdata[0]) + ' ' + str(transdata[1]) + ' ' + str(transdata[2]) + ' }'
                    is_transformed = True

                transdata = obj.rotation_euler#Oddity in egg syntax necessitates this
                if (transdata[0] != 0):
                    transform_string += newliner + '  <RotX> { ' + str(degrees(transdata[0])) + ' }'
                    is_transformed = True
                if (transdata[1] != 0):
                    transform_string += newliner + '  <RotY> { ' + str(degrees(transdata[1])) + ' }'
                    is_transformed = True
                if (transdata[2] != 0):
                    transform_string += newliner + '  <RotZ> { ' + str(degrees(transdata[2])) + ' }'
                    is_transformed = True

                transdata = obj.location
                if (transdata[0] != 0) or (transdata[1] != 0) or (transdata[2] != 0):
                    transform_string += newliner + '  <Translate> { ' + str(transdata[0]) + ' ' + str(transdata[1]) + ' ' + str(transdata[2]) + '}'
                    is_transformed = True


                if is_transformed:
                    transform_string += newliner + '  }'
                    egg_string += transform_string
                del transdata
                del transform_string
                ##End transform application


                child_addition = ''
                children = obj.children
                if len(children) > 0:
                    child_addition = childProcess(children, known_objects, known_names, texture_path, indent + 1)
                if obj.type == "MESH":

                    useTex = False
                    #Add texture references, and calculate the slot data for materials
                    picnum = len(obj.to_mesh().materials)
                    if picnum != 0:
                        for i in range(picnum):
                            mat = obj.to_mesh().materials[i]
                            img_name = None
                            tex_name = None
                            for x in mat.node_tree.nodes:
                                if x.bl_static_type=='TEX_IMAGE':##THIS IS APPARENTLY DEPRICATED; and for some f*****g reason the only alternative I can find is as well. good luck, future me!
                                   img_name = x.image.name
                                   tex_name = img_name.replace(' ', '_')
                                   useTex = True
                                   mats.append(tex_name)
                                   egg_string += "\n<Texture> " + tex_name + " { " + texture_path + img_name + " }"
                                   break

                        egg_string += newliner

                    #Process the mesh, and apply texture stuff in necissary
                    new_addition = process_mesh(obj.to_mesh(), name, mats, useTex, indent + 1)
                    egg_string += new_addition
                
                egg_string += child_addition
                
                egg_string += newliner + "}"
    return egg_string
                
                
######################## MAIN FUNCTION #####################################################

def write_egg_string(texture_path):
    known_objects = []
    known_names = []#necissary so we can tell when we need to add an incrementing digit if multiple objects share a name.
    
    egg_string = "<CoordinateSystem> { Z-Up }\n\n"
    
    mats = []

    child_addition = childProcess(bpy.data.objects, known_objects, known_names, texture_path)#This should be happening after mesh definition.

    egg_string += child_addition
    return egg_string
                    