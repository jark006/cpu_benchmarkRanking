'''
 jark006
 date: 2024年4月8日
 jark006@qq.com
'''

import numpy as np
import time
import cv2
import random
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from PIL import ImageFont, ImageDraw, Image
from myutil import *


isDebug = False
dataSource = 'GeekBench6'
authorInfo = 'Make by JARK006'
curVer = 'V2.2'
picFormat = '.png'
buildDateStr = time.strftime("%Y%m%d", time.localtime())
sourcesUrl = 'https://browser.geekbench.com/processor-benchmarks'
htmlPath = 'data/geekbench6.html'
dataSetPath = 'data/gb6DataSet.txt'
qrCodePath = 'pic/qrcode.png'

baiduyunShare = 'https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg?pwd=etpt 提取码: etpt'
aliyunShare = 'https://www.aliyundrive.com/s/jZUioTtYkKD'

# 霞鹜新晰黑  https://github.com/lxgw/LxgwNeoXiHei
# fontPath='LXGWNeoXiHei.ttf'
fontPath='LXGWFasmartGothic.ttf'

# 在此添加 Geekbench 未收录的 CPU
addMore:list[cpuInfo] = [
    # cpuInfo('R5 5600X3D', 2200, 10500, 'AMD', 'R5', 'Desktop'),
    # cpuInfo('R5 7500F', 2600, 11000, 'AMD', 'R5', 'Desktop'),
    # cpuInfo('R7 7840H', 2600, 12000, 'AMD', 'R7', 'Laptop'),
    # cpuInfo('R9 7940H', 2650, 12500, 'AMD', 'R9', 'Laptop'),
]

# 修正单核分数
fixSingleScore = {
    # 'i7-12700': 2350,
    # 'R5 7600X': 2750,
    # 'R5 7700X': 2760,
    # 'R7 7800X3D': 2875,
}
# 修正多核分数
fixMultiScore = {
    # 'i7-12700': 11400,
    # 'i7-13700': 15500,
    # 'i5-12600KF': 10500,
    # 'i5-12600K': 10500,
}

# 所有系列分成两列  各系列所在 第几列：
intelColumnLaptop = {
    'i3': 4,
    'i32': 5,
    'i5': 0,
    'i52': 1,
    'i7': 2,
    'i72': 3,
    'i9': 4,
    'i92': 5,
    'Atom': 0,
    'Atom2': 1,
    'Core2': 0,
    'Core22': 1,
    'Pentium': 2,
    'Pentium2': 3,
    'Celeron': 2,
    'Celeron2': 3,
}

intelColumnDesktop = {
    'Xeon': 2,
    'Xeon2': 3,
    'E5': 0,
    'E52': 1,
    'i3': 8,
    'i32': 9,
    'i5': 4,
    'i52': 5,
    'i7': 6,
    'i72': 7,
    'i9': 8,
    'i92': 9,
    'Core2': 4,
    'Core22': 5,
    'Pentium': 6,
    'Pentium2': 7,
    'Celeron': 8,
    'Celeron2': 9,
}

AMDColumn = {
    'EPYC': 0,
    'EPYC2': 0,
    'TR': 1,
    'TR2': 1,
    'R9': 2,
    'R92': 2,
    'R7': 4,
    'R72': 3,
    'R5': 6,
    'R52': 5,
    'R3': 7,
    'R32': 7,
    'A12': 1,
    'A122': 2,
    'A10': 1,
    'A102': 2,
    'A8': 3,
    'A82': 4,
    'A6': 1,
    'A62': 2,
    'A4': 3,
    'A42': 4,
    'Bulldozer': 0,
    'Bulldozer2': 0,
    'Phenom': 3,
    'Phenom2': 4,
    'Athlon': 5,
    'Athlon2': 6,
    'Turion': 0,
    'Turion2': 0,
    'Other': 5,
    'Other2': 6,
}

def processData(cpuInfoList: list[cpuInfo]):
    global intelColumnLaptop
    global intelColumnDesktop
    global AMDColumn

    setTmp = set()
    for i in cpuInfoList:
        setTmp.add(i.name)

    # 添加新 CPU 数据
    for i in addMore:
        if not setTmp.__contains__(i.name):
            print('Add', i.name, i.score, i.scoreMulti)
            cpuInfoList.append(i)

    # 修正分数
    for cpu in cpuInfoList:
        if fixSingleScore.__contains__(cpu.name):
            print('fixSingleScore {}: {} to {}'.format(cpu.name, cpu.score, fixSingleScore[cpu.name]))
            cpu.score = fixSingleScore[cpu.name]
        if fixMultiScore.__contains__(cpu.name):
            print('fixMultiScore {}: {} to {}'.format(cpu.name, cpu.score, fixMultiScore[cpu.name]))
            cpu.scoreMulti = fixMultiScore[cpu.name]

    print('process Done')


def draw(coreType: str, cpuInfoList: list[cpuInfo]):
    global intelColumnLaptop
    global intelColumnDesktop
    global AMDColumn

    savePath = 'output/GeekBench6_' + coreType + '_' + buildDateStr + '_' + curVer + picFormat

    highScale = 0.2  #高度比例
    fixOffset = 650
    baseScore = 5000
    parameter = [
        1068.3254719330803, -4907.442967544644, -98.48858423691054
    ]
    title = dataSource + '综合性能天梯图'
    watermarkText = title + ' Overall'
    logoPath = 'pic/logoGB6.png'
    percentList = \
        [i for i in range(20,  100+1,5)]+\
        [i for i in range(110, 200+1,10)]+\
        [i for i in range(200, 300+1,20)]+\
        [300,320, 350]

    for cpu in cpuInfoList:
        # 单核权重 30%  多核权重 70%
        cpu.score4sort = int(cpu.score*0.3+cpu.scoreMulti*0.7)

    # 排序
    cpuInfoList.sort(key=lambda e: e.score4sort)


    # 拟合函数
    def func(x, a, b, c):
        # return a * np.arctan(b / x) + c
        return a * np.exp2(b / x) + c

    # Begin -------------------拟合分数，将分数尽可能线性平均分布-------------------
    # def fit(title: str, x, y):
    #     popt, pcov = curve_fit(func, x, y, method='lm')
    #     print('[ {}, {}, {} ]'.format(popt[0], popt[1], popt[2]))
    #     y1 = [func(i, popt[0], popt[1], popt[2]) for i in x]
    #     plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    #     plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    #     plt.plot(x, y, '.', label='原始离散值')
    #     plt.plot(x, y1, 'r', label='拟合曲线')
    #     plt.xlabel('CPU score')
    #     plt.ylabel('High')
    #     plt.legend(loc=4)  # 指定legend的位置
    #     plt.title(title)
    #     plt.savefig('dataAnalysis/' + dataSource + coreType +
    #                 str(int(time.time_ns())) + '.png')
    #     plt.close()
    #     # plt.show()

    # for gap in range(3, 5):
    #     for fixOffset in range(400, 700, 10):
    #         x=list()
    #         x.append(cpuInfoList[0].score4sort+fixOffset)
    #         for cpu in cpuInfoList:
    #             if x[-1] <= (cpu.score4sort+gap+fixOffset): # 间隔取值，区段扎堆数据导致两极数据拟合差距大
    #                 x.append(cpu.score4sort+fixOffset)
    #         x.sort()
    #         y = range(len(x))
    #         fit('拟合结果 Geekbench '+coreType+' offset '+str(fixOffset)+' '+str(gap), x, y)
    # exit()
    # End -------------------拟合分数，将分数尽可能线性平均分布--------------------



    boolDictIntelDesktop = {
        'i3': True,
        'i5': True,
        'i7': True,
        'i9': True,
        'E5': True,
        'Xeon': True,
        'Core2': True,
        'Pentium': True,
        'Celeron': True,
        'Atom': True,
    }
    boolDictIntelLaptop = {
        'i3': True,
        'i5': True,
        'i7': True,
        'i9': True,
        'E5': True,
        'Xeon': True,
        'Core2': True,
        'Pentium': True,
        'Celeron': True,
        'Atom': True,
    }
    boolDictAMD = {
        'EPYC': True,
        'TR': True,
        'R9': True,
        'R7': True,
        'R5': True,
        'R3': True,
        'A12': True,
        'A10': True,
        'A8': True,
        'A6': True,
        'A4': True,
        'Bulldozer': True,
        'Phenom': True,
        'Athlon': True,
        'Turion': True,
        'Other': True,
    }
    # 根据系列规划 CPU 所在的列位置
    for cpu in cpuInfoList:
        if cpu.vendor == 'AMD':
            boolDictAMD[cpu.series] = not boolDictAMD[cpu.series]
            cpu.column = AMDColumn[cpu.series] if boolDictAMD[
                cpu.series] else AMDColumn[cpu.series + '2']
        elif cpu.platform == 'Desktop':
            boolDictIntelDesktop[
                cpu.series] = not boolDictIntelDesktop[cpu.series]
            cpu.column = intelColumnDesktop[
                cpu.series] if boolDictIntelDesktop[
                    cpu.series] else intelColumnDesktop[cpu.series + '2']
        else:
            boolDictIntelLaptop[
                cpu.series] = not boolDictIntelLaptop[cpu.series]
            cpu.column = intelColumnLaptop[cpu.series] if boolDictIntelLaptop[
                cpu.series] else intelColumnLaptop[cpu.series + '2']
            

    def score2high(p, x, highScale):
        # 12代单核有点高，从140%性能的开始自乘1.0, 线性到200%自乘0.9
        # if coreType == 'Single' and x > baseScore * 1.4:
        #     x = x * (37 / 30.0 - (x / baseScore) / 6)
        return int(func(x, p[0], p[1], p[2]) * highScale)
    
    # 根据性能分数 计算 排名高度
    for cpu in cpuInfoList:
        cpu.rankingIndex = int(score2high(parameter, cpu.score4sort, highScale))

    IntelLaptopListSet = []
    IntelDesktopListSet = []
    AMDListSet = []
    for i in range(1 + max(intelColumnLaptop.values())):
        IntelLaptopListSet.append(set())
    for i in range(1 + max(intelColumnDesktop.values())):
        IntelDesktopListSet.append(set())
    for i in range(1 + max(AMDColumn.values())):
        AMDListSet.append(set())

    for cpu in cpuInfoList:
        rankingIndex = cpu.rankingIndex
        if cpu.vendor == 'AMD':
            while rankingIndex in AMDListSet[
                    cpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            cpu.rankingIndexFix = rankingIndex
            AMDListSet[cpu.column].add(rankingIndex)
        elif cpu.platform == 'Desktop':
            while rankingIndex in IntelDesktopListSet[
                    cpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            cpu.rankingIndexFix = rankingIndex
            IntelDesktopListSet[cpu.column].add(rankingIndex)
        else:
            try:
                while rankingIndex in IntelLaptopListSet[
                        cpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                    rankingIndex -= 1
                cpu.rankingIndexFix = rankingIndex
                IntelLaptopListSet[cpu.column].add(rankingIndex)
            except:
                print('Error', len(IntelLaptopListSet), cpu.column, cpu.name,
                      cpu.series)
                exit(-1)

    highMAX = cpuInfoList[0].rankingIndexFix
    highMIN = highMAX

    for cpu in cpuInfoList:
        if cpu.rankingIndexFix < highMIN:
            highMIN = cpu.rankingIndexFix
        if cpu.rankingIndexFix > highMAX:
            highMAX = cpu.rankingIndexFix

    highMAX += 4
    for cpu in cpuInfoList:
        cpu.rankingIndex -= highMIN - 2
        cpu.rankingIndexFix -= highMIN - 2

    # 规划图片尺寸
    upEdgeHigh = int(100)  # 顶栏高度
    downEdgeHigh = int(120)  # 底栏高度
    edgeWidth = int(20)  # 左右空白边缘宽度
    centerWidth = int(120)  # 中间绘制百分比区域
    cpuTextHigh = int(12)
    cpuTextWidth = cpuTextHigh * 7
    imgHigh = (highMAX - highMIN + 1) * cpuTextHigh + upEdgeHigh + downEdgeHigh
    imgWidth = (max(intelColumnDesktop.values()) + max(intelColumnLaptop.values()) + max(AMDColumn.values()) + 3) * cpuTextWidth \
            + centerWidth + edgeWidth * 2

    intelLaptopXOffset = edgeWidth
    intelDesktopXOffset = intelLaptopXOffset + (
        max(intelColumnLaptop.values()) + 1) * cpuTextWidth
    centerOffset = intelDesktopXOffset + (max(intelColumnDesktop.values()) +
                                          1) * cpuTextWidth
    amdOffset = centerOffset + centerWidth

    img = np.zeros((imgHigh, imgWidth, 4), np.uint8)

    # CPU区域背景色
    img[:, 0:intelDesktopXOffset] = (230, 230, 255, 255)
    img[:, intelDesktopXOffset:centerOffset] = (220, 220, 255, 255)
    img[:, centerOffset:amdOffset] = (230, 230, 230, 255)
    img[:, amdOffset:] = (255, 230, 230, 255)

    # 顶栏背景色
    img[:upEdgeHigh, :intelDesktopXOffset] = (0, 180, 255, 255)
    img[:upEdgeHigh, intelDesktopXOffset:centerOffset] = (0, 150, 255, 255)
    img[:upEdgeHigh, amdOffset:] = (230, 0, 30, 255)

    # 底栏背景色
    img[-downEdgeHigh:, :] = (255, 127, 39, 255)

    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)

    # 在 src 的 xOffset, yOffset 坐标上绘制 pic
    def addPic(src, picPath, xOffset, yOffset):
        pic = cv2.imread(picPath, cv2.IMREAD_UNCHANGED)
        for x in range(pic.shape[1]):  # width
            for y in range(pic.shape[0]):  # high
                a = np.array(pic[y, x], dtype=int)
                b = np.array(src[yOffset + y, xOffset + x], dtype=int)
                src[yOffset + y, xOffset + x] = np.array(
                    (a * a[3] + b * (255 - a[3])) / 255, dtype=np.uint8)
        return pic.shape[1], pic.shape[0]

    w, h = addPic(img, logoPath, 20, 120)
    w, h = addPic(img, qrCodePath, 20, 130+h)

    # 转为 PIL 格式，用于绘制文字。（cv模式不支持自定义中文字体）
    imgPil = Image.fromarray(img)
    draw = ImageDraw.Draw(imgPil)

    font = ImageFont.truetype(fontPath, size=28)

    # draw.text((20, 100 + h + 20),
    #           '100%性能基准分:' + str(baseScore),
    #           font=font,
    #           fill='black')

    # 中间彩条
    if not isDebug:
        for y in range(imgHigh - downEdgeHigh):
            for x in range(centerOffset + 8, amdOffset - 8):
                h = (3 * y - 8 * abs(x - (centerOffset + centerWidth / 2)))
                h = ((h - (h % 200)) % imgHigh) / imgHigh
                draw.point((x, y), fill=HSL2BGR(h, 0.6, 0.80))

    # 中间百分比
    font = font.font_variant(size=24)
    for percent in percentList:
        text = str(percent) + '%'
        _, _, w, _ = font.getbbox(text)
        x = centerOffset + (centerWidth - w) / 2
        high = score2high(parameter, percent / 100 * baseScore,
                          highScale) - highMIN + 2
        y = int(imgHigh - downEdgeHigh - high * cpuTextHigh)
        h = 3 * y / imgHigh + 0.75
        h = h - int(h)
        draw.text((x, y), text, font=font, fill=tuple(HSL2RGB(h, 1, 0.30)))

    # 绘制 cpu
    font = font.font_variant(size=cpuTextHigh)
    AMDLaptopBackground = (180, 200, 255)
    for cpu in cpuInfoList:
        if cpu.vendor == 'AMD':
            textColor = (0, 0, 220)
            x = amdOffset + cpu.column * cpuTextWidth + 5
            y = int(imgHigh - downEdgeHigh - cpu.rankingIndexFix * cpuTextHigh)
            # if cpu.rankingIndex != cpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     cpu.name=cpu.name+' ^'+str(cpu.rankingIndex - cpu.rankingIndexFix)

            # AMD 移动端背景底色
            if cpu.platform == 'Laptop':
                _, _, w, h = font.getbbox(cpu.name)
                draw.rectangle((x - 2, y, x + w + 1, y + h),
                               fill=AMDLaptopBackground)

            draw.text((x, y), cpu.name, font=font, fill=textColor)

        elif cpu.platform == 'Desktop':
            textColor = (220, 0, 0)
            x = cpu.column * cpuTextWidth + intelDesktopXOffset + 5
            y = int(imgHigh - downEdgeHigh - cpu.rankingIndexFix * cpuTextHigh)
            # if cpu.rankingIndex != cpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     cpu.name=cpu.name+' ^'+str(cpu.rankingIndex - cpu.rankingIndexFix)
            draw.text((x, y), cpu.name, font=font, fill=textColor)

        else:
            textColor = (220, 0, 0)
            x = cpu.column * cpuTextWidth + intelLaptopXOffset + 5
            y = int(imgHigh - downEdgeHigh - cpu.rankingIndexFix * cpuTextHigh)
            # if cpu.rankingIndex != cpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     cpu.name=cpu.name+' ^'+str(cpu.rankingIndex - cpu.rankingIndexFix)
            draw.text((x, y), cpu.name, font=font, fill=textColor)

    font = font.font_variant(size=48)
    text = 'Intel移动端'
    _, _, w, h = font.getbbox(text)
    x, y = (intelDesktopXOffset - w) / 2, (100 - h) / 2
    draw.text((x, y), text, font=font, fill='white')
    text = 'Intel服务器及桌面端'
    _, _, w, h = font.getbbox(text)
    x, y = intelDesktopXOffset + (centerOffset - intelDesktopXOffset -
                                  w) / 2, (100 - h) / 2
    draw.text((intelLaptopXOffset + x, y), text, font=font, fill='white')
    text = 'AMD全系列'
    _, _, w, h = font.getbbox(text)
    x, y = amdOffset + (imgWidth - amdOffset - w) / 2, (100 - h) / 2
    draw.text((intelLaptopXOffset + x, y), text, font=font, fill='white')

    y = imgHigh - 105
    font = font.font_variant(size=36)
    draw.text((25, y), title + '  Build ' + buildDateStr + ' ' + curVer, font=font, fill='white')
    
    font = font.font_variant(size=48)
    _, _, w, _ = font.getbbox(authorInfo)
    draw.text((imgWidth - w - 25, y), authorInfo, font=font, fill='white')

    font = font.font_variant(size=24)
    draw.text((25, y + 46),
              '基于GeekBench6公开数据制作，30%单核+70%多核作为综合成绩，以5000分为100%性能基准', 
              font=font,
              fill='white')
    draw.text((25, y + 72),
              '阿里盘更新 ' + aliyunShare + '    百度盘更新 ' + baiduyunShare,
              font=font,
              fill='white')
    
    # 基本绘制完成， 转回 cv 格式
    img = np.array(imgPil)


    # debug 模式
    if isDebug:
        img = np.array(imgPil)
        cv2.imencode(picFormat, img)[1].tofile(savePath)
        print('Debug Mode')
        print(title + ' is done.')
        return

    # 绘制水印层
    font = font.font_variant(size=24)
    text = watermarkText + '\n' + 'Build ' + buildDateStr + ' ' + curVer + '    ' + authorInfo + '\n' + baiduyunShare + '\n' + aliyunShare
    _, _, w, h = font.getbbox(text)
    size = 2 * max(imgHigh, imgWidth)
    watermaskImg = np.zeros((size, size, 4), np.uint8)
    watermaskImg[:, :] = (0, 0, 0, 1)
    watermaskImgPil = Image.fromarray(watermaskImg)
    draw = ImageDraw.Draw(watermaskImgPil)
    for y in range(15, size, 8 * h):
        for x in range(15, size, int(0.4 * w)):
            draw.text((x + random.randint(0, 20), y + random.randint(0, 20)),
                      text,
                      font=font,
                      fill=HSL2RGB(0.2 + random.random() * 0.2, 1, 0.4))

    watermaskImg = np.array(watermaskImgPil)
    matRotate = cv2.getRotationMatrix2D((size / 2, size / 2), 45,
                                        1)  # center, angle, scale
    watermaskImg = cv2.warpAffine(watermaskImg, matRotate, (size, size))
    xStart, yStart = int((size - imgHigh) / 2), int((size - imgWidth) / 2)
    watermaskImg = watermaskImg[yStart:yStart + imgHigh,
                                xStart:xStart + imgWidth]

    
    img = cv2.addWeighted(img, 1, watermaskImg, 0.1, 0)  # 叠加水印层

    # 保存图片
    cv2.imencode(picFormat, img)[1].tofile(savePath)

    print(title + ' is done.')
    print('Path: ' + savePath)


if __name__ == '__main__':
    import download_gb
    # download_gb.downloadAndParseHTML(sourcesUrl, dataSetPath)
    cpuInfoList = loadDataSet(dataSetPath)

    processData(cpuInfoList)
    # draw('Single', cpuInfoList)
    # draw('Multi', cpuInfoList)
    draw('Overall', cpuInfoList)
