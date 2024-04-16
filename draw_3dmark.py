'''
 jark006
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
dataSource = '3DMark TimeSpy'
authorInfo = 'Make by JARK006'
curVer = 'V1.0'
picFormat = '.png'
buildDateStr = time.strftime("%Y%m%d", time.localtime())
sourcesUrl = 'https://benchmarks.ul.com/zh-hans/compare/best-gpus'
dataSetPath = 'data/3dmarkDataSet.txt'
qrCodePath = 'pic/qrcode.png'

baiduyunShare = 'https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg?pwd=etpt 提取码: etpt'
aliyunShare = 'https://www.aliyundrive.com/s/jZUioTtYkKD'

# 霞鹜新晰黑  https://github.com/lxgw/LxgwNeoXiHei
# fontPath='LXGWNeoXiHei.ttf'
fontPath='LXGWFasmartGothic.ttf'

# 在此添加 Geekbench 未收录的 GPU
addMore:list[gpuInfo] = [
    # gpuInfo('R5 5600X3D', 2200, 10500, 'AMD', 'R5', 'Desktop'),
]

# 修正单核分数
fixSingleScore = {
    # 'i7-12700': 2350,
    # 'R5 7600X': 2750,
}
# 修正多核分数
fixMultiScore = {
    # 'i7-12700': 11400,
    # 'i7-13700': 15500,
}

# 所有系列分成两列  各系列所在 第几列：
NvidiaColumn = {
    'RTX4': 5,
    'RTX3': 4,
    'RTXA': 4,
    'RTX2': 3,
    'RTX1': 3,
    'GTX16': 2,
    'GTX10': 1,
    'GTX9': 0,
    'GTX8': 0,
    'GTX7': 5,
    'GTX6': 4,
    'GT': 3,
    'Titan': 2,
    'Mobile': 2,
}

IntelColumn = {
    'Arc': 0,
    'UHD': 0,
    'HD': 0,
    'Iris': 0,
}

AMDColumn = {
    'RX7': 0,
    'RX6': 1,
    'RX5': 2,
    'RX4': 3,
    'RX50': 3,
    'RX40': 3,
    'R9': 0,
    'R7': 1,
    'R5': 2,
    'Vega': 1,
    'Radeon': 1,
    'Other': 2,
}

def processData(gpuInfoList: list[gpuInfo]):
    global NvidiaColumn
    global IntelColumn
    global AMDColumn

    setTmp = set()
    for i in gpuInfoList:
        setTmp.add(i.name)

    # 添加新 GPU 数据
    for i in addMore:
        if not setTmp.__contains__(i.name):
            print('Add', i.name, i.score, i.scoreMulti)
            gpuInfoList.append(i)

    # 修正分数
    for gpu in gpuInfoList:
        if fixSingleScore.__contains__(gpu.name):
            print('fixSingleScore {}: {} to {}'.format(gpu.name, gpu.score, fixSingleScore[gpu.name]))
            gpu.score = fixSingleScore[gpu.name]
        if fixMultiScore.__contains__(gpu.name):
            print('fixMultiScore {}: {} to {}'.format(gpu.name, gpu.score, fixMultiScore[gpu.name]))
            gpu.scoreMulti = fixMultiScore[gpu.name]

    print('process Done')


def draw(coreType: str, gpuInfoList: list[gpuInfo]):
    global NvidiaColumn
    global IntelColumn
    global AMDColumn

    savePath = 'output/3DMark_' + '_' + buildDateStr + '_' + curVer + picFormat

    highScale = 0.5  #高度比例
    fixOffset = 10000
    baseScore = 10000
    # parameter = [ 796.621935379174, -6120.371397702502, -498.7991449765785 ]
    parameter = [ 342.681689559398, -9299.090611064696, -49.0954724653573 ]
    title = dataSource + ' GPU性能天梯图'
    watermarkText = title + ' Overall'
    logoPath = 'pic/logoGB6.png'
    percentList = \
        [i for i in range(10,  100, 10)]+\
        [i for i in range(100, 200, 20)]+\
        [i for i in range(200, 500, 50)]

    # 排序
    gpuInfoList.sort(key=lambda e: e.score, reverse=True)


    # 拟合函数
    def func(x, a, b, c):
        # return a * np.arctan(b / x) + c
        return a * np.exp2(b / x) + c

    # Begin -------------------拟合分数，将分数尽可能线性平均分布-------------------
    if False:
    # if True:
        def fit(title: str, x, y, fixOffset):
            popt, pcov = curve_fit(func, x, y, method='lm')
            print('{} [ {}, {}, {} ]'.format(fixOffset, popt[0], popt[1], popt[2]))
            y1 = [func(i, popt[0], popt[1], popt[2]) for i in x]
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            plt.plot(x, y, '.', label='原始离散值')
            plt.plot(x, y1, 'r', label='拟合曲线')
            plt.xlabel('GPU score')
            plt.ylabel('High')
            plt.legend(loc=4)  # 指定legend的位置
            plt.title(title)
            plt.savefig('dataAnalysis/' + dataSource + coreType +
                        str(int(time.time_ns())) + '.png')
            plt.close()
            # plt.show()

        # # for gap in range(1, 2):
        # for fixOffset in range(1000, 10000, 1000):
        #     x=list()
        #     x.append(gpuInfoList[0].score+fixOffset)
        #     for gpu in gpuInfoList:
        #         # if x[-1] <= (gpu.score+gap+fixOffset): # 间隔取值，区段扎堆数据导致两极数据拟合差距大
        #         x.append(gpu.score+fixOffset)
            
        #     # a,b=x[-1]-100, x[-1]
        #     # for i in range(a,b):
        #     #     x.append(i)

        #     x.sort()
        #     y = range(len(x))+200
        #     fit('拟合结果 Geekbench '+coreType+' offset '+str(fixOffset), x, y)
        # exit()
        
        for fixOffset in range(2000, 4000, 200):
            x=list()
            x.append(gpuInfoList[0].score)
            for gpu in gpuInfoList:
                x.append(gpu.score+fixOffset)
            
            # idxEnd = len(x)
            # idxBegin=int(2*idxEnd/4)
            # k=gpuInfoList[idxBegin].score/gpuInfoList[-1].score
            # for i in range(idxBegin, idxEnd):
            #     x.append(int(gpuInfoList[i].score*k))

            idxBegin=int(0.85*len(x))
            idxEnd = len(x)
            v = int(x[-1])
            for i in range(idxBegin, idxEnd):
                x.append(v)
                

            x.sort()
            y = range(len(x))
            fit('拟合结果 Geekbench '+coreType+' offset '+str(fixOffset), x, y, fixOffset)
        exit()
    # End -------------------拟合分数，将分数尽可能线性平均分布--------------------


    # 根据系列规划 GPU 所在的列位置
    for gpu in gpuInfoList:
        if gpu.vendor == 'AMD':
            gpu.column = AMDColumn[gpu.series]
        elif gpu.vendor == 'Intel':
            gpu.column = IntelColumn[gpu.series]
        else:
            gpu.column = NvidiaColumn[gpu.series]
            

    def score2high(p, x, highScale):
        # 12代单核有点高，从140%性能的开始自乘1.0, 线性到200%自乘0.9
        # if coreType == 'Single' and x > baseScore * 1.4:
        #     x = x * (37 / 30.0 - (x / baseScore) / 6)
        return int(func(x, p[0], p[1], p[2]) * highScale)
    
    # 根据性能分数 计算 排名高度
    for gpu in gpuInfoList:
        gpu.rankingIndex = int(score2high(parameter, gpu.score, highScale))

    NvidiaListSet = []
    IntelListSet = []
    AMDListSet = []
    for i in range(1 + max(NvidiaColumn.values())):
        NvidiaListSet.append(set())
    for i in range(1 + max(IntelColumn.values())):
        IntelListSet.append(set())
    for i in range(1 + max(AMDColumn.values())):
        AMDListSet.append(set())

    for gpu in gpuInfoList:
        rankingIndex = gpu.rankingIndex
        if gpu.vendor == 'AMD':
            while rankingIndex in AMDListSet[
                    gpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            gpu.rankingIndexFix = rankingIndex
            AMDListSet[gpu.column].add(rankingIndex)
        elif gpu.vendor == 'Intel':
            while rankingIndex in IntelListSet[
                    gpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            gpu.rankingIndexFix = rankingIndex
            IntelListSet[gpu.column].add(rankingIndex)
        else:
            try:
                while rankingIndex in NvidiaListSet[
                        gpu.column]:  # 已存在的必定比当前的性能强，只能往下排
                    rankingIndex -= 1
                gpu.rankingIndexFix = rankingIndex
                NvidiaListSet[gpu.column].add(rankingIndex)
            except:
                print('Error', len(NvidiaListSet), gpu.column, gpu.name,
                      gpu.series)
                exit(-1)

    highMAX = gpuInfoList[0].rankingIndexFix
    highMIN = highMAX

    for gpu in gpuInfoList:
        if gpu.rankingIndexFix < highMIN:
            highMIN = gpu.rankingIndexFix
        if gpu.rankingIndexFix > highMAX:
            highMAX = gpu.rankingIndexFix

    highMAX += 4
    for gpu in gpuInfoList:
        gpu.rankingIndex -= highMIN - 2
        gpu.rankingIndexFix -= highMIN - 2

    # 规划图片尺寸
    upEdgeHigh = int(100)  # 顶栏高度
    downEdgeHigh = int(120)  # 底栏高度
    edgeWidth = int(20)  # 左右空白边缘宽度
    centerWidth = int(120)  # 中间绘制百分比区域
    gpuTextHigh = int(12)
    gpuTextWidth = gpuTextHigh * 12
    imgHigh = (highMAX - highMIN + 1) * gpuTextHigh + upEdgeHigh + downEdgeHigh
    imgWidth = (max(IntelColumn.values()) + max(NvidiaColumn.values()) + max(AMDColumn.values()) + 3) * gpuTextWidth \
            + centerWidth + edgeWidth * 2

    intelXOffset = edgeWidth
    nvidiaXOffset = intelXOffset + (
        max(IntelColumn.values()) + 1) * gpuTextWidth
    centerOffset = nvidiaXOffset + (max(NvidiaColumn.values()) +
                                          1) * gpuTextWidth
    amdOffset = centerOffset + centerWidth

    img = np.zeros((imgHigh, imgWidth, 4), np.uint8)

    # GPU区域背景色
    img[:, 0:nvidiaXOffset] = (230, 230, 255, 255)
    img[:, nvidiaXOffset:centerOffset] = (230, 240, 210, 255)
    img[:, centerOffset:amdOffset] = (230, 230, 230, 255)
    img[:, amdOffset:] = (255, 230, 230, 255)

    # 顶栏背景色
    img[:upEdgeHigh, :nvidiaXOffset] = (0, 180, 255, 255)
    img[:upEdgeHigh, nvidiaXOffset:centerOffset] = (118, 185, 0, 255)
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

    # w, h = addPic(img, logoPath, 20, 120)
    # w, h = addPic(img, qrCodePath, 20, 130+h)

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
        y = int(imgHigh - downEdgeHigh - high * gpuTextHigh)
        h = 3 * y / imgHigh + 0.75
        h = h - int(h)
        draw.text((x, y), text, font=font, fill=tuple(HSL2RGB(h, 1, 0.30)))

    # 绘制 gpu
    font = font.font_variant(size=gpuTextHigh)
    AMDLaptopBackground = (180, 200, 255)
    NvidiaLaptopBackground = (160, 220, 200)
    for gpu in gpuInfoList:
        if gpu.vendor == 'AMD':
            textColor = (0, 0, 220)
            x = amdOffset + gpu.column * gpuTextWidth + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)

            # AMD 移动端背景底色
            if gpu.platform == 'Laptop':
                _, _, w, h = font.getbbox(gpu.name)
                draw.rectangle((x - 2, y, x + w + 1, y + h),
                               fill=AMDLaptopBackground)

            draw.text((x, y), gpu.name, font=font, fill=textColor)

        elif gpu.vendor == 'NVIDIA':
            textColor = (0, 96, 0)
            x = gpu.column * gpuTextWidth + nvidiaXOffset + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)

            # 移动端背景底色
            if gpu.platform == 'Laptop':
                _, _, w, h = font.getbbox(gpu.name)
                draw.rectangle((x - 2, y, x + w + 1, y + h),
                               fill=NvidiaLaptopBackground)
            draw.text((x, y), gpu.name, font=font, fill=textColor)

        else:
            textColor = (220, 0, 0)
            x = gpu.column * gpuTextWidth + intelXOffset + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)
            draw.text((x, y), gpu.name, font=font, fill=textColor)

    font = font.font_variant(size=48)
    text = 'INTEL'
    _, _, w, h = font.getbbox(text)
    x, y = (nvidiaXOffset - w) / 2, (100 - h) / 2
    draw.text((x, y), text, font=font, fill='white')
    text = 'NVIDIA'
    _, _, w, h = font.getbbox(text)
    x, y = nvidiaXOffset + (centerOffset - nvidiaXOffset -
                                  w) / 2, (100 - h) / 2
    draw.text((intelXOffset + x, y), text, font=font, fill='white')
    text = 'AMD'
    _, _, w, h = font.getbbox(text)
    x, y = amdOffset + (imgWidth - amdOffset - w) / 2, (100 - h) / 2
    draw.text((intelXOffset + x, y), text, font=font, fill='white')

    y = imgHigh - 105
    font = font.font_variant(size=36)
    draw.text((25, y), title + '  Build ' + buildDateStr + ' ' + curVer, font=font, fill='white')
    
    font = font.font_variant(size=48)
    _, _, w, _ = font.getbbox(authorInfo)
    draw.text((imgWidth - w - 25, y), authorInfo, font=font, fill='white')

    font = font.font_variant(size=24)
    draw.text((25, y + 46),
              '基于3DMarkTimeSpy公开数据制作，以10000分为100%性能基准', 
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
    import download_3dmark
    download_3dmark.downloadAndParseHTML(sourcesUrl, dataSetPath)
    gpuInfoList = loadDataSet(dataSetPath)

    processData(gpuInfoList)

    draw('TimeSpy', gpuInfoList)
