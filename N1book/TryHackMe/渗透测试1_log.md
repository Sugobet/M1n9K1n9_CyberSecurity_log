从渗透测试到red的path

记录点刚学的有意思的，前面有一些挺简单的没记录

https://crt.sh/ 可以查站点ssl/tls的证书，作用就是可以收集子域

python3 sublist3r.py -d     通过一大堆osint，搜索相关的子域信息

ffuf -w(wordlist) /usr/share/wordlists/SecLists/Discovery/DNS/namelist.txt -H(head) "Host: FUZZ.acmeitsupport.thm" -u(Url) http://

-fs参数过滤多数size相同的结果

这里通过利用namelist.txt 爆破请求头中的host字段，以达到搜索出子域。

ffuf还能扫目录，通过-u参数: "https://baidu.com/FUZZ"     ‘FUZZ’将会被程序识别并匹配字典
