from bs4 import BeautifulSoup
from myutil import *
import urllib.request


unsupport_list = set()


def unsupport(reason: str, gpuName: str):
    print("[Add unsupport GPU]", reason, gpuName)
    unsupport_list.add(gpuName)


def parseBody(html: BeautifulSoup) -> list[gpuInfo]:
    gpuInfoList: list[gpuInfo] = []
    namelist: list[BeautifulSoup] = html.find_all("a", class_="hover:no-underline")
    scorelist: list[BeautifulSoup] = html.find_all(
        "span", class_="mx-2 text-slate-900 text-sm font-bold"
    )

    namelist2 = list()
    for n in namelist:
        n = n.text.replace("\n", "").strip()
        n = (
            n.replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
        )
        namelist2.append(n)

    scorelist2 = list()
    for n in scorelist:
        n = n.text.replace("\n", "").strip()
        n = (
            n.replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
        )
        if "." not in n:
            scorelist2.append(n)

    if len(namelist2) == len(scorelist2):
        for i in range(len(namelist2)):
            gpuInfoList.append(gpuInfo(namelist2[i], scorelist2[i]))
    elif len(namelist2) > len(scorelist2):
        offset = len(namelist2) - len(scorelist2)
        for i in range(len(scorelist2)):
            gpuInfoList.append(gpuInfo(namelist2[i + offset], scorelist2[i]))
    else:
        print(
            f"ERROR len(namelist2):{len(namelist2)}  len(scorelist2):{len(scorelist2)}"
        )
        exit(-1)

    return gpuInfoList


def downloadAndParseHTML(url: str, DataSetPath: str):
    print("Downloading from {} ...".format(url))
    req = urllib.request.Request(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        },
    )
    res = urllib.request.urlopen(req)
    html = res.read().decode("utf-8")

    # with open('data/top-gpus.html', 'wb') as f:
    #     f.write(html.encode('utf-8'))
    # exit(0)

    # print('read from data/top-gpus.html')
    # with open('data/top-gpus.html', 'rb') as f:
    #     html = f.read().decode('utf-8')

    print("Start parse HTML file ...")

    gpuList = parseBody(BeautifulSoup(html, "html.parser"))

    parseGpuInfoList(gpuList)

    gpuInfoDict: dict[str, gpuInfo] = {}
    for gpu in gpuList:
        gpuInfoDict[gpu.name] = gpu

    save_GPU_DataSet(DataSetPath, gpuInfoDict)


def parseGpuInfoList(gpuInfoList: list[gpuInfo]):
    for gpu in gpuInfoList:
        gpu.name = gpu.name.replace("th gen", "th").replace("notebook", "M").strip()
        if "Intel" in gpu.name:
            gpu.vendor = "Intel"
            gpu.platform = "Desktop"

            try:
                if "Arc" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("Arc") :]
                    gpu.series = "Arc"
                elif "UHD" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("UHD") :].replace(
                        " Graphics ", ""
                    )
                    gpu.series = "UHD"
                elif "HD" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("HD") :].replace(
                        " Graphics ", ""
                    )
                    gpu.series = "HD"
                elif "Iris" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("Iris") :].replace(
                        " Graphics ", ""
                    )
                    gpu.series = "Iris"
                else:
                    # gpu.name = gpu.name.replace('Intel','').strip()
                    # gpu.series = 'Other'
                    gpu.isDeprecated = True
                    unsupport("Unknown Intel", gpu.name)
                    continue

            except Exception:
                gpu.isDeprecated = True
                unsupport("Intel Exception:", gpu.name)
                continue

            gpu.name = gpu.name.strip()

            if len(gpu.name) < 3 or len(gpu.name) > 32:
                gpu.isDeprecated = True
                unsupport("Intel The length of the name is illegal:", gpu.name)
                continue

            if "M" == gpu.name[-1]:
                gpu.platform = "Laptop"
            if "M)" in gpu.name:
                gpu.platform = "Laptop"
            if "Mobile" in gpu.name:
                gpu.platform = "Laptop"

        elif ("AMD" in gpu.name) or ("ATI" in gpu.name):
            gpu.vendor = "AMD"
            gpu.platform = "Desktop"

            try:
                if "RX" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("RX") :]
                    if "9" == gpu.name[3]:
                        gpu.series = "RX9"
                    elif "7" == gpu.name[3]:
                        gpu.series = "RX7"
                    elif "6" == gpu.name[3]:
                        gpu.series = "RX6"
                    elif "5" == gpu.name[3]:
                        gpu.series = (
                            "RX5"
                            if (len(gpu.name) > 6 and gpu.name[6] == "0")
                            else "RX500"
                        )
                    elif "4" == gpu.name[3]:
                        gpu.series = "RX4"
                    elif "Vega" in gpu.name:
                        gpu.name = gpu.name[gpu.name.index("Vega") :]
                        gpu.series = "Vega"
                    else:
                        gpu.isDeprecated = True
                        unsupport("Unknown series", gpu.name)
                        continue

                elif "R9" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("R9") :]
                    gpu.series = "R9"
                elif "R7" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("R7") :]
                    gpu.series = "R7"
                elif "R5" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("R5") :]
                    gpu.series = "R5"
                elif "Vega" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("Vega") :]
                    gpu.series = "Vega"
                elif "FirePro" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("FirePro") :]
                    gpu.series = "FirePro"
                elif "HD" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("HD") :]
                    gpu.series = "HD"
                elif "Radeon" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("Radeon") + 7 :]
                    gpu.series = "Other"
                    if "6900" in gpu.name:
                        gpu.name = "RX " + gpu.name
                        gpu.series = "RX6"
                else:
                    gpu.isDeprecated = True
                    unsupport("Unknown series", gpu.name)
                    continue

            except Exception:
                gpu.isDeprecated = True
                unsupport("AMD Exception: ", gpu.name)
                continue

            gpu.name = gpu.name.strip()

            if len(gpu.name) < 3 or len(gpu.name) > 32:
                gpu.isDeprecated = True
                unsupport("AMD The length of the name is illegal:", gpu.name)
                continue

            if gpu.name[-1:] == "M" or gpu.name[-1:] == "S":
                gpu.platform = "Laptop"
            if len(gpu.name) > 4 and gpu.name[-4:] == "M XT":
                gpu.platform = "Laptop"
            if "Mobile" in gpu.name:
                gpu.platform = "Laptop"

        elif "NVIDIA" in gpu.name:
            gpu.vendor = "NVIDIA"
            gpu.platform = "Desktop"
            gpu.name = (
                gpu.name.replace("notebook", "M")
                .replace("Notebook", "M")
                .replace("SUPER", "S")
            )
            try:
                if "RTX" in gpu.name:
                    gpu.name = gpu.name[gpu.name.index("RTX") :]
                    if gpu.name[4] == "6":
                        gpu.series = "RTX6"
                    elif gpu.name[4] == "5":
                        gpu.series = "RTX5"
                    elif gpu.name[4] == "4":
                        gpu.series = "RTX4"
                    elif gpu.name[4] == "3":
                        gpu.series = "RTX3"
                    elif gpu.name[4] == "2":
                        gpu.series = "RTX2"
                    elif gpu.name[4] == "A":
                        gpu.series = "RTXA"
                    else:
                        gpu.series = "RTX1"
                elif "Quadro" in gpu.name:
                    gpu.series = "Quadro"
                    gpu.name = gpu.name[gpu.name.index("Quadro") :]
                elif "Tesla" in gpu.name:
                    gpu.series = "Tesla"
                    gpu.name = gpu.name[gpu.name.index("Tesla") :]
                elif "TITAN" in gpu.name:
                    gpu.series = "Titan"
                    gpu.name = gpu.name[gpu.name.index("TITAN") :]
                elif "Titan" in gpu.name:
                    gpu.series = "Titan"
                    gpu.name = gpu.name[gpu.name.index("Titan") :]
                elif "GTX 16" in gpu.name:
                    gpu.series = "GTX16"
                    gpu.name = gpu.name[gpu.name.index("GTX 16") :]
                elif "GTX 10" in gpu.name:
                    gpu.series = "GTX10"
                    gpu.name = gpu.name[gpu.name.index("GTX 10") :]
                elif "P106" in gpu.name:
                    gpu.series = "GTX10"
                    gpu.name = gpu.name[gpu.name.index("NVIDIA") + 7 :]
                elif "GTX 9" in gpu.name:
                    gpu.series = "GTX9"
                    gpu.name = gpu.name[gpu.name.index("GTX 9") :]
                elif "GTX 8" in gpu.name:
                    gpu.series = "GTX8"
                    gpu.name = gpu.name[gpu.name.index("GTX 8") :]
                elif "GTX 7" in gpu.name:
                    gpu.series = "GTX7"
                    gpu.name = gpu.name[gpu.name.index("GTX 7") :]
                elif "GTX 6" in gpu.name:
                    gpu.series = "GTX6"
                    gpu.name = gpu.name[gpu.name.index("GTX 6") :]
                elif "GT 10" in gpu.name:
                    gpu.series = "GT10"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 9" in gpu.name:
                    gpu.series = "GT9"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 8" in gpu.name:
                    gpu.series = "GT8"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 7" in gpu.name:
                    gpu.series = "GT7"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 6" in gpu.name:
                    gpu.series = "GT6"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 5" in gpu.name:
                    gpu.series = "GT5"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 4" in gpu.name:
                    gpu.series = "GT4"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 3" in gpu.name:
                    gpu.series = "GT3"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "GT 2" in gpu.name:
                    gpu.series = "GT2"
                    gpu.name = gpu.name[gpu.name.index("GT") :]
                elif "LHR" in gpu.name:
                    gpu.series = "RTX3"
                    gpu.name = "RTX " + gpu.name[gpu.name.index("GeForce") + 8 :]
                elif "MX" in gpu.name:
                    gpu.series = "MX"
                    gpu.name = gpu.name[gpu.name.index("MX") :]
                elif gpu.name.startswith("NVIDIA GeForce GTS"):
                    gpu.series = "GT" + gpu.name[19:20]
                    gpu.name = gpu.name[15:]
                elif gpu.name.startswith("NVIDIA GeForce"):
                    gpu.series = "GT" + gpu.name[15:16]
                    gpu.name = "GT " + gpu.name[15:]
                else:
                    gpu.isDeprecated = True
                    unsupport("NVIDIA Exception: ", gpu.name)
                    continue

            except Exception:
                gpu.isDeprecated = True
                unsupport("NVIDIA Exception: ", gpu.name)
                continue

            if (
                (gpu.name[-1] == "M")
                or (gpu.name[-4:] == "M GT")
                or ("(M" in gpu.name)
                or ("MX" in gpu.name)
                or ("Mobile" in gpu.name)
            ):
                gpu.platform = "Laptop"

        else:
            gpu.isDeprecated = True
            unsupport("Unknown GPU: ", gpu.name)
            continue

    IntelCnt = 0
    AMDCnt = 0
    NVIDIACnt = 0

    for gpu in gpuInfoList:
        if len(gpu.series) == 0 or len(gpu.platform) == 0:
            print("Some wrong:")
            for key, value in vars(gpu).items():
                print(key, ":", value)
            exit(-1)

        if gpu.vendor == "Intel":
            IntelCnt += 1
        elif gpu.vendor == "AMD":
            AMDCnt += 1
        elif gpu.vendor == "NVIDIA":
            NVIDIACnt += 1

    print("Total GPUs:", len(gpuInfoList))
    print("Intel_list:", IntelCnt)
    print("AMD_list:", AMDCnt)
    print("NVIDIA_list:", NVIDIACnt)
    print("Unspport_list:", len(unsupport_list))


if __name__ == "__main__":
    print("Do not run this.\nRun draw_3dmark.py")
