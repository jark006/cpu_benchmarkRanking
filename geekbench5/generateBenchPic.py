'''
 jark006
 date： 2020-6-13 03:19:41
 jark006@qq.com

 Explanation:
    First step, run 'download_data.py' download cpu bench date from geekbench.com,
        it will parsing data and save to file 'all_list.txt'
    And then run this script, load 'all_list' and make it to a chart file.
'''

import numpy as np
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import ptp
from scipy.optimize import curve_fit
import time
import cv2
from PIL import ImageFont, ImageDraw, Image
from download_data import Node
import math
import random

buildType = 'debugA'
coreType = 'single'
dataSource = r'Geekbench5'
datalink = r'https://browser.geekbench.com/processor-benchmarks'
authorInfo = r' 贴吧ID:泛感思杰 '
link = r'https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg  提取码：etpt'

fontFile = r'c:\windows\fonts\msyh.ttc'
fontFilebd = r'c:\windows\fonts\msyhbd.ttc'


if coreType == 'single':
    bench_version = r'Beta V0.7'
    baseScore = 500
    parameter = [ 2.24473411e+03, -9.66584721e+02,  1.22222273e+00]  # geekbench single
    title = dataSource+'单核性能天梯图'
    watermarkText = title + ' Single-Core ' + authorInfo
    logoPath = 'logos.png'
    listPath = 'single_list.txt'
    percent = [x for x in range(30, 341, 5)]
    
    intel_dict2 = {'i3': 3, 'i5': 1, 'i7': 2, 'i9': 3,
                'Core2': 0, 'Pentium': 0, 'Celeron': 0, 
                'Atom': 2, 'Atom2': 1,}

    intel_dict = {'i3': 3, 'i5': 1, 'i7': 2, 'i9': 3, 'E5': 4, 'Xeon': 5,
                'Core2': 3, 'Core22': 4,
                'Pentium': 0, 'Pentium2': 1, 
                'Celeron': 0, 'Celeron2': 2,
                }  # core2系列太多，为避免堆积，分成两拨

    amd_dict = {'EPYC': 0, 'TR': 0, 'R9': 1, 'R7': 2, 'R5': 3, 'R3': 3,
                'Bulldozer': 0, 'APU': 1, 'Phenom': 2, 'Athlon': 3, 'Turion': 0}
    # 修正分数
    fix_score = {
        # 'i9-10900K': 1420,

    }

    more = [
        # Node('AMD', 'R9', 'R9 3900XT', 1350, 'desktop'),
        # Node('AMD', 'R7', 'R7 3800XT', 1340, 'desktop'),
        # Node('AMD', 'R5', 'R5 3600XT', 1300, 'desktop'),
    ]
else:  # multiCore
    bench_version = r'Beta V0.7'
    baseScore = 1000
    parameter = [1.40299769e+03, - 1.79848915e+03, - 8.62352477e-01] # geekbench multi
    title = dataSource+'多核性能天梯图'
    watermarkText = title+' Multi-Core '+authorInfo
    logoPath = 'logom.png'
    listPath = 'multi_list.txt'

    percent = [
        40, 45, 50, 55, 60, 65,
        70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130,
        135, 140, 145, 150, 155, 160, 170, 180, 190, 200, 210, 220,
        230, 240, 250, 260, 270, 280, 290, 300, 320, 340, 360, 380,
        400, 430, 460, 490, 520, 560, 600, 650, 700, 750, 800, 850,
        900, 1000, 1100, 1200, 1400, 1700, 2000, 2200, 2400
    ]
    intel_dict2 = {'i3': 0, 'i5': 2, 'i7': 1, 'i9': 2,
                'Atom': 2,'Atom2': 1,
               'Core2': 0, 'Pentium': 2, 'Celeron': 1}

    intel_dict = {'i3': 0, 'i5': 2, 'i7': 1, 'E5': 3, 'i9': 2, 'Xeon': 4,
                'Core2': 3, 'Core22': 4, 'Pentium': 2, 'Pentium2': 2, 
                'Celeron': 1, 'Celeron2': 0}  # core2系列太多，为避免堆积，分成两拨

    amd_dict = {'EPYC': 0, 'TR': 0, 'R9': 1, 'R7': 2, 'R5': 3, 'R3': 1, 'Bulldozer': 0,
                'APU': 1, 'Phenom': 2, 'Athlon': 3, 'Turion': 0}
    # 修正分数
    fix_score = {
        # 'W-3175X': 20500,
        # 'i9-9980XE': 15400,
        # 'i9-7980XE': 15200,
        # 'i9-9920X': 12400,

        # 'TR 2950X': 13500,
        # 'TR 2970WX': 16000,
        # 'TR 2990WX': 18000,
    }
    # # block list
    # blocklist = [
    #     'i5 750S',
    #     'i5 E 520',
    #     'FX-74',
    #
    # ]

    more = [
        # Node('AMD', 'R9', 'R9 3900XT', 13700, 'desktop'),
        # Node('AMD', 'R7', 'R7 3800XT',  9700, 'desktop'),
        # Node('AMD', 'R5', 'R5 3600XT',  7400, 'desktop'),
    ]

build_date = time.strftime("%Y%m%d", time.localtime())
pic_path = '../'+title + build_date + bench_version + '.png'



# 效果不错
def func(x, a, b, c):
    return a * np.exp2(b / x) + c


def fit(x, y):
    popt, pcov = curve_fit(func, x, y)
    print(popt)
    a = popt[0]  # popt里面是拟合系数
    b = popt[1]
    c = popt[2]
    y1 = [func(i, a, b, c) for i in x]

    plt.plot(x, y, '.', label='original values')
    plt.plot(x, y1, 'r', label='y1')
    plt.xlabel('CPU score')
    plt.ylabel('High')
    plt.legend(loc=4)  # 指定legend的位置
    plt.title('curve_fit')
    plt.savefig('all' + str(time.time()) + '.png')
    plt.show()


def readlist(path):
    boollist = [True, True, True, True, True, True, ]
    f = open(path, 'r')
    cnt = int(f.readline())
    ll = []
    for a in range(0, cnt):
        vendor = f.readline().strip('\r').strip('\n')
        series = f.readline().strip('\r').strip('\n')
        name = f.readline().strip('\r').strip('\n')
        score = int(f.readline().strip('\r').strip('\n'))
        platform  = f.readline().strip('\r').strip('\n')

        if platform == 'laptop':
            if series == 'Atom' and score<baseScore*0.8:
                if (boollist[0]):
                    boollist[0] = not boollist[0]
                    series = 'Atom2'
        else:  # desktop
            if series == 'Core2' and score<baseScore*0.8:
                boollist[1] = not boollist[1]
                if (boollist[1]):
                    series = 'Core22'

            if coreType == 'single':
                if series == 'Celeron' and score<baseScore*0.8:
                    boollist[2] = not boollist[2]
                    if (boollist[2]):
                        series = 'Celeron2'
                if series == 'Pentium' and score<baseScore*0.8:
                    boollist[3] = not boollist[3]
                    if (boollist[3]):
                        series = 'Pentium2'
            else:  # multiCore
                if series == 'Celeron' and score<baseScore*0.8:
                    boollist[4] = not boollist[4]
                    if (boollist[4]):
                        series = 'Celeron2'
                if series == 'Pentium' and score<baseScore*0.8 and len(name)<6:
                    boollist[5] = not boollist[5]
                    if (boollist[5]):
                        series = 'Pentium2'

        
        ll.append(Node(vendor, series, name, score, platform))
    f.close()
    return ll


def score2high(x):
    # y= a*np.exp(b/x)+c
    p = parameter
    a = p[0]
    b = p[1]
    c = p[2]
    res = a * np.exp(b / x) + c
    return int(res * 0.5)


def HSL2RGB(h, s, l):
    u"HSL -> RGB，返回一个元组，格式为：(r, g, b)"
    if s > 0:
        v_1_3 = 1.0 / 3
        v_1_6 = 1.0 / 6
        v_2_3 = 2.0 / 3

        q = l * (1 + s) if l < 0.5 else l + s - (l * s)
        p = l * 2 - q
        hk = h / 360.0  # h 规范化到值域 [0, 1) 内
        tr = hk + v_1_3
        tg = hk
        tb = hk - v_1_3
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
    # s == 0 的情况
    else:
        rgb = l, l, l
    return rgb
def HSL2BGR(h, s, l):
    # "HSL -> BGR，返回一个元组，格式为：(r, g, b)"
    if s > 0:
        v_1_3 = 1.0 / 3
        v_1_6 = 1.0 / 6
        v_2_3 = 2.0 / 3

        q = l * (1 + s) if l < 0.5 else l + s - (l * s)
        p = l * 2 - q
        hk = h / 360.0  # h 规范化到值域 [0, 1) 内
        tb = hk + v_1_3
        tg = hk
        tr = hk - v_1_3
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
    # s == 0 的情况
    else:
        rgb = l, l, l
    return rgb


all_list = readlist(listPath)
intel_list = []  # 桌面平台
intel_list2 = []  # 移动平台
amd_list = []

# 拟合分数，将分数尽可能线性平均分布
# y = [i for i in range(50, len(all_list)+50)]
# x = [y.score for y in all_list]
# x.sort()
# fit(x, y)
# exit()

# y = [i for i in range(60, len(all_list)+70)]  # 前加10个
# x = [y.score for y in all_list]
# x.sort()
# k = 10/(x[9]-x[0])
# b = 60 - k*x[0]
# l = []
# for i in range(50, 60):
#     print((i-b)/k)
#     l.append((i-b)/k)
# x = l+x
# fit(x, y)
# exit()


for i in more:
    print('Add '+i.name+':'+str(i.score))
    all_list.append(i)


all_list.sort(key=lambda e: e.score)


for n in all_list:

    # # 移除名单
    # if n.name in blocklist:
    #     print('Remove:' + n.name)
    #     continue
    #
    # 修正分数
    if fix_score.__contains__(n.name):
        scoreBefore = n.score
        n.score = fix_score[n.name]
        print('Fix {}: {} to {}'.format(n.name, scoreBefore, n.score))

    n.high = (score2high(n.score))

    if n.vendor == 'Intel':
        if n.platform == 'desktop':
            intel_list.append(n)
        else:
            intel_list2.append(n)
    else:
        amd_list.append(n)

print('Intel_list len:{}'.format(len(intel_list)))
print('Intel_list2 len:{}'.format(len(intel_list2)))
print('AMD_list len:{}'.format(len(amd_list)))

# print(se)
# print(se2)
# exit()

# intel 移动端 高度修正
sslist2 = []
for i in range(0, len(intel_dict2)):
    sslist2.append(set())  # 移动端
for n in intel_list2:
    h = int(n.high)
    while h in sslist2[int(intel_dict2[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist2[int(intel_dict2[n.series])].add(h)

# intel 高度修正
sslist = []
for i in range(0, len(intel_dict)):
    sslist.append(set())  # 桌面端
for n in intel_list:
    h = int(n.high)
    while h in sslist[int(intel_dict[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist[int(intel_dict[n.series])].add(h)

# amd 高度修正
sslist = []
for i in range(0, len(amd_dict)):
    sslist.append(set())

for n in amd_list:
    h = int(n.high)
    while h in sslist[int(amd_dict[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist[int(amd_dict[n.series])].add(h)


highMAX = 100
highMIN = 100

for n in intel_list2:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix

for n in intel_list:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix

for n in amd_list:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix


for n in intel_list2:
    n.highFix -= highMIN-2
for n in intel_list:
    n.highFix -= highMIN-2
for n in amd_list:
    n.highFix -= highMIN-2

highMAX += 4


# all unit is pexil
upEdgeHigh = 100  # 顶部边缘高度
downEdgeHigh = 100  # 底部边缘高度
edgeWidth = 20  # 左右空白边缘宽度
centerWidth = int(120)  # 中间绘制百分比区域
seriesWidth = int(120)
seriesWidth_amd = int(seriesWidth * 1)
textHigh = int(16)
imgHigh = int((highMAX - highMIN+1) * textHigh) + upEdgeHigh + downEdgeHigh
imgWidth = ((max(intel_dict.values()) + max(intel_dict2.values()) + 2) * int(seriesWidth)) \
           + (max(amd_dict.values()) + 1) * seriesWidth_amd + centerWidth + edgeWidth * 2

intelOffset2 = edgeWidth
intelOffset = intelOffset2 + (max(intel_dict2.values()) + 1) * seriesWidth
centerOffset = intelOffset + (max(intel_dict.values()) + 1) * seriesWidth
amdOffset = centerOffset + centerWidth

# img[i][j] = (B, G, R, A) # A 透明度 0全透明 0xff不透明
img = np.zeros((imgHigh, imgWidth, 4), np.uint8)

# img[:, :] = (230, 230, 230, 255)  # 微灰

img[:, 0:intelOffset] = (230, 230, 255, 255)
img[:, intelOffset:centerOffset] = (220, 220, 255, 255)
img[:, centerOffset:amdOffset] = (230, 230, 230, 255)
img[:, amdOffset:] = (255, 230, 230, 255)

# title
img[:upEdgeHigh, :intelOffset] = (0, 180, 255, 255)
img[:upEdgeHigh, intelOffset:centerOffset] = (0, 150, 255, 255)
# img[:100, centerOffset:amdOffset] = (100, 255, 100, 255)
img[:upEdgeHigh, amdOffset:] = (230, 0, 30, 255)

# bottom
img[-downEdgeHigh:, :] = (255, 127, 39, 255)

img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
logo = cv2.imread('qr2.png', cv2.IMREAD_UNCHANGED)
xOffset, yOffset = 30, 230
for x in range(0, logo.shape[0]):
    for y in range(0, logo.shape[1]):
        a = np.array(logo[x, y], dtype=int)
        b = np.array(img[yOffset+x, xOffset+y], dtype=int)
        t = (a*a[3] + b*(255-a[3]))/255
        t = np.array(t, dtype=np.uint8)
        img[yOffset + x, xOffset + y] = t


logo = cv2.imread(logoPath, cv2.IMREAD_UNCHANGED)
xOffset2, yOffset2 = xOffset+180, yOffset
for x in range(0, logo.shape[0]):
    for y in range(0, logo.shape[1]):
        a = np.array(logo[x, y], dtype=int)
        b = np.array(img[yOffset2+x, xOffset2+y], dtype=int)
        t = (a*a[3] + b*(255-a[3]))/255
        t = np.array(t, dtype=np.uint8)
        img[yOffset2 + x, xOffset2 + y] = t


img_pil = Image.fromarray(img)
draw = ImageDraw.Draw(img_pil)

font = ImageFont.truetype(fontFilebd, size=32)
draw.text((xOffset, yOffset+logo.shape[0]), '100%性能基准分:'+str(baseScore), font=font, fill='black')

# 绘制中间百分比
textColor = (0, 0, 0)
percentHigh = [score2high(i / 100 * baseScore)-highMIN+2 for i in percent]

# 中间彩条
if buildType != 'debug':
    for y in range(0, imgHigh):
        for x in range(centerOffset + 8, amdOffset - 8):
            h = (int((1080 * y / imgHigh) + 360 - math.fabs(x - (centerOffset + centerWidth / 2)))&0xfff0) % 360
            draw.point((x, y), fill=tuple(HSL2BGR(h, 0.6, 0.8)))

# 中间百分比
font = ImageFont.truetype(fontFilebd, size=24)
for index, high in enumerate(percentHigh):
    t = '%3d%%' % (percent[index])
    x = centerOffset + 20
    y = int(imgHigh - downEdgeHigh - high * textHigh)
    h = ((1080 * y / imgHigh) + 270) % 360
    draw.text((x, y), t, font=font, fill=tuple(HSL2RGB(h, 0.9, 0.35)))


font = ImageFont.truetype(fontFile, size=16)
textColor = (220, 0, 0)
for n in intel_list2:
    x = int(intel_dict2[n.series]) * seriesWidth + intelOffset2 + 5
    y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
    draw.text((x, y), n.name, font=font, fill=textColor)

for n in intel_list:
    x = (int(intel_dict[n.series])) * seriesWidth + intelOffset + 5
    y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
    draw.text((x, y), n.name, font=font, fill=textColor)

textColor = (0, 0, 220)
text_bg = (180, 200, 255)
for n in amd_list:
    x = amdOffset + int(amd_dict[n.series]) * seriesWidth_amd + 5
    y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)

    # 文字背景
    if n.platform == 'laptop':
        w, h = font.getsize(n.name)
        draw.rectangle((x - 2, y+2, x + w + 2, y + h), fill=text_bg)

    draw.text((x, y), n.name, font=font, fill=textColor)



font = ImageFont.truetype(fontFilebd, size=30)
text = 'Intel Mobile'
w, h = font.getsize(text)
x, y = (intelOffset-w)/2, (100-h)/2
draw.text((x, y), text, font=font, fill='white')
text = 'Intel Desktop & Server'
w, h = font.getsize(text)
x, y = intelOffset+(centerOffset-intelOffset-w)/2, (100-h)/2
draw.text((intelOffset2 + x, y), text, font=font, fill='white')
text = 'AMD All Series'
w, h = font.getsize(text)
x, y = amdOffset+(imgWidth-amdOffset-w)/2, (100-h)/2
draw.text((intelOffset2 + x, y), text, font=font, fill='white')




x, y = 50, imgHigh - 85
draw.text((50, y), title, font=font, fill='white')
draw.text((x + amdOffset, y), 'Build ' + build_date + '  ' + bench_version, font=font, fill='white')

font = ImageFont.truetype(fontFile, size=25)
draw.text((50, y + 40), r'主要数据来源:'+datalink, font=font, fill='white')
draw.text((x + amdOffset, y + 45), authorInfo, font=font, fill='white')




# debug 模式
if buildType == 'debug':
    img = np.array(img_pil)

    cv2.imencode('.png', img)[1].tofile(pic_path)
    print('Debug Mode:')
    print(title+' is done.')
    exit()


# # 绘制错误提示水印
# tips  = '征集意见版,该版本数据错误较多'
# font = ImageFont.truetype(fontFile, size=50)
# w, h = font.getsize(tips)
# watermask = np.zeros((imgHigh, imgHigh, 4), np.uint8)
# watermask_pil = Image.fromarray(watermask)
# draw = ImageDraw.Draw(watermask_pil)
# x, y=30, 30
# while y < imgHigh:
#     while x < imgHigh:
#         draw.text((x, y), tips, font=font, fill='white')
# #        cv2.putText(watermask, authorInfo+link, (x, y), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255, 255, 40), 2)
#         x += int(1.5*w)
#     x = 30
#     y += 5*h

# 绘制水印层
font = ImageFont.truetype(fontFile, size=30)
w, h = font.getsize(link)
watermask = np.zeros((imgHigh, imgHigh, 4), np.uint8)
watermask[:, :] = (0, 0, 0, 1)
watermask_pil = Image.fromarray(watermask)
draw = ImageDraw.Draw(watermask_pil)
x, y = 30, 30
while y < imgHigh:
    while x < imgHigh:
        draw.text((x, y), watermarkText, font=font, fill='white')
        draw.text((x, y + h), link, font=font, fill='white')
        x += int(1.6 * w)
    x = 30
    y += 10 * h

# 水印层旋转加裁切
watermask = np.array(watermask_pil)
matRotate = cv2.getRotationMatrix2D((imgHigh * 0.5, imgHigh * 0.5), 45, 1)  # mat rotate 1 center 2 angle 3 缩放系数
watermask = cv2.warpAffine(watermask, matRotate, (imgHigh, imgHigh))
w = int((imgHigh - imgWidth) / 2)
watermask = watermask[:, w:w + imgWidth]
watermask = cv2.resize(watermask, (imgWidth, imgHigh), interpolation=cv2.INTER_AREA)

img = np.array(img_pil)
img = cv2.addWeighted(img, 1, watermask, 0.08, 0)  # 叠加水印层



# 错误提示水印
# img_add = cv2.addWeighted(img, 1, watermask, 0.2, 0)


# 保存图片
# cv2.imwrite(pic_path, img)
cv2.imencode('.png', img)[1].tofile(pic_path)

print(title+' is done.')

