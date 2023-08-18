from bs4 import BeautifulSoup
from myutil import *
import urllib.request


unsupport_list = set()
def unsupport(reason:str, cpuName:str):
    print('[Add unsupport CPU]', reason, cpuName)
    unsupport_list.add(cpuName)
    return

def parseBody(body):
    CpuInfoList:list[cpuInfo] = []
    for tr in body.find_all('tr'):
        name = tr.find('a').text.strip('\n')
        score = tr.find('td', class_='score').text.strip('\n')
        CpuInfoList.append(cpuInfo(name, score))
    return CpuInfoList


def downloadAndParseHTML(url:str, DataSetPath:str):
    print('Downloading from {} ...'.format(url))
    req = urllib.request.Request(url=url, headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
    res = urllib.request.urlopen(req)
    html = res.read().decode('utf-8')

    print('Start parse HTML file ...')
    singleBody = BeautifulSoup(html, "html.parser").find('div', id='single-core').find('tbody')
    multiBody = BeautifulSoup(html, "html.parser").find('div', id='multi-core').find('tbody')
    singleCoreCpuInfoList, multiCoreCpuInfoList = parseBody(singleBody), parseBody(multiBody)

    parseCpuInfoList(singleCoreCpuInfoList)
    parseCpuInfoList(multiCoreCpuInfoList)

    cpuInfoDict:dict[str,cpuInfo]={}
    for cpu in singleCoreCpuInfoList:
        cpuInfoDict[cpu.name]=cpu

    for cpu in multiCoreCpuInfoList:
        cpuInfoDict[cpu.name].scoreMulti=cpu.score

    for cpu in cpuInfoDict.values():
        if cpu.score == 0 or cpu.scoreMulti == 0:
            cpu.isDeprecated=True

    saveDataSet(DataSetPath, cpuInfoDict)


def parseCpuInfoList(cpuInfoList:list[cpuInfo]):    
    for cpu in cpuInfoList:
        nameBackup = cpu.name
        cpu.name = cpu.name.replace('Microsoft Surface Edition', '')
        if 'Intel' in cpu.name:
            cpu.vendor = 'Intel'
            cpu.platform = 'Desktop'

            try:
                if ('m3-' in cpu.name) or ('m5-' in cpu.name) or ('m7-' in cpu.name) or ('M-' in cpu.name):
                    cpu.name = cpu.name[cpu.name.index('-') - 2:]
                    cpu.series = 'Atom'
                    cpu.platform = 'Laptop'

                elif 'Atom' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Atom'):].replace('Atom', '')
                    cpu.series = 'Atom'
                    cpu.platform = 'Laptop'

                elif 'Core 2' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Core 2'):].replace('Core 2', '').replace('Extreme ', 'Extreme-').replace('Quad ', 'Quad-').replace('Duo ', 'Duo-')
                    cpu.series = 'Core2'

                elif 'Core ' in cpu.name:
                    if 'i9' in cpu.name:
                        cpu.series = 'i9'
                    elif 'i7' in cpu.name:
                        cpu.series = 'i7'
                    elif 'i5' in cpu.name:
                        cpu.series = 'i5'
                    elif 'i3' in cpu.name:
                        cpu.series = 'i3'
                    elif 'i4' in cpu.name:
                        cpu.name = cpu.name.replace('i4', 'i5') # i4-4690T ???
                        cpu.series = 'i5'
                    else:
                        cpu.isDeprecated=True
                        unsupport('Unknown Intel Core', cpu.name)
                        continue

                    cpu.name = cpu.name[cpu.name.index('i'):]

                elif 'Pentium' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Pentium'):].replace('Pentium', ' ').replace('Gold', ' ').replace('Silver', ' ')
                    cpu.series = 'Pentium'

                elif 'Celeron' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Celeron'):].replace('Celeron', '').replace('Gold', '')
                    cpu.series = 'Celeron'

                elif 'Xeon' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Xeon'):].replace('Xeon', '').replace('Processor', '')
                    cpu.series = 'E5'if 'E5-' in cpu.name else 'Xeon'
                    if len(cpu.name) < 1:
                        cpu.name=nameBackup
                else:
                    cpu.isDeprecated=True
                    unsupport('Unknown Intel', cpu.name)
                    continue

            except Exception:
                cpu.isDeprecated=True
                unsupport("Intel Exception:", cpu.name)
                continue

            cpu.name=cpu.name.strip()

            if len(cpu.name) < 3 or len(cpu.name) > 14:
                cpu.isDeprecated=True
                unsupport('Intel The length of the name is illegal:', cpu.name)
                continue

            if ('U' in cpu.name) or ('M' in cpu.name) or ('H' in cpu.name) or ('EQ' in cpu.name) or ('QE' in cpu.name) or ('Y' in cpu.name):
                cpu.platform = 'Laptop'

            if cpu.name[-3] == 'G' and cpu.name[-1] == 'E':
                cpu.platform = 'Laptop'

            if cpu.name[0] == 'i' and (cpu.name[-1] == 'G' or cpu.name[-2] == 'G'):
                cpu.platform = 'Laptop'
            
            if cpu.series == 'Xeon':
                cpu.platform = 'Desktop'

        elif 'AMD' in cpu.name:
            cpu.vendor='AMD'
            cpu.platform='Desktop'

            if ('Opteron' in cpu.name) or ('Sempron' in cpu.name) or ('AMD E1-' in cpu.name) or ('AMD E2-' in cpu.name)or ('AMD E-' in cpu.name) or ('AMD C-' in cpu.name):
                cpu.name = cpu.name.replace('AMD ', '').strip(' ')
                cpu.series='Other'
                continue

            # info.name = info.name
            cpu.name = cpu.name.replace('APU', '').replace('Black Edition', '').replace(' PRO', 'P')

            try:
                if 'EPYC' in cpu.name:
                    cpu.series = 'EPYC'
                    # info.nameFix = 'EPYC '+info.name[info.name.index('EPYC'):].replace('EPYC', '')
                    cpu.name = cpu.name[cpu.name.index('EPYC'):]
                elif 'Ryzen Threadripper' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Threadripper'):].replace('Threadripper', 'TR')
                    cpu.series = 'TR'
                elif 'Ryzen 9' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Ryzen'):].replace('Ryzen 9', 'R9')
                    cpu.series = 'R9'
                elif 'Ryzen 7' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Ryzen'):].replace('Ryzen 7', 'R7')
                    cpu.series = 'R7'
                elif 'Ryzen 5' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Ryzen'):].replace('Ryzen 5', 'R5')
                    cpu.series = 'R5'
                elif 'Ryzen 3' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Ryzen'):].replace('Ryzen 3', 'R3')
                    cpu.series = 'R3'

                elif 'FX' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('FX'):].replace('Eight-Core', '').replace('Six-Core', '').replace('Quad-Core', '')
                    cpu.series = 'Bulldozer'
                elif 'A12' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('A12'):]
                    cpu.series = 'A12'
                elif 'A10' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('A10'):]
                    cpu.series = 'A10'
                elif 'A8' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('A8'):]
                    cpu.series = 'A8'
                elif 'A6' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('A6'):]
                    cpu.series = 'A6'
                elif 'A4' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('A4'):]
                    cpu.series = 'A4'
                elif 'Turion' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Turion'):].replace('Turion 64', '').replace('Turion ', '')
                    cpu.series = 'Turion'
                elif 'Athlon' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Athlon'):].replace('Athlon 64', '').replace('Athlon ', '')
                    cpu.series = 'Athlon'
                elif 'Phenom' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('Phenom')+7:]
                    cpu.series = 'Phenom'
                elif 'R-Series' in cpu.name:
                    cpu.name = cpu.name[cpu.name.index('R-Series'):].replace('R-Series ', '')
                    cpu.series = 'R3'
                else:
                    cpu.isDeprecated=True
                    unsupport('Unknown series', cpu.name)
                    continue

            except Exception:
                cpu.isDeprecated=True
                unsupport('AMD Exception', cpu.name)
                continue

            cpu.name=cpu.name.strip()

            if len(cpu.name) < 3 or len(cpu.name) > 14:
                cpu.isDeprecated=True
                unsupport('AMD The length of the name is illegal:', cpu.name)
                continue

            if cpu.name[-1:] in ['U', 'H','M','N','B','P','G',]:
                cpu.platform = 'Laptop'
            if cpu.name[-2:] in ['HX', 'HS','MX',]:
                cpu.platform = 'Laptop'
            if ('EPYC' in cpu.name):
                cpu.platform = 'Desktop'

        else:
            cpu.isDeprecated=True
            unsupport('Unknwn CPU:', cpu.name)
            continue

    IntelCnt=0
    AMDCnt=0

    for cpu in cpuInfoList:
        if len(cpu.series)==0 or len(cpu.platform)==0:
            print('Some wrong:')
            for key, value in vars(cpu).items():
                print(key, ":", value)
            exit(-1)

        if cpu.vendor == 'Intel':
            IntelCnt +=1
        elif cpu.vendor == 'AMD':
            AMDCnt +=1

    print('Total CPUs:', len(cpuInfoList))
    print('Intel_list:', IntelCnt)
    print('AMD_list:', AMDCnt)
    print('Unspport_list:', len(unsupport_list))


if __name__ == '__main__':
    print('Do not run this.\nRun draw_gb5.py')