
def doColProps(obj, string):
    if 'level' in obj:
        if obj['level']:
            string += ' level'
    if 'keep' in obj:
        if obj['keep']:
            string += ' keep'
    if 'event' in obj:
        if obj['event']:
            string += ' event'
    if 'intangible' in obj:
        if obj['intangible']:
            string += ' intangible'
            
colStart = '<Collide> { '#a silly attempt to minimize the number of strings in memory.
            
colCap = ' descend }'

def writeBox(obj):
    if obj['collisionBox']:
        string = colStart + 'Box '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writePlane(obj):
    if obj['collisionPlane']:
        string = colStart + 'Plane '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writePolygon(obj):
    if obj['collisionPolygon']:
        string = colStart + 'Polygon '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writePolyset(obj):
    if obj['collisionPolyset']:
        string = colStart + 'Polyset '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writeSphere(obj):
    if obj['collisionSphere']:
        string = colStart + 'Sphere '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writeInvSphere(obj):
    if obj['collisionInvSphere']:
        string = colStart + 'InvSphere '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''
    
def writeTube(obj):
    if obj['collisionTube']:
        string = colStart + 'Tube '
        doColProps(obj, string)
        string += colCap
        return string
    else: return ''

propDict = {
    'collisionBox': writeBox,
    'collisionPlane': writePlane,
    'collisionPolygon':writePolygon,
    'collisionPolyset':writePolyset,
    'collisionSphere':writeSphere,
    'collisionInvSphere':writeInvSphere,
    'collisionTube':writeTube,
    }