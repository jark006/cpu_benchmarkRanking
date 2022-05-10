'''
 jark006
 date: 2021-4-28
 jark006@qq.com

 Explanation:
    First step, run 'download_data.py' download cpu bench date from geekbench.com,
        it will parsing data and save to file 'all_list.txt'
    And then run this script, load 'all_list' and make it to a chart file.
'''

from ast import Return
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import ptp
from scipy.optimize import curve_fit
import time
import cv2
from PIL import ImageFont, ImageDraw, Image
from myutil import *
import random, os, datetime

def draw(coreType = 'Single'):
    
    global singleVerChange
    global multiVerChange

    buildType = 'debugX'
    dataSource = r'Geekbench5'
    datalink = r'https://browser.geekbench.com/processor-benchmarks'
    authorInfo = 'Make by JARK006'
    # link = r'https://pan.baidu.com/s/1PII6fOqHPoyRy-pr37CPBg  提取码: etpt'

    fontFile = r'c:\windows\fonts\msyh.ttc'
    fontFilebd = r'c:\windows\fonts\msyhbd.ttc'
    pic_format = '.png'
    
    if coreType == 'Single':
        highScale = 1.2 #高度比例
        fixOffset = 40
        baseScore = 1000
        # parameter = [ 2.24473411e+03, -9.66584721e+02,  1.22222273e+00]  # geekbench single
        parameter = [ 399.3926221795527, -1476.1098914481624, 2.7568419324427853 ]
        title = dataSource+'单核性能天梯图'
        watermarkText = title + ' Single-Core'
        versionFilePath = r'gb5_single_ver.txt'
        logoPath = r'pic/logoGB5s.png'
        listPath = r'data/gb5_single_list.txt'
        percent = [x for x in range(20, 151, 5)]+[x for x in range(160, 211, 10)]
        
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
            'other':7,'other2':7,
            }
        # 修正分数
        fix_score = {
            # 'i9-10900K': 1420,
        }
        more = [
            # Node('AMD', 'R9', 'R9 3900XT', 1350, 'desktop'),
        ]
    else:  # multiCore
        highScale = 0.2 #高度比例
        fixOffset = 0
        baseScore = 2000
        parameter = [1.40299769e+03, - 1.79848915e+03, - 8.62352477e-01] # geekbench multi
        title = dataSource+'多核性能天梯图'
        watermarkText = title+' Multi-Core'
        versionFilePath = r'gb5_multi_ver.txt'
        logoPath = r'pic/logoGB5m.png'
        listPath = r'data/gb5_multi_list.txt'
        percent = \
            [i for i in range(20,  100+1,5)]+\
            [i for i in range(110, 200+1,10)]+\
            [i for i in range(200, 300+1,20)]+\
            [i for i in range(300, 500+1,50)]+\
            [600, 700, 800, 1000, 1200, 1500]
        

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
            'other':7,'other2':7,
        }

        # 修正分数
        fix_score = {
            # 'i9-9980XE': 15400,
        }
        more = [
            # Node('AMD', 'R9', 'R9 3900XT', 13700, 'desktop'),
        ]

    cur_Ver, lastVer = get_update_version(versionFilePath)
    if coreType == 'Single':
        singleVerChange = '{} to {} '.format(lastVer, cur_Ver)
    else:
        multiVerChange = '{} to {} '.format(lastVer, cur_Ver)
    build_date = time.strftime("%Y%m%d", time.localtime())
    pic_path = 'output/GeekBench5_'+coreType + '_' + build_date + '_' +  cur_Ver + pic_format




    def score2high(p, x, highScale):
        if coreType == 'Single' and x>baseScore*1.4: # 12代单核有点高，从140%性能的开始自乘1.0, 线性到200%自乘0.9,
            x=x*(37/30.0-(x/baseScore)/6)

        res = func(x, p[0], p[1],p[2])
        return int(res*highScale)

    all_list = readlistGB(listPath)

    boollist = {'i3': True, 'i5': True, 'i7': True, 'i9': True, 'E5': True, 'Xeon': True,
                'Core2': True,  'Pentium': True,'Celeron': True, 'Atom':True,
                'EPYC': True, 'TR': True, 'R9': True, 'R7': True, 'R5': True, 'R3': True, 
                'Bulldozer': True, 'APU': True, 'Phenom': True, 'Athlon': True, 'Turion': True,
                'other':True
                }
    for node in all_list:
        series = node.series
        boollist[series] = not boollist[series]
        if (boollist[series]):
            series = series+'2'
        node.series = series

    intel_desktop = []  # 桌面平台
    intel_mobile = []  # 移动平台
    amd_all = []


    # 效果不错
    def func(x, a, b, c):
        # if coreType == 'Single':
        #     return a * np.arctan(b / x) + c
        # else:
        #     return a * np.exp2(b / x) + c
        x=x+fixOffset
        return a * np.exp2(b / x) + c

    def fit(x, y):
        popt, pcov = curve_fit(func, x, y)
        print('[ {}, {}, {} ]'.format(popt[0], popt[1], popt[2]))
        y1 = [func(i, popt[0], popt[1], popt[2]) for i in x]
        # 支持中文
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.plot(x, y,  '.', label='原始离散值')
        plt.plot(x, y1, 'r', label='拟合曲线')
        plt.xlabel('CPU score')
        plt.ylabel('High')
        plt.legend(loc=4)  # 指定legend的位置
        plt.title('拟合结果')
        # plt.savefig(dataSource+('Single' if coreType=='Single' else 'multi') + str(int(time.time())) + '.png')
        plt.show()


    # Begin -------------------拟合分数，将分数尽可能线性平均分布-------------------
    # x=list()
    # x.append(all_list[0].score+fixOffset)
    # for y in all_list:
    #     if x[-1]> y.score+4+fixOffset: # 间隔取值，区段扎堆数据导致两极数据拟合差距大
    #         x.append(y.score+fixOffset)
    # x.sort()
    # y = range(len(x))
    # fit(x, y)
    # exit()
    # End -------------------拟合分数，将分数尽可能线性平均分布--------------------


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

    # print('Intel_desktop len:{}'.format(len(intel_desktop)))
    # print('Intel_mobile len:{}'.format(len(intel_mobile)))
    # print('AMD_all len:{}'.format(len(amd_all)))


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
        n.high -= highMIN-2
    for n in intel_desktop:
        n.highFix -= highMIN-2
        n.high -= highMIN-2
    for n in amd_all:
        n.highFix -= highMIN-2
        n.high -= highMIN-2

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
                h = (3*y - 8*abs(x - (centerOffset + centerWidth / 2)))
                h = ((h - (h%200)) % imgHigh) / imgHigh
                draw.point((x, y), fill=HSL2BGR(h, 0.6, 0.80))

    # 中间百分比
    font = ImageFont.truetype(fontFilebd, size=24)
    for index, high in enumerate(percentHigh):
        t = '%3d%%' % (percent[index])
        x = centerOffset + 20
        y = int(imgHigh - downEdgeHigh - high * textHigh)
        h = 3*y / imgHigh + 0.75
        h =  h - int(h)
        draw.text((x, y), t, font=font, fill=tuple(HSL2RGB(h, 1, 0.30)))


    font = ImageFont.truetype(fontFile, size=textHigh)
    textColor = (220, 0, 0)
    for n in intel_mobile:
        x = int(intel_Column_mobile[n.series]) * seriesWidth + intelOffset2 + 5
        y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
        # if n.high != n.highFix: # 附加修正位置时，被迫下降的高度
        #     n.name=n.name+' ^'+str(n.high - n.highFix)
        draw.text((x, y), n.name, font=font, fill=textColor)

    for n in intel_desktop:
        x = (int(intel_Column_desktop[n.series])) * seriesWidth + intelOffset + 5
        y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
        # if n.high != n.highFix:
        #     n.name=n.name+' ^'+str(n.high - n.highFix)
        draw.text((x, y), n.name, font=font, fill=textColor)

    textColor = (0, 0, 220)
    text_bg = (180, 200, 255)
    for n in amd_all:
        x = amdOffset + int(amd_Column[n.series]) * seriesWidth_amd + 5
        y = int(imgHigh - downEdgeHigh - n.highFix * textHigh)
        # if n.high != n.highFix:
        #     n.name=n.name+' ^'+str(n.high - n.highFix)

        # 文字背景
        if n.platform == 'laptop':
            w, h = font.getsize(n.name)
            draw.rectangle((x - 2, y+2, x + w + 2, y + h), fill=text_bg)

        draw.text((x, y), n.name, font=font, fill=textColor)



    font = ImageFont.truetype(fontFilebd, size=30)
    text = 'Intel移动端'
    w, h = font.getsize(text)
    x, y = (intelOffset-w)/2, (100-h)/2
    draw.text((x, y), text, font=font, fill='white')
    text = 'Intel桌面及服务器端'
    w, h = font.getsize(text)
    x, y = intelOffset+(centerOffset-intelOffset-w)/2, (100-h)/2
    draw.text((intelOffset2 + x, y), text, font=font, fill='white')
    text = 'AMD全系列(移动端为浅红底色)'
    w, h = font.getsize(text)
    x, y = amdOffset+(imgWidth-amdOffset-w)/2, (100-h)/2
    draw.text((intelOffset2 + x, y), text, font=font, fill='white')




    x, y = 50, imgHigh - 85
    draw.text((50, y), title, font=font, fill='white')
    draw.text((x + amdOffset, y), 'Build ' + build_date + ' ' + cur_Ver, font=font, fill='white')

    font = ImageFont.truetype(fontFile, size=25)
    draw.text((50, y + 40), r'数据源  '+datalink, font=font, fill='white')
    draw.text((x + amdOffset, y + 45), authorInfo, font=font, fill='white')




    # debug 模式
    if buildType == 'debug':
        img = np.array(img_pil)

        cv2.imencode(pic_format, img)[1].tofile(pic_path)
        print('Debug Mode:')
        print(title+' is done.')
        exit()


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
            rd_color = HSL2RGB(random.random(), 1, 0.65)
            authorInfo2 = ' '*random.randint(0,6)+ authorInfo
            draw.text((x, y), watermarkText, font=font, fill=rd_color)
            draw.text((x, y + h), authorInfo2, font=font, fill=rd_color)
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


def get_update_version(path):
    mainVer = 1
    subVer = 0
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                ver = f.readline().split('.')
                mainVer = int(ver[0])
                subVer = int(ver[1])
            except:
                print('版本文件读取解析错误')
                f.close()
    
    lastVerStr = 'Ver{}.{}'.format(mainVer, subVer)
    subVer += 1 #只更改子版本号， 主版本号待较大升级时手动更改

    verStr = 'Ver{}.{}'.format(mainVer, subVer)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines('{}.{}'.format(mainVer, subVer))
    
    return verStr, lastVerStr


if __name__ == '__main__':
    global singleVerChange
    global multiVerChange
    import download_gb5
    isSingleUpdate, isMultiUpdate, logSingle, logMulti= download_gb5.main()

    if not isSingleUpdate and not isMultiUpdate:
        print('没有内容更新。')
        exit(0)
    
    singleVerChange = ''
    multiVerChange  = ''
    if isSingleUpdate:
        draw('Single')
    if isMultiUpdate:
        draw('Multi')

    cur_time = datetime.datetime.now()
    date_str = cur_time.strftime('%Y%m%d_%H%M%S')
    with open('./output/GeekBench5更新日志_'+date_str+'.txt', 'w', encoding='utf-8') as f:
        date_str = cur_time.strftime('%Y-%m-%d %H:%M:%S')
        f.write('Geekbench5 更新日志 '+date_str+'\n\n')
        f.write('单核 '+singleVerChange+'更新内容：\n')
        f.write(logSingle)
        
        f.write('多核 '+multiVerChange+'更新内容：\n')
        f.write(logMulti)
