from math import degrees


def gen_anim_egg_string(armDict, armatures, armMems, collapse_nodes):
    #print("beginning armiture writing")


    eggStr = "\n"
    
    for arm in armatures:
        if not arm.name in armDict:
            continue
        eggStr += "\n<Group> %s {\n <Dart> { %s }" % (arm.name.replace(' ', '_'), "1" if collapse_nodes else "structured")

        #create classic groups
        eggStr += armMems[arm.name]

        knownBones = []        

        for bone in arm.bones:
            if (bone.name in armDict[arm.name]) and not (bone.name in knownBones):
                if bone.parent:#This loop is only for top level bones. writeBoneEgg handles hierarchy.
                    #print(bone.name + 'has parent')
                    continue
                eggStr = writeBoneEgg(eggStr, bone, armDict[arm.name][bone.name], 2, knownBones)
                
        eggStr += '}\n'

    return eggStr
############################################################################################
def writeBoneEgg(eggStr, bone, poolDict, indent, knownBones):
    
    if bone.name in knownBones:#Edge case, idk if this is even nessisary
        return
    knownBones.append(bone.name)
        

    eggStr += (indent*" ") + "<Joint> " + bone.name.replace(' ', '_') + " {\n"
    eggStr += ((indent+1)*" ") + "<Transform> {\n" + ((indent + 2) * " ")
    #calc bone transforms
    
    mat = bone.matrix_local
    scale = mat.to_scale()
    rot = mat.to_euler()#WARNING! these are radians
    trans = mat.to_translation()
    
    if (scale[0]) or (scale[1]) or (scale[2]):
        eggStr += "<Scale> { " + str(scale.x) + ' ' + str(scale.y) + ' ' + str(scale.z) + ' }\n' + ((indent+ 2)*' ')
        
    if rot[0]:
        eggStr += "<RotX> { " + str(degrees(rot.x)) + ' }\n' + ((indent+ 2)*' ')
    if rot[1]:
        eggStr += "<RotY> { " + str(degrees(rot.y)) + ' }\n' + ((indent+ 2)*' ')
    if rot[2]:
        eggStr += "<RotZ> { " + str(degrees(rot.x)) + ' }\n' + ((indent+ 2)*' ')
    
    if trans[0] or trans[1] or trans[2]:
        eggStr += "<Translate> { " + str(trans[0]) + ' ' + str(trans[1]) + ' ' + str(trans[2]) + " }"#Last possible transform, so no new line plus indent
    
    #cap transform
    eggStr += '\n' + ((indent + 1) * ' ') + "}\n"
    
    for pool in poolDict:
        for weight in poolDict[pool]:
            eggStr += ((indent + 1) * ' ') + "<VertexRef> { "
            for idx in poolDict[pool][weight]:
                eggStr += str(idx) + ' '
            
            if weight != 1:
                eggStr += '<Scalar> membership { ' + str(weight) + ' } '
            eggStr += "<Ref> { " + pool + "} }\n"
    
    #Repeat for children. We do children in this function to preserve hierarchy.
    for child in bone.children:
        eggStr = writeBoneEgg(eggStr, child, poolDict, indent + 1, knownBones)
    
    eggStr += indent*' ' + '}\n'
    return eggStr