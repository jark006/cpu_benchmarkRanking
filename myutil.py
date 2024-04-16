
class cpuInfo:
    name:str        # Example: i9 14900K
    score=0         # 单核
    scoreMulti=0    # 多核
    score4sort=0
    vendor:str      # Intel, AMD
    series:str      # I9, I7, R9, R7
    platform:str    # desktop, laptop, server
    rankingIndex=0
    rankingIndexFix=0    # 高度修正，避免重叠
    column=0             # 位于第几列
    isDeprecated=False

    def __init__(self, name:str='Unknown', score:int=0, scoreMulti:int=0, vendor:str='Unknown', series:str='Unknown', platform:str='Unknown'):
        self.name = name
        self.score = score
        self.scoreMulti = scoreMulti
        self.vendor = vendor
        self.series = series
        self.platform = platform

class gpuInfo:
    name:str        # Example: RTX4090
    score=0         # 单核
    vendor:str      # Intel, AMD
    series:str      # 第几代
    platform:str    # desktop, laptop, server
    rankingIndex=0
    rankingIndexFix=0    # 高度修正，避免重叠
    column=0             # 位于第几列
    isDeprecated=False

    def __init__(self, name:str='Unknown', score:int=0, scoreMulti:int=0, vendor:str='Unknown', series:str='Unknown', platform:str='Unknown'):
        self.name = name
        self.score = score
        self.scoreMulti = scoreMulti
        self.vendor = vendor
        self.series = series
        self.platform = platform

def saveDataSet(dataPath:str, cpuInfoDict:dict[str,cpuInfo]):
    deprecateCnt=0
    for cpu in cpuInfoDict.values():
        if cpu.isDeprecated:
            deprecateCnt+=1
    
    with open(dataPath, 'w') as f:
        f.writelines(str(len(cpuInfoDict)-deprecateCnt) + '\n')
        for cpu in cpuInfoDict.values():
            if cpu.isDeprecated:
                continue
            f.writelines(cpu.name + '\n')
            f.writelines(str(cpu.score) + '\n')
            f.writelines(str(cpu.scoreMulti) + '\n')
            f.writelines(cpu.vendor + '\n')
            f.writelines(cpu.series + '\n')
            f.writelines(cpu.platform + '\n')


def loadDataSet(dataPath:str):
    cpuInfoList = []
    with open(dataPath, 'r') as f:
        lines = int(f.readline())
        for i in range(lines):
            name = f.readline().strip()
            score = int(f.readline().strip())
            scoreMulti = int(f.readline().strip())
            vendor = f.readline().strip()
            series = f.readline().strip()
            platform  = f.readline().strip()
            cpuInfoList.append(cpuInfo(name, score, scoreMulti, vendor, series, platform))
    return cpuInfoList


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

