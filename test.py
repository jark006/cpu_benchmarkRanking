from bs4 import BeautifulSoup
from myutil import Node
import urllib.request
import sys
import random
import hashlib
from io import BytesIO
import gzip

url = [
    r'https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_single_core-7',
    r'https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_multi_core-8',
    ]
urlphp = [r'https://www.cpu-monkey.com/ajax/benchmark.php']
htmlPath = [
    r'data/r15_single.html',
    r'data/r15_multi.html'
]

path = [
    r'data/r15_single_list.txt',
    r'data/r15_multi_list.txt',
]

def download2htmlfile(url1, p):
    print('Download ... {}'.format(url1))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'accept-encoding':'gzip, deflate, br',
        'content-length':'4',
        'content-type':'application/x-www-form-urlencoded',
        'origin':'https://www.cpu-monkey.com',
        'refer':'https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_single_core-7',
        }
    data = b'id=7'
    req = urllib.request.Request(url=url1, headers=headers,data=data)
    res = urllib.request.urlopen(req)
    html = res.read()
    buff = BytesIO(html)
    f = gzip.GzipFile(fileobj=buff)
    html = f.read().decode('utf-8')
    # print(html)
    f = open(p, 'w', encoding='utf-8')
    f.write(html)
    f.close()

download2htmlfile(r'https://www.cpu-monkey.com/ajax/benchmark.php', 'data/test.html')