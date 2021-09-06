'''
 jark006
 date： 2021-4-28
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
from myutil import *
import math

buildType = 'debugA'
coreType = 'single'
dataSource = r'Geekbench5'
datalink = r'https://browser.geekbench.com/processor-benchmarks'
authorInfo = r'贴吧ID:泛感思杰  jark006@qq.com'
link = r'https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg  提取码：etpt'

fontFile = r'c:\windows\fonts\msyh.ttc'
fontFilebd = r'c:\windows\fonts\msyhbd.ttc'
highScale = 0.2 #高度比例
pic_format = '.png'
bench_version = r'V1.0'

if coreType == 'single':
    baseScore = 500
    parameter = [ 2.24473411e+03, -9.66584721e+02,  1.22222273e+00]  # geekbench single
    title = dataSource+'单核性能天梯图'
    watermarkText = title + ' Single-Core'
    logoPath = r'pic/logoGB5s.png'
    listPath = r'data/gb5_single_list.txt'
    percent = [x for x in range(40, 381, 10)]
    
    # 所有系列分成两列
    intel_Column_mobile = {
        'i3': 0, 'i5': 2, 'i7': 4, 'i9': 4,'Core2': 1, 'Pentium': 0, 'Celeron': 2, 'Atom': 4,
        'i32': 1, 'i52': 3, 'i72': 5, 'i92': 5,'Core22': 1, 'Pentium2': 1, 'Celeron2': 3, 'Atom2': 5,
        }

    intel_Column_desktop = {
        'i3': 4, 'i5': 6, 'i7': 8, 'i9': 10, 'E5': 0, 'Xeon': 2,'Core2': 6, 'Pentium': 10, 'Celeron': 8,
        'i32': 5, 'i52': 7, 'i72': 9, 'i92': 11, 'E52': 1, 'Xeon2': 3,'Core22': 7, 'Pentium2': 11, 'Celeron2': 9,
    }

    amd_Column = {
        'EPYC': 0, 'TR': 0, 'R9': 0, 'R7': 1, 'R5': 2, 'R3': 3,'Bulldozer': 0, 'APU': 1, 'Phenom': 3, 'Athlon': 5, 'Turion': 0,
        'EPYC2': 0, 'TR2': 0, 'R92': 0, 'R72': 1, 'R52': 2, 'R32': 3,'Bulldozer2': 0, 'APU2': 2, 'Phenom2': 4, 'Athlon2': 6, 'Turion2': 0,
        }
    # 修正分数
    fix_score = {
        # 'i9-10900K': 1420,
    }
    more = [
        # Node('AMD', 'R9', 'R9 3900XT', 1350, 'desktop'),
    ]
else:  # multiCore
    baseScore = 1000
    parameter = [1.40299769e+03, - 1.79848915e+03, - 8.62352477e-01] # geekbench multi
    title = dataSource+'多核性能天梯图'
    watermarkText = title+' Multi-Core'
    logoPath = r'pic/logoGB5m.png'
    listPath = r'data/gb5_multi_list.txt'
    percent = [
        40,  50,  60, 70,  80,  90,  100,  110,  120, 130, 140, 150, 160, 170, 180, 190, 200,
        220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 450, 500, 550, 600, 650, 700, 750, 800,
        900, 1000, 1200, 1400, 1600, 2000, 2500, 3000
    ]

    # 所有系列分成两列
    intel_Column_mobile = {
        'i3': 4, 'i5': 0, 'i7': 2, 'i9': 4, 'Atom': 0, 'Core2': 0, 'Pentium': 2, 'Celeron': 2,
        'i32': 5, 'i52': 1, 'i72': 3, 'i92': 5, 'Atom2': 1, 'Core22': 1, 'Pentium2': 3, 'Celeron2': 3,
    }

    intel_Column_desktop = {
        'E5': 0, 'Xeon': 2,'i3': 8, 'i5': 4, 'i7': 6, 'i9': 8, 'Core2': 4,  'Pentium': 6,  'Celeron': 8, 
        'E52': 1, 'Xeon2': 3,'i32': 9, 'i52': 5, 'i72': 7, 'i92': 9, 'Core22': 5,  'Pentium2': 7,  'Celeron2': 9, 
    }

    amd_Column = {
        'EPYC': 0, 'TR': 0, 'R9': 1, 'R7': 1, 'R5': 3, 'R3': 5, 'Bulldozer': 0,'APU': 1, 'Phenom': 3, 'Athlon': 5, 'Turion': 0,
        'EPYC2': 0, 'TR2': 0, 'R92': 2, 'R72': 2, 'R52': 4, 'R32': 6, 'Bulldozer2': 0,'APU2': 2, 'Phenom2': 4, 'Athlon2': 6, 'Turion2': 0,
    }

    # 修正分数
    fix_score = {
        # 'i9-9980XE': 15400,
    }
    more = [
        # Node('AMD', 'R9', 'R9 3900XT', 13700, 'desktop'),
    ]

build_date = time.strftime("%Y%m%d", time.localtime())
pic_path = 'output/'+title + build_date + bench_version+pic_format



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
    plt.savefig(dataSource+('single' if coreType=='single' else 'multi') + str(int(time.time())) + '.png')
    plt.show()


def readlist(path):
    boollist = {'i3': True, 'i5': True, 'i7': True, 'i9': True, 'E5': True, 'Xeon': True,
                'Core2': True,  'Pentium': True,'Celeron': True, 'Atom':True,
                'EPYC': True, 'TR': True, 'R9': True, 'R7': True, 'R5': True, 'R3': True, 
                'Bulldozer': True, 'APU': True, 'Phenom': True, 'Athlon': True, 'Turion': True,
                }
    f = open(path, 'r')
    cnt = int(f.readline())
    ll = []
    for a in range(0, cnt):
        vendor = f.readline().strip('\r').strip('\n')
        series = f.readline().strip('\r').strip('\n')
        name = f.readline().strip('\r').strip('\n')
        score = int(f.readline().strip('\r').strip('\n'))
        platform  = f.readline().strip('\r').strip('\n')

        boollist[series] = not boollist[series]
        if (boollist[series]):
            series = series+'2'
        ll.append(Node(vendor, series, name, score, platform))
    f.close()
    return ll


def score2high(p, x, highScale):
    # y= a*np.exp(b/x)+c
    a = p[0]
    b = p[1]
    c = p[2]
    res = a * np.exp(b / x) + c
    return int(res*highScale)

all_list = readlist(listPath)
intel_desktop = []  # 桌面平台
intel_mobile = []  # 移动平台
amd_all = []

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

    n.high = int(score2high(parameter, n.score, highScale))

    if n.vendor == 'Intel':
        if n.platform == 'desktop':
            intel_desktop.append(n)
        else:
            intel_mobile.append(n)
    else:
        amd_all.append(n)

print('Intel_desktop len:{}'.format(len(intel_desktop)))
print('Intel_mobile len:{}'.format(len(intel_mobile)))
print('AMD_all len:{}'.format(len(amd_all)))

# print(se)
# print(se2)
# exit()

# intel 移动端 高度修正
sslist2 = []
for i in range(0, len(intel_Column_mobile)):
    sslist2.append(set())  # 移动端
for n in intel_mobile:
    h = int(n.high)
    while h in sslist2[int(intel_Column_mobile[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist2[int(intel_Column_mobile[n.series])].add(h)

# intel 高度修正
sslist = []
for i in range(0, len(intel_Column_desktop)):
    sslist.append(set())  # 桌面端
for n in intel_desktop:
    h = int(n.high)
    while h in sslist[int(intel_Column_desktop[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist[int(intel_Column_desktop[n.series])].add(h)

# amd 高度修正
sslist = []
for i in range(0, len(amd_Column)):
    sslist.append(set())

for n in amd_all:
    h = int(n.high)
    while h in sslist[int(amd_Column[n.series])]:  # 已存在的必定比当前的性能强，只能往下排
        h -= 1
    n.highFix = h
    sslist[int(amd_Column[n.series])].add(h)


highMAX = 100
highMIN = 100

for n in intel_mobile:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix

for n in intel_desktop:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix

for n in amd_all:
    if n.highFix < highMIN:
        highMIN = n.highFix
    if n.highFix > highMAX:
        highMAX = n.highFix


for n in intel_mobile:
    n.highFix -= highMIN-2
for n in intel_desktop:
    n.highFix -= highMIN-2
for n in amd_all:
    n.highFix -= highMIN-2

highMAX += 4


# all unit is pexil
upEdgeHigh = 100  # 顶部边缘高度
downEdgeHigh = 100  # 底部边缘高度
edgeWidth = 20  # 左右空白边缘宽度
textHigh = int(10)
centerWidth = int(120)  # 中间绘制百分比区域
seriesWidth = int(textHigh*8)
seriesWidth_amd = int(seriesWidth * 1)
imgHigh = int((highMAX - highMIN+1) * textHigh) + upEdgeHigh + downEdgeHigh
imgWidth = int(((max(intel_Column_desktop.values()) + max(intel_Column_mobile.values()) + 2) * int(seriesWidth)) \
           + (max(amd_Column.values()) + 1) * seriesWidth_amd + centerWidth + edgeWidth * 2)

intelOffset2 = edgeWidth
intelOffset = int(intelOffset2 + (max(intel_Column_mobile.values()) + 1) * seriesWidth)
centerOffset = int(intelOffset + (max(intel_Column_desktop.values()) + 1) * seriesWidth)
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
logo = cv2.imread('pic/qrcode.png', cv2.IMREAD_UNCHANGED)
xOffset, yOffset = 30, 100
for x in range(0, logo.shape[0]):
    for y in range(0, logo.shape[1]):
        a = np.array(logo[x, y], dtype=int)
        b = np.array(img[yOffset+x, xOffset+y], dtype=int)
        t = (a*a[3] + b*(255-a[3]))/255
        t = np.array(t, dtype=np.uint8)
        img[yOffset + x, xOffset + y] = t


logo = cv2.imread(logoPath, cv2.IMREAD_UNCHANGED)
xOffset2, yOffset2 = imgWidth-180, yOffset
for x in range(0, logo.shape[0]):
    for y in range(0, logo.shape[1]):
        a = np.array(logo[x, y], dtype=int)
        b = np.array(img[yOffset2+x, xOffset2+y], dtype=int)
        t = (a*a[3] + b*(255-a[3]))/255
        t = np.array(t, dtype=np.uint8)
        img[yOffset2 + x, xOffset2 + y] = t


img_pil = Image.fromarray(img)
draw = ImageDraw.Draw(img_pil)

font = ImageFont.truetype(fontFilebd, size=28)
draw.text((xOffset, yOffset+logo.shape[0]+20), '100%性能基准分:'+str(baseScore), font=font, fill='black')

# 绘制中间百分比
textColor = (0, 0, 0)
percentHigh = [score2high(parameter,i / 100 * baseScore, highScale)-highMIN+2 for i in percent]

# 中间彩条
if buildType != 'debug':
    for y in range(0, imgHigh):
        for x in range(centerOffset + 8, amdOffset - 8):
            h = (int((720 * y / imgHigh) + 360 - abs(x - (centerOffset + centerWidth / 2)))&0xfff0) % 360
            draw.point((x, y), fill=tuple(HSL2BGR(h, 0.6, 0.8)))

# 中间百分比
font = ImageFont.truetype(fontFilebd, size=24)
for index, high in enumerate(percentHigh):
    t = '%3d%%' % (percent[index])
    x = centerOffset + 20
    y = int(imgHigh - downEdgeHigh - high * textHigh)
    h = ((720 * y / imgHigh) + 270) % 360
    draw.text((x, y), t, font=font, fill=tuple(HSL2RGB(h, 0.9, 0.35)))


font = ImageFont.truetype(fontFile, size=textHigh)
textColor = (220, 0, 0)
for n in intel_mobile:
    x = int(intel_Column_mobile[n.series]) * seriesWidth + intelOffset2 + 5
    y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
    draw.text((x, y), n.name, font=font, fill=textColor)

for n in intel_desktop:
    x = (int(intel_Column_desktop[n.series])) * seriesWidth + intelOffset + 5
    y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
    draw.text((x, y), n.name, font=font, fill=textColor)

textColor = (0, 0, 220)
text_bg = (180, 200, 255)
for n in amd_all:
    x = amdOffset + int(amd_Column[n.series]) * seriesWidth_amd + 5
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
draw.text((50, y + 40), r'数据源:'+datalink, font=font, fill='white')
draw.text((x + amdOffset, y + 45), authorInfo, font=font, fill='white')




# debug 模式
if buildType == 'debug':
    img = np.array(img_pil)

    cv2.imencode(pic_format, img)[1].tofile(pic_path)
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
font = ImageFont.truetype(fontFile, size=24)
w, h = font.getsize(watermarkText)
watermask = np.zeros((imgHigh, imgWidth*2, 4), np.uint8)
watermask[:, :] = (0, 0, 0, 1)
watermask_pil = Image.fromarray(watermask)
draw = ImageDraw.Draw(watermask_pil)
x, y = 15, 15
while y < imgHigh:
    while x < imgWidth*2:
        rd_color = HSL2RGB(int(random.random()*360),1, 0.75)

        draw.text((x, y), watermarkText, font=font, fill=rd_color)
        draw.text((x, y + h), authorInfo, font=font, fill=rd_color)
        x += int(1.6 * w)
    x = 15
    y += 8 * h

# cv2.imshow('watermask',np.array(watermask_pil))
# cv2.waitKey(0)
# exit(-99)

# 水印层旋转加裁切
watermask = np.array(watermask_pil)
matRotate = cv2.getRotationMatrix2D((imgHigh * 0.5, imgHigh * 0.5), 45, 1)  # mat rotate 1 center 2 angle 3 缩放系数
watermask = cv2.warpAffine(watermask, matRotate, (imgHigh, imgHigh))
w = int((imgHigh - imgWidth) / 2)
watermask = watermask[:, w:w + imgWidth]
watermask = cv2.resize(watermask, (imgWidth, imgHigh), interpolation=cv2.INTER_AREA)

img = np.array(img_pil)
img = cv2.addWeighted(img, 1, watermask, 0.1, 0)  # 叠加水印层



# 错误提示水印
# img_add = cv2.addWeighted(img, 1, watermask, 0.2, 0)


# 保存图片
# cv2.imwrite(pic_path, img)
cv2.imencode(pic_format, img)[1].tofile(pic_path)

print(title+' is done.')
print('Path: '+pic_path)

