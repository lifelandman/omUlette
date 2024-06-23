
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
    string = colStart + 'Box '
    doColProps(obj, string)
    string += colCap
    return string
    
def writePlane(obj):
    string = colStart + 'Plane '
    doColProps(obj, string)
    string += colCap
    return string
    
def writePolygon(obj):
    string = colStart + 'Polygon '
    doColProps(obj, string)
    string += colCap
    return string
    
def writePolyset(obj):
    string = colStart + 'Polyset '
    doColProps(obj, string)
    string += colCap
    return string
    
def writeSphere(obj):
    string = colStart + 'Sphere '
    doColProps(obj, string)
    string += colCap
    return string
    
def writeInvSphere(obj):
    string = colStart + 'InvSphere '
    doColProps(obj, string)
    string += colCap
    return string
    
def writeTube(obj):
    string = colStart + 'Tube '
    doColProps(obj, string)
    string += colCap
    return string

propDict = {
    'collisionbox': writeBox,
    'collisionplane': writePlane,
    'collisionpolygon':writePolygon,
    'collisionpolyset':writePolyset,
    'collisionsphere':writeSphere,
    'collisioninvsphere':writeInvSphere,
    'collisiontube':writeTube,
    }