
class Node:
    def __init__(self, vendor, series, name, score, platform):
        self.vendor = vendor
        self.series = series
        self.name = name
        self.score = score
        self.platform = platform
        self.high = 0
        self.highFix = 0  # 高度修正，避免重叠


def readlistGB(path):
    f = open(path, 'r')
    cnt = int(f.readline())
    ll = []
    for a in range(cnt):
        vendor = f.readline().strip('\r').strip('\n')
        series = f.readline().strip('\r').strip('\n')
        name = f.readline().strip('\r').strip('\n')
        score = int(f.readline().strip('\r').strip('\n'))
        platform  = f.readline().strip('\r').strip('\n')
        ll.append(Node(vendor, series, name, score, platform))
    f.close()
    return ll

def HSL2RGB(h, s, l):
    if h <= 0:
        h = 1e-5
    elif h >= 1:
        h = 1 - 1e-5
    if s <= 0:
        s = 1e-5
    elif s >= 1:
        s = 1 - 1e-5
    if l <= 0:
        l = 1e-5
    elif l >= 1:
        l = 1 - 1e-5
        
    v_1_3 = 1.0 / 3
    v_1_6 = 1.0 / 6
    v_2_3 = 2.0 / 3

    q = l * (1 + s) if l < 0.5 else l + s - (l * s)
    p = l * 2 - q
    tr = h + v_1_3
    tg = h
    tb = h - v_1_3
    rgb = [
        tc + 1.0 if tc < 0 else
        tc - 1.0 if tc > 1 else
        tc
        for tc in (tr, tg, tb)
    ]
    rgb = [
        p + ((q - p) * 6 * tc) if tc < v_1_6 else
        q if v_1_6 <= tc < 0.5 else
        p + ((q - p) * 6 * (v_2_3 - tc)) if 0.5 <= tc < v_2_3 else
        p
        for tc in rgb
    ]
    rgb = tuple(int(i * 256) for i in rgb)

    return rgb

def HSL2BGR(h, s, l):
    r, g, b = HSL2RGB(h, s, l)
    return b, g, r

