"""
jark006
jark006@qq.com
"""

import numpy as np
import time
import cv2
import random
from PIL import ImageFont, ImageDraw, Image
from myutil import *

# pip install opencv-contrib-python numpy scipy matplotlib Pillow beautifulsoup4

isDebug = False
dataSource = "3DMark TimeSpy"
authorInfo = "Make by JARK006"
curVer = "V2.0"
picFormat = ".png"
buildDateStr = time.strftime("%Y%m%d", time.localtime())
sourcesUrl = "https://benchmarks.ul.com/zh-hans/compare/best-gpus"
sourcesUrlTopcpu = "https://www.topcpu.net/en/gpu-r/3dmark-time-spy"
dataSetPath = "data/3dmarkDataSet.csv"
isDrawQrcode = True
qrCodePath = "pic/qrcode2.png"
logoPath = "pic/3dmark.png"
benchNote = "基于3DMarkTimeSpy公开数据制作  以10000分为100%性能基准  部分GPU数据错得离谱  有空再勘误"

baiduyunShare = "https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg?pwd=etpt 提取码: etpt"
aliyunShare = "https://www.aliyundrive.com/s/jZUioTtYkKD"
allLinks = f"阿里盘 {aliyunShare}    百度盘 {baiduyunShare}"

# 霞鹜新晰黑  https://github.com/lxgw/LxgwNeoXiHei
# fontPath='LXGWNeoXiHei.ttf'
fontPath = "LXGWFasmartGothic.ttf"

# 在此添加 Geekbench 未收录的 GPU
addMore: list[gpuInfo] = [
    # gpuInfo('MX250 (25W)', 1200, 0, 'NVIDIA', 'MX', 'Laptop'),
    # gpuInfo('R9 Nano', 4690, 0, 'AMD', 'R9', 'Desktop'),
    # gpuInfo('RX 7900M', 19434, 0, 'AMD', 'RX7', 'Laptop'),
    # gpuInfo('RX 6850M XT 175W', 12674, 0, 'AMD', 'RX6', 'Laptop'),
    # gpuInfo('RX 6850M XT 140W', 11633, 0, 'AMD', 'RX6', 'Laptop'),
    # gpuInfo('RX 6550M', 4546, 0, 'AMD', 'RX6', 'Laptop'),
    # gpuInfo('RX 6500M', 4380, 0, 'AMD', 'RX6', 'Laptop'),
    # gpuInfo('RX 5500M', 4220, 0, 'AMD', 'RX5', 'Laptop'),
    # gpuInfo('Arc A550M', 5552, 0, 'Intel', 'Arc', 'Laptop'),
    # gpuInfo('Arc A370M', 3650, 0, 'Intel', 'Arc', 'Laptop'),
    # gpuInfo('Arc A350M', 2900, 0, 'Intel', 'Arc', 'Laptop'),
    # gpuInfo('Arc A310', 3270, 0, 'Intel', 'Arc', 'Desktop'),
]

# 修正分数
fixScore = {
    # 'RTX 4060 Ti 16 GB': 13473,
}

# 所有系列分成两列  各系列所在 第几列：
NvidiaColumn = {
    "RTX6": 6,
    "RTX5": 6,
    "RTX4": 5,
    "RTX3": 4,
    "RTXA": 0,
    "RTX2": 3,
    "RTX1": 2,
    "GTX16": 2,
    "GTX10": 6,
    "GTX9": 5,
    "GTX8": 4,
    "GTX7": 3,
    "GTX6": 2,
    "GT10": 6,
    "GT9": 5,
    "GT8": 4,
    "GT7": 3,
    "GT6": 2,
    "GT5": 6,
    "GT4": 5,
    "GT3": 4,
    "GT2": 3,
    "GT1": 2,
    "Titan": 0,
    "GeForce": 4,
    "Quadro": 1,
    "Tesla": 0,
    "MX": 0,
}

IntelColumn = {
    "Arc": 0,
    "UHD": 0,
    "HD": 0,
    "Iris": 0,
}

AMDColumn = {
    "RX9": 0,
    "RX7": 1,
    "RX6": 0,
    "RX5": 2,
    "RX500": 3,
    "RX4": 4,
    "R9": 0,
    "R7": 1,
    "R5": 2,
    "Vega": 1,
    "Radeon": 1,
    # 'FirePro': 5,
    # 'HD': 6,
    # 'Other': 7,
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
        if i.name not in setTmp:
            print("Add", i.name, i.score)
            gpuInfoList.append(i)
        else:
            print("Skip add", i.name, i.score)

    # 修正分数
    for gpu in gpuInfoList:
        if gpu.name in fixScore:
            print(
                "fixScore {}: {} to {}".format(gpu.name, gpu.score, fixScore[gpu.name])
            )
            gpu.score = fixScore[gpu.name]

    print("process Done")


def draw(gpuInfoList: list[gpuInfo]):
    global NvidiaColumn
    global IntelColumn
    global AMDColumn

    savePath = f"output/GPU性能天梯图3DMark_{buildDateStr}_{curVer}.png"

    baseScore = 10000
    title = f"{dataSource} GPU性能天梯图"
    watermarkText = title
    percentList = (
        [i for i in range(10, 30, 2)]
        + [i for i in range(30, 50, 5)]
        + [i for i in range(50, 100, 10)]
        + [i for i in range(100, 200, 20)]
        + [i for i in range(200, 510, 50)]
    )

    gpuInfoList = [gpu for gpu in gpuInfoList if gpu.score >= 1000]
    gpuInfoList = [
        gpu for gpu in gpuInfoList if gpu.series not in ["FirePro", "HD", "Other"]
    ]

    # 排序
    gpuInfoList.sort(key=lambda e: e.score, reverse=True)

    # 根据系列规划 GPU 所在的列位置
    for gpu in gpuInfoList:
        if gpu.vendor == "AMD":
            gpu.column = AMDColumn[gpu.series]
        elif gpu.vendor == "Intel":
            gpu.column = IntelColumn[gpu.series]
        else:
            gpu.column = NvidiaColumn[gpu.series]

    def score2high(score) -> int:
        return int(np.log(score) * 40)

    # 根据性能分数 计算 排名高度
    for gpu in gpuInfoList:
        gpu.rankingIndex = score2high(gpu.score)

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
        if gpu.vendor == "AMD":
            while (
                rankingIndex in AMDListSet[gpu.column]
            ):  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            gpu.rankingIndexFix = rankingIndex
            AMDListSet[gpu.column].add(rankingIndex)
        elif gpu.vendor == "Intel":
            while (
                rankingIndex in IntelListSet[gpu.column]
            ):  # 已存在的必定比当前的性能强，只能往下排
                rankingIndex -= 1
            gpu.rankingIndexFix = rankingIndex
            IntelListSet[gpu.column].add(rankingIndex)
        else:
            try:
                while (
                    rankingIndex in NvidiaListSet[gpu.column]
                ):  # 已存在的必定比当前的性能强，只能往下排
                    rankingIndex -= 1
                gpu.rankingIndexFix = rankingIndex
                NvidiaListSet[gpu.column].add(rankingIndex)
            except:
                print("Error", len(NvidiaListSet), gpu.column, gpu.name, gpu.series)
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
    leftEdgeWidth = int(20)  # 左右空白边缘宽度
    rightEdgeWidth = int(20)  # 左右空白边缘宽度
    centerWidth = int(120)  # 中间绘制百分比区域
    gpuTextHigh = int(12)
    gpuTextWidth = gpuTextHigh * 11
    imgHigh = (highMAX - highMIN + 1) * gpuTextHigh + upEdgeHigh + downEdgeHigh
    imgWidth = (
        (
            max(IntelColumn.values())
            + max(NvidiaColumn.values())
            + max(AMDColumn.values())
            + 3
        )
        * gpuTextWidth
        + centerWidth
        + leftEdgeWidth
    )

    intelXOffset = leftEdgeWidth
    nvidiaXOffset = intelXOffset + (max(IntelColumn.values()) + 1) * gpuTextWidth
    centerOffset = nvidiaXOffset + (max(NvidiaColumn.values()) + 1) * gpuTextWidth
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
                    (a * a[3] + b * (255 - a[3])) / 255, dtype=np.uint8
                )
        return pic.shape[1], pic.shape[0]

    if isDrawQrcode:
        w, h = addPic(img, logoPath, 10, 120)
        w, h = addPic(img, qrCodePath, 20 + w, 120)

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
                h = 3 * y - 8 * abs(x - (centerOffset + centerWidth / 2))
                h = ((h - (h % 200)) % imgHigh) / imgHigh
                draw.point((x, y), fill=HSL2BGR(h, 0.6, 0.80))

    # 中间百分比
    font = font.font_variant(size=24)
    for percent in percentList:
        text = f"{percent}%"
        _, _, w, _ = font.getbbox(text)
        x = centerOffset + (centerWidth - w) / 2
        high = score2high(percent * baseScore / 100) - highMIN + 2
        y = int(imgHigh - downEdgeHigh - high * gpuTextHigh)
        h = 3 * y / imgHigh + 0.75
        h = h - int(h)
        draw.text((x, y), text, font=font, fill=tuple(HSL2RGB(h, 1, 0.30)))

    # 绘制 gpu
    font = font.font_variant(size=gpuTextHigh)
    AMDLaptopBackground = (180, 200, 255)  # BGR
    NvidiaLaptopBackground = (160, 220, 200)
    IntelLaptopBackground = (220, 200, 200)
    for gpu in gpuInfoList:
        if len(gpu.name) > 18:
            gpu.name = gpu.name[:18]

        if gpu.vendor == "AMD":
            textColor = (0, 0, 220)
            x = amdOffset + gpu.column * gpuTextWidth + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)

            # AMD 移动端背景底色
            if gpu.platform == "Laptop":
                _, _, w, h = font.getbbox(gpu.name)
                draw.rectangle((x - 2, y, x + w + 1, y + h), fill=AMDLaptopBackground)

            draw.text((x, y), gpu.name, font=font, fill=textColor)

        elif gpu.vendor == "NVIDIA":
            textColor = (0, 96, 0)
            x = gpu.column * gpuTextWidth + nvidiaXOffset + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)

            # 移动端背景底色
            if gpu.platform == "Laptop":
                _, _, w, h = font.getbbox(gpu.name)
                draw.rectangle(
                    (x - 2, y, x + w + 1, y + h), fill=NvidiaLaptopBackground
                )
            draw.text((x, y), gpu.name, font=font, fill=textColor)

        else:
            textColor = (220, 0, 0)
            x = gpu.column * gpuTextWidth + intelXOffset + 5
            y = int(imgHigh - downEdgeHigh - gpu.rankingIndexFix * gpuTextHigh)
            # if gpu.rankingIndex != gpu.rankingIndexFix:  # 修正位置时，被迫下降的高度
            #     gpu.name=gpu.name+' ^'+str(gpu.rankingIndex - gpu.rankingIndexFix)

            if gpu.platform == "Laptop":
                _, _, w, h = font.getbbox(gpu.name)
                draw.rectangle((x - 2, y, x + w + 1, y + h), fill=IntelLaptopBackground)
            draw.text((x, y), gpu.name, font=font, fill=textColor)

            draw.text((x, y), gpu.name, font=font, fill=textColor)

    font = font.font_variant(size=48)
    text = "INTEL"
    _, _, w, h = font.getbbox(text)
    x, y = (nvidiaXOffset - w) / 2, (100 - h) / 2
    draw.text((x, y), text, font=font, fill="white")
    text = "NVIDIA"
    _, _, w, h = font.getbbox(text)
    x, y = nvidiaXOffset + (centerOffset - nvidiaXOffset - w) / 2, (100 - h) / 2
    draw.text((intelXOffset + x, y), text, font=font, fill="white")
    text = "AMD"
    _, _, w, h = font.getbbox(text)
    x, y = amdOffset + (imgWidth - amdOffset - w) / 2, (100 - h) / 2
    draw.text((intelXOffset + x, y), text, font=font, fill="white")

    y = imgHigh - 105
    font = font.font_variant(size=36)
    draw.text(
        (25, y),
        f"{title}  Build {buildDateStr} {curVer}",
        font=font,
        fill="white",
    )

    font = font.font_variant(size=56)
    _, _, box_w, box_h = font.getbbox(authorInfo)
    draw.text(
        (imgWidth - box_w - 25, imgHigh - (box_h + downEdgeHigh) / 2),
        authorInfo,
        font=font,
        fill="white",
    )

    font = font.font_variant(size=20)
    draw.text((25, y + 46), benchNote, font=font, fill="white")
    draw.text((25, y + 72), allLinks, font=font, fill="white")

    # 基本绘制完成， 转回 cv 格式
    img = np.array(imgPil)

    # debug 模式
    if isDebug:
        img = np.array(imgPil)
        cv2.imencode(picFormat, img)[1].tofile(savePath)
        print("Debug Mode")
        print(f"{title} is done.")
        return

    # 绘制水印层
    font = font.font_variant(size=24)
    text = f"{watermarkText}\nBuild {buildDateStr} {curVer}    {authorInfo}\n{baiduyunShare}\n{aliyunShare}"
    _, _, w, h = font.getbbox(text)
    size = 2 * max(imgHigh, imgWidth)
    watermaskImg = np.zeros((size, size, 4), np.uint8)
    watermaskImg[:, :] = (0, 0, 0, 1)
    watermaskImgPil = Image.fromarray(watermaskImg)
    draw = ImageDraw.Draw(watermaskImgPil)
    for y in range(15, size, int(8 * h)):
        for x in range(15, size, int(0.4 * w)):
            draw.text(
                (x + random.randint(0, 20), y + random.randint(0, 20)),
                text,
                font=font,
                fill=HSL2RGB(0.2 + random.random() * 0.2, 1, 0.4),
            )

    watermaskImg = np.array(watermaskImgPil)
    matRotate = cv2.getRotationMatrix2D(
        (size / 2, size / 2), 45, 1
    )  # center, angle, scale
    watermaskImg = cv2.warpAffine(watermaskImg, matRotate, (size, size))
    xStart, yStart = int((size - imgHigh) / 2), int((size - imgWidth) / 2)
    watermaskImg = watermaskImg[yStart : yStart + imgHigh, xStart : xStart + imgWidth]

    img = cv2.addWeighted(img, 1, watermaskImg, 0.1, 0)  # 叠加水印层

    # 保存图片
    cv2.imencode(picFormat, img)[1].tofile(savePath)

    print(f"{title} is done.")
    print(f"Path: {savePath}")


if __name__ == "__main__":
    import download_3dmark_topcpu

    download_3dmark_topcpu.downloadAndParseHTML(sourcesUrlTopcpu, dataSetPath)
    gpuInfoList = load_GPU_DataSet(dataSetPath)
    processData(gpuInfoList)
    draw(gpuInfoList)
