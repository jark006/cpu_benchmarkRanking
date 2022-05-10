from bs4 import BeautifulSoup
from myutil import *
import urllib.request

url = r'https://browser.geekbench.com/processor-benchmarks'
htmlPath = r'data/geekbench5.html'

path = [
    r'data/gb5_single_list.txt',
    r'data/gb5_multi_list.txt',
]

def download2htmlfile(url1, p):
    print('Download ... {}'.format(url1))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
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
    singlebody = BeautifulSoup(html, "html.parser").find('div', id='single-core').find('tbody')
    multibody = BeautifulSoup(html, "html.parser").find('div', id='multi-core').find('tbody')
    return singlebody, multibody


def chart2rawlist(body):
    name_list = []
    score_list = []
    for tr in body.find_all('tr'):
        name = tr.find('a').text
        score = tr.find('td', class_='score').text
        name_list.append(name.strip('\n'))
        score_list.append(score.strip('\n'))
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
        orgName = str(name_list[i])
        orgName = orgName.replace('Microsoft Surface Edition', '')
        orgName = orgName.replace('Black Edition', '')
        reduceName = ''
        if 'Intel' in orgName:
            # if ('m3-' in s) or ('m5-' in s) or ('m7-' in s) or ('M-' in s) or ('Atom' in s):
            #     # print(s + ' ' + str(sys._getframe().f_lineno))
            #     unsupport(s)
            #     continue

            try:
                if ('m3-' in orgName) or ('m5-' in orgName) or ('m7-' in orgName) or ('M-' in orgName):
                    reduceName = orgName[orgName.index('-') - 2:]
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Atom'
                    cpu_platform = 'laptop'
                elif 'Atom' in orgName:
                    reduceName = orgName[orgName.index('Atom'):]
                    reduceName = reduceName.replace('Atom', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Atom'
                    cpu_platform = 'laptop'
                elif 'Core 2' in orgName:
                    reduceName = orgName[orgName.index('Core 2'):]
                    reduceName = reduceName.replace('Core 2', '')
                    reduceName = reduceName.replace('Extreme ', 'Extreme-')
                    reduceName = reduceName.replace('Quad ', 'Quad-')
                    reduceName = reduceName.replace('Duo ', 'Duo-')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Core2'
                    cpu_platform = 'desktop'
                elif 'Core ' in orgName:
                    if 'i9' in orgName:
                        cpu_series = 'i9'
                    elif 'i7' in orgName:
                        cpu_series = 'i7'
                    elif 'i5' in orgName:
                        cpu_series = 'i5'
                    elif 'i3' in orgName:
                        cpu_series = 'i3'
                    elif 'i4' in orgName:
                        orgName = orgName.replace('i4', 'i5')
                        cpu_series = 'i5'
                    else:
                        # print(s + ' ' + str(sys._getframe().f_lineno))
                        unsupport(orgName)
                        continue
                    reduceName = orgName[orgName.index('i'):]
                    reduceName = reduceName.strip(' ')
                    cpu_platform = 'desktop'
                elif 'Pentium' in orgName:
                    reduceName = orgName[orgName.index('Pentium'):]
                    reduceName = reduceName.replace('Pentium', ' ')
                    reduceName = reduceName.replace('Gold', ' ')
                    reduceName = reduceName.replace('Silver', ' ')

                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Pentium'
                    cpu_platform = 'desktop'
                elif 'Celeron' in orgName:
                    reduceName = orgName[orgName.index('Celeron'):]
                    reduceName = reduceName.replace('Celeron', '')
                    reduceName = reduceName.replace('Gold', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Celeron'
                    cpu_platform = 'desktop'
                elif 'Xeon' in orgName:
                    reduceName = orgName[orgName.index('Xeon'):]
                    reduceName = reduceName.replace('Xeon', '')
                    reduceName = reduceName.replace('Processor', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Xeon'
                    if 'E5-' in orgName:
                        cpu_series = 'E5'
                    cpu_platform = 'desktop'
                else:

                    # print(orgName + ' ' + str(sys._getframe().f_lineno))
                    unsupport(orgName)
                    continue
            except Exception:
                # print("ERROR:" + s)
                # print(orgName + ' ' + str(sys._getframe().f_lineno))
                unsupport(orgName)
                continue

            if len(reduceName) < 3 or len(reduceName) > 14:
                # print(ss+' is too long.')
                # print(orgName + ' ' + str(sys._getframe().f_lineno))
                unsupport(orgName)
                continue

            if(len(reduceName) < 4):
                continue

            if ('U' in reduceName) or ('M' in reduceName) or ('H' in reduceName) or ('EQ' in reduceName) or ('QE' in reduceName) or ('Y' in reduceName):
                cpu_platform = 'laptop'

            if cpu_series == 'Xeon':
                cpu_platform = 'desktop'

            if reduceName[-3] == 'G' and reduceName[-1] == 'E':
                cpu_platform = 'laptop'

            if reduceName[0] == 'i' and (reduceName[-1] == 'G' or reduceName[-2] == 'G'):
                cpu_platform = 'laptop'

            intel_list.append(Node('Intel', cpu_series, reduceName, score_list[i], cpu_platform))

        else:
            
            if ('Opteron' in orgName)  or ('Sempron' in orgName) : #or ('AMD E1-' in s) or ('AMD E2-' in s)or ('AMD E-' in s) or ('AMD C-' in s):
                # print(s + ' ' + str(sys._getframe().f_lineno))
                # unsupport(s)
                reduceName = orgName.replace('AMD ', '')
                amd_list.append(Node('AMD', 'other', reduceName, score_list[i], 'desktop'))
                continue

            # s = s.replace('PRO', '')
            orgName = orgName.replace('APU', '')

            try:
                if 'EPYC' in orgName:
                    reduceName = orgName[orgName.index('EPYC'):]
                    reduceName = reduceName.replace('EPYC', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'EPYC'
                    reduceName = cpu_series + ' ' + reduceName
                elif 'Ryzen Threadripper' in orgName:
                    reduceName = orgName[orgName.index('Threadripper'):]
                    reduceName = reduceName.replace('Threadripper', 'TR')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'TR'
                elif 'Ryzen 9' in orgName:
                    reduceName = orgName[orgName.index('Ryzen'):]
                    reduceName = reduceName.replace('Ryzen 9', 'R9')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'R9'
                elif 'Ryzen 7' in orgName:
                    reduceName = orgName[orgName.index('Ryzen'):]
                    reduceName = reduceName.replace('Ryzen 7', 'R7')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'R7'
                elif 'Ryzen 5' in orgName:
                    reduceName = orgName[orgName.index('Ryzen'):]
                    reduceName = reduceName.replace('Ryzen 5', 'R5')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'R5'
                elif 'Ryzen 3' in orgName:
                    reduceName = orgName[orgName.index('Ryzen'):]
                    reduceName = reduceName.replace('Ryzen 3', 'R3')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'R3'

                elif 'FX' in orgName:
                    reduceName = orgName[orgName.index('FX'):]
                    reduceName = reduceName.replace('Eight-Core', '')
                    reduceName = reduceName.replace('Six-Core', '')
                    reduceName = reduceName.replace('Quad-Core', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'Bulldozer'
                elif 'A12' in orgName:
                    reduceName = orgName[orgName.index('A12'):]
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'APU'
                elif 'A10' in orgName:
                    reduceName = orgName[orgName.index('A10'):]
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'APU'
                elif 'A8' in orgName:
                    reduceName = orgName[orgName.index('A8'):]
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'APU'
                elif 'A6' in orgName:
                    # reduceName = orgName[orgName.index('A6'):]
                    reduceName = orgName.replace('AMD ', '')
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'APU'
                elif 'A4' in orgName:
                    reduceName = orgName[orgName.index('A4'):]
                    reduceName = reduceName.strip(' ')
                    cpu_series = 'APU'
                elif 'Turion' in orgName:
                    reduceName = orgName[orgName.index('Turion'):]
                    reduceName = reduceName.replace('Turion 64', '')
                    reduceName = reduceName.replace('Turion ', '')
                    reduceName = reduceName.strip()
                    cpu_series = 'Turion'
                elif 'Athlon' in orgName:
                    reduceName = orgName[orgName.index('Athlon'):]
                    reduceName = reduceName.replace('Athlon 64', '')
                    reduceName = reduceName.replace('Athlon ', '')
                    reduceName = reduceName.strip()
                    cpu_series = 'Athlon'
                elif 'Phenom' in orgName:
                    reduceName = orgName[orgName.index('Phenom'):]
                    reduceName = reduceName.replace('Phenom ', '')
                    # ss = ss.replace('Quad-Core', '')
                    # ss = ss.replace('Triple-Core', '')
                    # ss = ss.replace('Dual-Core', '')
                    reduceName = reduceName.strip()
                    cpu_series = 'Phenom'
                else:
                    # print(orgName + ' ' + str(sys._getframe().f_lineno))
                    unsupport(orgName)
                    continue
                cpu_platform = 'desktop'
            except Exception:
                # print(orgName + ' ' + str(sys._getframe().f_lineno))
                unsupport(orgName)
                continue

            if len(reduceName) < 3 or len(reduceName) > 14:
                # print(reduceName+' is too long.')
                # print(orgName + ' ' + str(sys._getframe().f_lineno))
                unsupport(orgName)
                continue

            if ('U' in reduceName) or ('H' in reduceName) or ('M' in reduceName) or ('N' in reduceName) or ('B' in reduceName):
                cpu_platform = 'laptop'
            if ('P' in reduceName) and ('PRO' not in reduceName):
                cpu_platform = 'laptop'
            if ('EPYC' in reduceName):
                cpu_platform = 'desktop'

            if(len(reduceName) == 0):
                continue

            amd_list.append(Node('AMD', cpu_series, reduceName, score_list[i], cpu_platform))

    # print('Total CPU list len:{}'.format(len(name_list)))
    # print('Intel_list len:{}'.format(len(intel_list)))
    # print('AMD_list len:{}'.format(len(amd_list)))
    # print('Unspport_list len:{}'.format(len(unsupport_list)))

    return intel_list, amd_list


def save_list(path1, intel_list, amd_list):
    all_list = intel_list + amd_list
    # for i in intel_list:
    #     all_list.append(i)
    # for i in amd_list:
    #     all_list.append(i)

    f = open(path1, 'w')
    f.writelines(str(len(all_list)) + '\n')
    for a in all_list:
        f.writelines(a.vendor + '\n')
        f.writelines(a.series + '\n')
        f.writelines(a.name + '\n')
        f.writelines(str(a.score) + '\n')
        f.writelines(a.platform + '\n')
    f.close()


def main():
    download2htmlfile(url, htmlPath)

    logSingle=''
    logMulti =''
    isSingleUpdate = False
    isMultiUpdate = False

    single_list_last = readlistGB(path[0])
    multi_list_last  = readlistGB(path[1])
    single_set_last = set()
    multi_set_last  = set()

    for node in single_list_last:
        single_set_last.add(node.vendor+' '+node.name)
    for node in multi_list_last:
        multi_set_last.add(node.vendor+' '+node.name)

    singlebody, multibody = htmlfile2chart(htmlPath)

    name_list, score_list = chart2rawlist(singlebody)
    # print(len(name_list))
    intel_list, amd_list = rawlist_depart(name_list, score_list)

    singleNew = list()
    for node in intel_list+amd_list:
        if node.vendor+' '+node.name in single_set_last:
            single_set_last.remove(node.vendor+' '+node.name)
        else:
            singleNew.append(node.vendor+' '+node.name)
    singleRemove = list(single_set_last)

    if len(singleNew) > 0  or len(singleRemove) > 0:
        isSingleUpdate = True

        save_list(path[0], intel_list, amd_list)
        # print(unsupport_list)
        # length = len(unsupport_list)

        if len(singleNew) > 0:
            logSingle += '新增内容：\n'
            for name in singleNew:
                logSingle += '  新增 '+name+'\n'
        if len(singleRemove) > 0:
            logSingle += '移除内容：\n'
            for name in singleRemove:
                logSingle += '  移除 '+name+'\n'
        logSingle += '\n'
        print(path[0]+' is done.')
    else:
        logSingle += '\n单核数据无变更。\n\n'

    name_list, score_list = chart2rawlist(multibody)
    # print(len(name_list))
    intel_list, amd_list = rawlist_depart(name_list, score_list)

    mutilNew = list()
    for node in intel_list+amd_list:
        if node.vendor+' '+node.name in multi_set_last:
            multi_set_last.remove(node.vendor+' '+node.name)
        else:
            mutilNew.append(node.vendor+' '+node.name)
    mutilRemove = list(multi_set_last)

    if len(mutilNew) > 0  or len(mutilRemove) > 0:
        isMultiUpdate = True

        save_list(path[1], intel_list, amd_list)
        # print(unsupport_list)
        # length = len(unsupport_list)

        if len(mutilNew) > 0:
            logMulti += '新增内容：\n'
            for name in mutilNew:
                logMulti += '  新增 '+name+'\n'
        if len(mutilRemove) > 0:
            logMulti += '移除内容：\n'
            for name in mutilRemove:
                logMulti += '  移除 '+name+'\n'
        logMulti += '\n'
            
        print(path[0]+' is done.')
    else:
        logMulti += '数据无变更。\n\n'


    # print(logStr)

    print('All done.')

    return isSingleUpdate, isMultiUpdate, logSingle, logMulti

if __name__ == '__main__':
    print('Do not run this.\nRun draw_gb5.py')