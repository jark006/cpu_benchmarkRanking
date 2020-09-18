# cpu_benchmarkRanking

## Lang: Python3.X

## System: Windows10

### You need change the value of var `fontFile `(path to fontfile:" xxx.ttc") to run on other systems.

## Lib request: ` OpenCV, BeautifulSoup, numpy, matplotlib, scipy, PIL ` 

First step, cd to one of those directory, such as  `cd ./cinebenchr15` ;

Now run `download_data.py` to download cpu bench date from website, it will parsing data and save to file 'all_list.txt'

Then, run `generateBenchPic.py` to generate a chart pictrue in this directory.

In `generateBenchPic.py `, change the value of var `coreType`(`'single'` or other ) to set whether to generate a single-core graph or a multi-core graph.

Same the operate to directory `cinebenchr20` and `geekbench5`.

----
----
# Date source：

## CinebenchR15

https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_single_core-7

https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r15_multi_core-8


## CinebenchR20

https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r20_single_core-9

https://www.cpu-monkey.com/en/cpu_benchmark-cinebench_r20_multi_core-10'

## Geekbench 5

https://browser.geekbench.com/processor-benchmarks

