from bs4 import BeautifulSoup
from myutil import Node
import urllib.request
import sys

url = r'https://browser.geekbench.com/processor-benchmarks'
htmlPath = r'data/geekbench5.html'

path = [
    r'data/gb5_single_list.txt',
    r'data/gb5_multi_list.txt',
]

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
                elif 'Core 2' in s:
                    ss = s[s.index('Core 2'):]
                    ss = ss.replace('Core 2', '')
                    ss = ss.replace('Extreme', '')
                    ss = ss.replace('Quad', '')
                    ss = ss.replace('Duo', '')
                    ss = ss.strip(' ')
                    cpu_series = 'Core2'
                    cpu_platform = 'desktop'
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
                        # print(s + ' ' + str(sys._getframe().f_lineno))
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
                    cpu_series = 'Xeon'
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

            if cpu_series == 'Xeon':
                cpu_platform = 'desktop'

            if(len(ss) == 0):
                continue

            if ss[0] == 'i' and (ss[-1] == 'G' or ss[-2] == 'G'):
                cpu_platform = 'laptop'

            intel_list.append(Node('Intel', cpu_series, ss, score_list[i], cpu_platform))

        else:
            if ('Opteron' in s) or ('Embedded' in s):
                # print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue
            if ('Opteron' in s) or ('Dual Core' in s) or ('Quad Core' in s):
                # print(s + ' ' + str(sys._getframe().f_lineno))
                unsupport(s)
                continue

            # s = s.replace('PRO', '')
            s = s.replace('APU', '')

            try:
                if 'EPYC' in s:
                    ss = s[s.index('EPYC'):]
                    ss = ss.replace('EPYC', '')
                    ss = ss.strip(' ')
                    cpu_series = 'EPYC'
                    ss = cpu_series + ' ' + ss
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
                elif 'Turion' in s:
                    ss = s[s.index('Turion'):]
                    ss = ss.replace('Turion 64', '')
                    ss = ss.replace('Turion ', '')
                    ss = ss.strip()
                    cpu_series = 'Turion'
                elif 'Athlon' in s:
                    ss = s[s.index('Athlon'):]
                    ss = ss.replace('Athlon 64', '')
                    ss = ss.replace('Athlon ', '')
                    ss = ss.strip()
                    cpu_series = 'Athlon'
                elif 'Phenom' in s:
                    ss = s[s.index('Phenom'):]
                    ss = ss.replace('Phenom ', '')
                    # ss = ss.replace('Quad-Core', '')
                    # ss = ss.replace('Triple-Core', '')
                    # ss = ss.replace('Dual-Core', '')
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

            if ('U' in ss) or ('H' in ss) or ('M' in ss) or ('N' in ss) or ('B' in ss):
                cpu_platform = 'laptop'
            if ('P' in ss) and ('PRO' not in ss):
                cpu_platform = 'laptop'
            if ('EPYC' in ss):
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


if __name__ == '__main__':
    download2htmlfile(url, htmlPath)
    singlebody, multibody = htmlfile2chart(htmlPath)


    name_list, score_list = chart2rawlist(singlebody)
    print(len(name_list))
    intel_list, amd_list = rawlist_depart(name_list, score_list)
    save_list(path[0], intel_list, amd_list)
    print(unsupport_list)
    length = len(unsupport_list)
    print(path[0]+' is done.')

    name_list, score_list = chart2rawlist(multibody)
    print(len(name_list))
    intel_list, amd_list = rawlist_depart(name_list, score_list)
    save_list(path[1], intel_list, amd_list)
    print(unsupport_list[length:])
    print(path[1]+' is done.')
    

    print('All done.')

