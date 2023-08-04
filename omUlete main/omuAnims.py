from math import degrees
import bpy


def gen_anim_egg_string(armDict, armatures, armMems, collapse_nodes):
    #print("beginning armiture writing")


    eggStr = "\n"
    
    for arm in armatures:
        if not arm.name in armDict:
            continue
        eggStr += "\n<Group> %s {\n <Dart> { %s }" % (clean_name(arm.name), "1" if collapse_nodes else "structured")

        #create classic groups
        eggStr += armMems[arm.name]

        knownBones = []        

        for bone in arm.bones:
            if (bone.name in armDict[arm.name]) and not (bone.name in knownBones):
                if bone.parent:#This loop is only for top level bones. writeBoneEgg handles hierarchy.
                    #print(bone.name + 'has parent')
                    continue
                eggStr = write_bone_egg(eggStr, bone, armDict[arm.name], 2, knownBones)
                
        eggStr += '}\n'

    return eggStr
############################################################################################
def write_bone_egg(eggStr, bone, boneDict, indent, knownBones):
    poolDict = boneDict[bone.name]
    if bone.name in knownBones:#Edge case, idk if this is even nessisary
        return
    knownBones.append(bone.name)
        

    eggStr += (indent*" ") + "<Joint> " + clean_name(bone.name) + " {\n"
    eggStr += ((indent+1)*" ") + "<Transform> {\n" + ((indent + 2) * " ")
    #calc bone transforms
    
    mat = bone.parent.matrix_local.inverted() @ bone.matrix_local if bone.parent else bone.matrix_local#Complicated because we need to not access parent if it doesn't exist
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
        eggStr += "<RotZ> { " + str(degrees(rot.z)) + ' }\n' + ((indent+ 2)*' ')
    
    if trans[0] or trans[1] or trans[2]:
        eggStr += "<Translate> { " + str(trans[0]) + ' ' + str(trans[1]) + ' ' + str(trans[2]) + " }"#Last possible transform, so no new line plus indent
    
    #cap transform
    eggStr += '\n' + ((indent + 1) * ' ') + "}\n"
    
    for pool in poolDict:
        for weight in poolDict[pool]:
            eggStr += ((indent + 1) * ' ') + "<VertexRef> { "
            for idx in poolDict[pool][weight]:
                eggStr += str(idx) + ' '
            
            eggStr += '<Scalar> membership { ' + str(weight) + ' } '
            eggStr += "<Ref> { " + pool + "} }\n"
    
    #Repeat for children. We do children in this function to preserve hierarchy.
    for child in bone.children:
        eggStr = write_bone_egg(eggStr, child, boneDict, indent + 1, knownBones)
    
    eggStr += indent*' ' + '}\n'
    return eggStr


########################ANIMATION EGG GENERATOR###################################
from copy import deepcopy
def action2anim(armatures, actionProps, filepath, fps):
    eggStr = "\n"
    arms = {}
    
    for arm in armatures:
        arms[arm.name] = parse_bone_children(arm)
    
    for prop in actionProps:
        action = prop.action
        if not prop.export:#user has opted to decline this action
            continue
        
        foundArm = False
        loopCheck = False#If this is true, we've found a matching armature
        for arm in armatures:#Find the armature that matches this action.
            for track in bpy.data.objects[arm.name].animation_data.nla_tracks:#Rather hacky to try and grab the armature object, but documentation is lying about whether you can access animation data from armature(ID)
                for strip in track.strips:
                    if strip.action.name == action.name:
                        armature = arm
                        foundArm = True
                        loopCheck = True
                        break
                if loopCheck:
                    break
            if loopCheck:
                break
        del loopCheck
        if not foundArm:#Uh oh! no armature uses this action, so we can't structure the egg data!
            print("Warning! cannot find assosiated armature for action " + action.name)
            continue
        del foundArm#We've found an armature, and broken out of the loops, so we can now start processing.
        
        curvedArm = parse_anim_values(action, deepcopy(arms[clean_name(armature.name)]), bpy.data.objects[armature.name])#We get a dictionary of both hierarchy (done above) and the curves used for each property of bones
    
        animStr = "\n<Table> {\n <Bundle> " + (clean_name(action.name) if prop.filePlace == 'OP1' else clean_name(armature.name)) + " {"
        animStr += "\n  <Table> \"<skeleton>\" {\n"
        
        for bone in armature.bones:
            if bone.parent:
                continue
            else:
                animStr += write_joints(bone, curvedArm, fps, int(action.curve_frame_range[0]), int(action.curve_frame_range[1]))
        
        animStr += "  }\n }\n}"
        
        if prop.filePlace == 'OP1':
            eggStr += animStr
        else:
            f = open(filepath + "_" + clean_name(action.name) + ".egg", 'w', encoding='utf-8')
            f.write(animStr)
            f.close()
    return eggStr


from mathutils import Quaternion
def write_joints(bone, armDict, fps, start, stop, level = 3):
    indent = ' ' * level

    jointStr = indent + "<Table> " + clean_name(bone.name) + " {\n"
    jointStr += indent + " <Xfm$Anim_S$> xform {\n"
    jointStr += indent + "  <Scalar> fps { " + str(fps) + " }\n"
    jointStr += indent + "  <Scalar> order { srpht }\n"##Changed this for testing
    
    boneCN = clean_name(bone.name)
    ##SCALE WRITING
    if 'scale' in armDict[boneCN]:
        jointStr += indent + "  <S$Anim> i { <V>{ "
        jointStr += armDict[boneCN]['scale']["x"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> j { <V>{ "
        jointStr += armDict[boneCN]['scale']["y"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> k { <V>{ "
        jointStr += armDict[boneCN]['scale']["z"]
        jointStr += "}}\n"
    
    ##Rotation WRITING
    if 'rotation' in armDict[boneCN]:
        jointStr += indent + "  <S$Anim> r { <V>{ "
        jointStr += armDict[boneCN]['rotation']["r"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> p { <V>{ "
        jointStr += armDict[boneCN]['rotation']["p"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> h { <V>{ "
        jointStr += armDict[boneCN]['rotation']["h"]
        jointStr += "}}\n"

    ##location WRITING
    if 'translation' in armDict[boneCN]:
        jointStr += indent + "  <S$Anim> x { <V>{ "
        jointStr += armDict[boneCN]['translation']["x"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> y { <V>{ "
        jointStr += armDict[boneCN]['translation']["y"]
        jointStr += "}}\n"
        ############################################
        jointStr += indent + "  <S$Anim> z { <V>{ "
        jointStr += armDict[boneCN]['translation']["z"]
        jointStr += "}}\n"
    del boneCN
    jointStr += indent + " }\n"
            
    #add child bones under this hierarchy
    for child in bone.children:
        jointStr += write_joints(child, armDict, fps, start, stop, level + 1)
    
    jointStr += indent + "}\n"
    return jointStr

def parse_bone_children(arm):#This is an artifact, but I can't remove it because it means rewriting a lot and it's output is still kinda nessicary, even if it no longer deserves it's own function.
    #{'bone1':{'translation':{"x":"3 4 1",...}, 'bone2'...}
    boneDict = {}
    for bone in arm.bones:
        cName = clean_name(bone.name)
        if cName not in boneDict:
            boneDict[cName] = {'translation':{'x':"", 'y':"", 'z':""}, 'rotation':{'r':"", 'p':"", 'h':""}, 'scale':{'x':"", 'y':"", 'z':""}}
        else:
            print("ALERT! Bone name found twice, animation invalid")
        
    return boneDict#We don't process fcurve data here because we don't want to loop through an armature's bones for each action related to that armature. if we just loop for hiarchy once, good.

def parse_anim_values(action, boneDict, armObj):
    pose = armObj.pose
    aLen = action.curve_frame_range
    for bone in pose.bones:#Ensure all bones are selected
        bone.bone.select = True

    for frame in range(int(aLen[0]), int(aLen[1])):
        pose.apply_pose_from_action(action, evaluation_time = frame)
        poseB = armObj.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose
        for bone in poseB.bones:
            cName = clean_name(bone.bone.name)
            if cName not in boneDict:
                print("Alert! Bone was not logged before animation value processing")
            transforms = boneDict[cName]
            
            mat = bone.parent.matrix.inverted() @ bone.matrix if bone.parent else bone.matrix
            scale = bone.scale#This has to be different because negative scale can't be gotten from just a matrix
            rot = mat.to_euler("YXZ")#WARNING! these are radians
            trans = mat.to_translation()
            #Translation
            transforms["translation"]["x"] += (str(trans.x) + ' ')
            transforms["translation"]["y"] += (str(trans.y) + ' ')
            transforms["translation"]["z"] += (str(trans.z) + ' ')
            #Rotation
            transforms["rotation"]["r"] += (str(degrees(rot[1])) + ' ')
            transforms["rotation"]["p"] += (str(degrees(rot[0])) + ' ')
            transforms["rotation"]["h"] += (str(degrees(rot[2])) + ' ')
            #scale
            transforms["scale"]["x"] += (str(scale[0]) + ' ')
            transforms["scale"]["y"] += (str(scale[1]) + ' ')
            transforms["scale"]["z"] += (str(scale[2]) + ' ')
    return boneDict
        

##Utility tool
def clean_name(name):
    return name.replace(' ', '_')
    