import sys

ENABLE_VERTFILE = False


class Vertex:
    def __init__(self):
        self.x = None
        self.y = None

def toXYZ(n):
    i = n / 10
    if i == 1: return 'X'
    if i == 2: return 'Y'
    if i == 3: return 'Z'
    return None

def toXYZStr(code):
    return toXYZ(int(code))

def toComment(code):
    n = int(code)
    if (10 <= n and n < 40):
        return format(toXYZ(n))
    if (40 <= n and n < 49):
        return 'Val'
    if (50 <= n and n < 59):
        return 'Angle'
    if (n == 0): return 'FigType'
    if (n == 1): return 'Text'
    if (n == 2): return 'Name'
    if (n == 8): return 'Layer'
    if (n == 66): return 'ConnectFlag'
    if (n == 70): return 'ModeFlag'
    if (n == 999): return 'Comment'
    return '?'

def parseCode(code):
    t = code
    com = toComment(t)
    tx = ('____' + t)[-4:]
    if not com is None:
        return '({}) <{}>'.format(tx, com)
    else:
        return '({})'.format(tx)

def blockBegin(code, arg):
    if code == '0':
        if arg == 'SECTION': return True
        if arg == 'POLYLINE': return True
        if arg == 'BLOCK': return True
    return False

def blockEnd(code, arg):
    if code == '0':
        if arg == 'ENDSEC': return True
        if arg == 'SEQEND': return True
        if arg == 'ENDBLK': return True
    return False

def line(l):
    ll = l
    ll = ll.replace('\n', '')
    ll = ll.replace('\r', '')
    return ll

def checkBlock(rc, arg):
    be = False
    cl = False
    if blockBegin(rc, arg):
        be = True
    elif blockEnd(rc, arg):
        cl = True
    return be, cl

def isVertex(rc, arg):
    if rc == '0':
        if arg == 'VERTEX': return True
        if arg == 'POINT': return True
    return False

def mainproc(f, wc, wcl, wv):
    t = None
    indent = 0
    vv = []
    lno = 0
    for l in f:
        ll = line(l)
        lno += 1
        if t is None:
            t = ll
            continue
        rc = t.strip()
        t = None
        arg = ll
        code = parseCode(rc)
        be, cl = checkBlock(rc, arg)

        if isVertex(rc, arg):
            vv.append(Vertex())
        elif len(vv) > 0:
            vt = toXYZStr(rc)
            if vt == 'X':
                vv[-1].x = arg
            elif vt == 'Y':
                vv[-1].y = arg

        if cl:
            indent -= 1
            if (indent < 0):
                indent = 0

        idt = ' ' * (indent * 2)
        if cl:
            wc.write(idt + '}' + '\n')
            wcl.write(idt + '}' + '\n')

        lx = (' ' * 6 + str(lno))[-6:]
        wcl.write(f'[{lx}]')

        wc.write(idt + f'{code} {arg}\n')
        wcl.write(idt + f'{code} {arg}\n')

        if be:
            wc.write(idt + '{' + '\n')
            wcl.write(idt + '{' + '\n')
            indent += 1

    if wv:
        for v in vv:
            wv.write(f'v {v.x} {v.y} 0\n')

def makeAuto(fileIn):
    com = fileIn + '_comment.txt'
    comL = fileIn + '_commentLN.txt'
    vf = fileIn + '_vert.txt'
    with open(fileIn) as f, open(com, 'w') as wc, open(comL, 'w') as wcl:
        if ENABLE_VERTFILE:
            with open(vf, 'w') as wv:
                mainproc(f, wc, wcl, wv)
        else:
            mainproc(f, wc, wcl, None)

def makeArgs():
    for a in sys.argv:
        if a is sys.argv[0]:
            continue
        makeAuto(a)

makeArgs()
