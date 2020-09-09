from bs4 import BeautifulSoup
import urllib.request
import sys
import random
import hashlib

url = [
    r'https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_single_core-7',
    r'https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_multi_core-8',
    ]

htmlPath = [
    r'single.html',
    r'multi.html'
]

path = [
    'single_list.txt',
    'multi_list.txt',
]
pathLast = [
    'single_listLast.txt',
    'multi_listLast.txt',
]


class Node:
    def __init__(self, vendor, series, name, score, platform):
        self.vendor = vendor
        self.series = series
        self.name = name
        self.score = score
        self.platform = platform
        self.high = 0
        self.highFix = 0  # 高度修正，避免重叠







def download2htmlfile(url1, p):
    print('Download ... {}'.format(url1))
    headers = {
        'User-Agent': 'Chrome/55.0.2883.87'}
    req = urllib.request.Request(url=url1, headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read().decode('utf-8')
    f = open(p, 'w', encoding='utf-8')
    f.write(html)
    f.close()


def htmlfile2chart(p):
    print('read:'+p)
    f = open(p, 'r', encoding='utf-8')
    html = f.read()
    f.close()

    print('Start parse...')
    tbody = BeautifulSoup(html, "html.parser").find('table', class_='data')
    return tbody


def chart2rawlist(body):
    name_list = []
    score_list = []
    for tr in body.find_all('tr', style='vertical-align: middle;'):
        name = tr.find('a', class_='black').text
        score = tr.find('div', class_='benchmarkbar').text
        score = score.replace(',', '')
        name_list.append(name.strip('\n'))
        score_list.append(int(score))
    print('CPU num:'+str(len(name_list)))
    return name_list, score_list

unsupport_list = []
def unsupport(s):
    # print('Unsupport CPU: '+s)
    unsupport_list.append(s)
    return


def rawlist_depart(name_list, score_list):
    intel_list = []
    amd_list = []
    
    for i in range(0, len(name_list)):
        cpu_platform = 'unkown'
        cpu_series = ''
        s = str(name_list[i])
        s = s.replace('Microsoft Surface Edition', '')
        s = s.replace('Black Edition', '')

        if 'Intel' in s:
            # if ('m3-' in s) or ('m5-' in s) or ('m7-' in s) or ('M-' in s) or ('Atom' in s):
            #     # print(s + ' ' + str(sys._getframe().f_lineno))
            #     unsupport(s)
            #     continue

            try:
                if ('m3-' in s) or ('m5-' in s) or ('m7-' in s) or ('M-' in s):
                    ss = s[s.index('-') - 2:]
                    ss = ss.strip(' ')
                    cpu_series = 'Atom'
                    cpu_platform = 'laptop'
                elif 'Atom' in s:
                    ss = s[s.index('Atom'):]
                    ss = ss.replace('Atom', '')
                    ss = ss.strip(' ')
                    cpu_series = 'Atom'
                    cpu_platform = 'laptop'
                elif 'Core ' in s:
                    if 'i9' in s:
                        cpu_series = 'i9'
                    elif 'i7' in s:
                        cpu_series = 'i7'
                    elif 'i5' in s:
                        cpu_series = 'i5'
                    elif 'i3' in s:
                        cpu_series = 'i3'
                    elif 'i4' in s:
                        s = s.replace('i4', 'i5')
                        cpu_series = 'i5'
                    else:
                        print(s + ' ' + str(sys._getframe().f_lineno))
                        unsupport(s)
                        continue
                    ss = s[s.index('i'):]
                    ss = ss.strip(' ')
                    cpu_platform = 'desktop'
                elif 'Pentium' in s:
                    ss = s[s.index('Pentium'):]
                    ss = ss.replace('Pentium', ' ')
                    ss = ss.replace('Gold', ' ')
                    ss = ss.replace('Silver', ' ')

                    ss = ss.strip(' ')
                    cpu_series = 'Pentium'
                    cpu_platform = 'desktop'
                elif 'Celeron' in s:
                    ss = s[s.index('Celeron'):]
                    ss = ss.replace('Celeron', '')
                    ss = ss.replace('Gold', '')
                    ss = ss.strip(' ')
                    cpu_series = 'Celeron'
                    cpu_platform = 'desktop'
                elif 'Xeon' in s:
                    ss = s[s.index('Xeon'):]
                    ss = ss.replace('Xeon', '')
                    ss = ss.replace('Processor', '')
                    ss = ss.strip(' ')
                    cpu_series = 'Platinum' if 'Platinum' in s else 'Xeon'
                    if 'E5-' in s:
                        cpu_series = 'E5'
                    cpu_platform = 'desktop'
                else:

                    print(s + ' ' + str(sys._getframe().f_lineno))
                    unsupport(s)
                    continue
            except Exception:
                # print("ERROR:" + s)
                print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            if len(ss) > 14:
                # print(ss+' is too long.')
                print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            if ('U' in ss) or ('M' in ss) or ('H' in ss) or ('EQ' in ss) or ('QE' in ss) or ('Y' in ss):
                cpu_platform = 'laptop'

            if cpu_series == 'Xeon' or cpu_series == 'Platinum':
                cpu_platform = 'desktop'

            if(len(ss) == 0):
                continue

            if ss[0] == 'i' and (ss[-1] == 'G' or ss[-2] == 'G'):
                cpu_platform = 'laptop'

            intel_list.append(Node('Intel', cpu_series, ss, score_list[i], cpu_platform))

        else:
            if 'Opteron' in s:
                # print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue
            if ('Opteron' in s) or ('Dual Core' in s) or ('Quad Core' in s):
                # print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            s = s.replace('APU', '')
            s = s.replace('Pro', 'PRO')

            try:
                if 'PRO 7' in s:
                    s = s.replace('PRO 7', '7 PRO')

                if 'Epyc' in s:
                    ss = s[s.index('Epyc'):]
                    ss = ss.strip(' ')
                    cpu_series = 'EPYC'
                elif 'Ryzen Threadripper' in s:
                    ss = s[s.index('Threadripper'):]
                    ss = ss.replace('Threadripper', 'TR')
                    ss = ss.strip(' ')
                    cpu_series = 'TR'
                elif 'Ryzen 9' in s:
                    ss = s[s.index('Ryzen'):]
                    ss = ss.replace('Ryzen 9', 'R9')
                    ss = ss.strip(' ')
                    cpu_series = 'R9'
                elif 'Ryzen 7' in s:
                    ss = s[s.index('Ryzen'):]
                    ss = ss.replace('Ryzen 7', 'R7')
                    ss = ss.strip(' ')
                    cpu_series = 'R7'
                elif 'Ryzen 5' in s:
                    ss = s[s.index('Ryzen'):]
                    ss = ss.replace('Ryzen 5', 'R5')
                    ss = ss.strip(' ')
                    cpu_series = 'R5'
                elif 'Ryzen 3' in s:
                    ss = s[s.index('Ryzen'):]
                    ss = ss.replace('Ryzen 3', 'R3')
                    ss = ss.strip(' ')
                    cpu_series = 'R3'
                elif 'Ryzen Embedded' in s:
                    ss = s[s.index('Embedded'):]
                    ss = ss.replace('Embedded', 'RE')
                    ss = ss.strip(' ')
                    cpu_series = 'RE'
                elif 'FX' in s:
                    ss = s[s.index('FX'):]
                    ss = ss.replace('Eight-Core', '')
                    ss = ss.replace('Six-Core', '')
                    ss = ss.replace('Quad-Core', '')
                    ss = ss.strip(' ')
                    cpu_series = 'Bulldozer'
                elif 'A12' in s:
                    ss = s[s.index('A12'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'A10' in s:
                    ss = s[s.index('A10'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'A8' in s:
                    ss = s[s.index('A8'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'A6' in s:
                    ss = s[s.index('A6'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'A4' in s:
                    ss = s[s.index('A4'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'A9' in s:
                    ss = s[s.index('A9'):]
                    ss = ss.strip(' ')
                    cpu_series = 'APU'
                elif 'Turion' in s:
                    ss = s[s.index('Turion'):]
                    ss = ss.replace('Turion ', '')
                    ss = ss.strip()
                    cpu_series = 'Turion'
                elif 'Athlon' in s:
                    ss = s[s.index('Athlon'):]
                    ss = ss.replace('Athlon ', '')
                    ss = ss.strip()
                    cpu_series = 'Athlon'
                elif 'Phenom' in s:
                    ss = s[s.index('Phenom'):]
                    ss = ss.replace('Phenom ', '')
                    ss = ss.strip()
                    cpu_series = 'Phenom'
                else:
                    print(s + ' ' + str(sys._getframe().f_lineno))
                    unsupport(s)
                    continue
                cpu_platform = 'desktop'
            except Exception:
                print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            if len(ss) > 14:
                print(ss+' is too long.')
                print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            if ('U' == ss[-1]) or ('H' == ss[-1]) or ('M' == ss[-1]) \
                or ('P' == ss[-1]) or ('B' == ss[-1]) or ('S' == ss[-1]):
                cpu_platform = 'laptop'
            if cpu_series == 'EPYC':
                cpu_platform = 'desktop'

            if(len(ss) == 0):
                continue

            amd_list.append(Node('AMD', cpu_series, ss, score_list[i], cpu_platform))

    print('Total CPU list len:{}'.format(len(name_list)))
    print('Intel_list len:{}'.format(len(intel_list)))
    print('AMD_list len:{}'.format(len(amd_list)))
    print('Unspport_list len:{}'.format(len(unsupport_list)))

    return intel_list, amd_list


def save_list(path1, intel_list, amd_list):
    all_list = []
    for i in intel_list:
        all_list.append(i)
    for i in amd_list:
        all_list.append(i)

    f = open(path1, 'w')
    f.writelines(str(len(all_list)) + '\n')
    for a in all_list:
        f.writelines(a.vendor + '\n')
        f.writelines(a.series + '\n')
        f.writelines(a.name + '\n')
        f.writelines(str(a.score) + '\n')
        f.writelines(a.platform + '\n')
    f.close()



def CalcSha1(filepath):
    # os.path.exists
    try:
        with open(filepath,'rb') as f:
            sha1obj = hashlib.sha1()
            sha1obj.update(f.read())
            hash = sha1obj.hexdigest()
            return hash
    except IOError:
        return 'xx'

s = 's'

if __name__ == '__main__':
    returnValue = 0

    download2htmlfile(url[0], htmlPath[0])
    singlebody = htmlfile2chart(htmlPath[0])
    name_list, score_list = chart2rawlist(singlebody)

    intel_list, amd_list = rawlist_depart(name_list, score_list)
    print(unsupport_list)

    save_list(path[0], intel_list, amd_list)
    hashNew = CalcSha1(path[0])
    hashOld = CalcSha1(pathLast[0])
    if(hashNew != hashOld):
        print(path[0]+' is update, need to generate a new benchmark piture.')
        save_list(pathLast[0], intel_list, amd_list)
        returnValue += 1
    else:
        print(path[0]+' nothing change.')


    download2htmlfile(url[1], htmlPath[1])
    multibody = htmlfile2chart(htmlPath[1])
    name_list, score_list = chart2rawlist(multibody)    

    intel_list, amd_list = rawlist_depart(name_list, score_list)
    print(unsupport_list)
    save_list(path[1], intel_list, amd_list)
    hashNew = CalcSha1(path[1])
    hashOld = CalcSha1(pathLast[1])
    if(hashNew != hashOld):
        print(path[1]+' is update, need to generate a new benchmark piture.')
        save_list(pathLast[1], intel_list, amd_list)
        returnValue += 2
    else:
        print(path[1]+' nothing change.')
    
    exit(returnValue)


