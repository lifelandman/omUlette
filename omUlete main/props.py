
def doColProps(obj):
    string = ""
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
    return string
            
colStart = '<Collide> { '#a silly attempt to minimize the number of strings in memory.
            
colCap = ' descend }'

def writeBox(obj):
    string = colStart + 'Box '
    string += doColProps(obj)
    string += colCap
    return string
    
def writePlane(obj):
    string = colStart + 'Plane '
    string += doColProps(obj)
    string += colCap
    return string
    
def writePolygon(obj):
    string = colStart + 'Polygon '
    string += doColProps(obj)
    string += colCap
    return string
    
def writePolyset(obj):
    string = colStart + 'Polyset '
    string += doColProps(obj)
    string += colCap
    return string
    
def writeSphere(obj):
    string = colStart + 'Sphere '
    string += doColProps(obj)
    string += colCap
    return string
    
def writeInvSphere(obj):
    string = colStart + 'InvSphere '
    string += doColProps(obj)
    string += colCap
    return string
    
def writeTube(obj):
    string = colStart + 'Tube '
    string += doColProps(obj)
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

#This is for quickProps.
colPropList = ("level",
               "keep",
               "event",
               "intangible")