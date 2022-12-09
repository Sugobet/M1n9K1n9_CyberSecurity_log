由于这几章实验内容比较多，就不在这展示了

# Shell and Web Shell

比较简单, 主要是netcat和matesploit的使用

不用msfvenom生成shellcode payload也可以看在线网站：https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md

包含了非常多的reverse shell payload

# Linux 权限提升

由于东西太多，只记录点重要的

    uname -a 信息收集
    /proc/version 信息收集
    ps -aux 进程表
    env 环境变量
    sudo -l 查看能sudo的命令
    find
    find ... 2>/dev/null 将错误丢垃圾桶，其他命令适用


### 内核漏洞利用

通过信息收集的系统内核版本，寻找存在的漏洞

在线网站: https://www.linuxkernelcves.com/

使用可用exp或者matesploit利用

### sudo -l

sudo允许我们以比当前用户更高的权限运行某个命令

如果sudo运行当前用户运行如：find、less、base64....等等

则可以尝试提权：

    sudo find . -exec /bin/bash \;  -exec 执行命令

.

    sudo less /etc/passwd 回车
    !/bin/bash 回车

.

    base64用于读取权限高的文件

# https://gtfobins.github.io/ 命令列表


### SUID

文件可以具有读取、写入和执行权限。这些权限授予用户的权限级别。这随着 SUID（设置用户标识）和 SGID（设置组标识）而更改。它们允许分别以文件所有者或组所有者的权限级别执行文件。

    find / -type f -perm -04000 2>/dev/null    查看设有suid的文件

/etc/shadow需要root才能读写, 可以想办法利用sudo或具有suid的文件读写命令尝试读取，如base64

利用unshadow配合john可以尝试爆破用户密码:

    unshadow </etc/passwd> </etc/shadow> > <OutFileName>

将上述输出的文件利用john暴力破解

    john --wordlist <比如rockyou.txt> <上述输出的文件名>


此外，如果有权限，还可以直接向/etc/passwd/添加root权限的用户

使用openssl创建加盐hash密码:

    openssl passwd -1 -salt h4ck <password>

然后将结果插入：

    <username>:<上述结果>:0:0:root:/root:/bin/bash

    将该条信息追加进/etc/passwd


### Capabilities

系统管理员可用于提高进程或二进制文件权限级别的另一种方法是“Capabilities”. Capabilities 帮助在更精细的级别管理权限。例如，如果 SOC 分析师需要使用需要启动套接字连接的工具，则普通用户将无法执行此操作。如果系统管理员不想授予此用户更高的权限，他们可以更改Capabilities的二进制文件。因此，二进制文件将在不需要更高权限用户的情况下完成其任务

    getcap -r / 2>/dev/null

例如如果vim在cap里面，则可以尝试提权：

    ./vim -c ':py3 import os;os.setuid(0);os.execl("/bin/sh","sh","-c","reset; exec sh")'

注意程序路径！

<pre>karen@ip-10-10-141-89:~$ pwd
/home/karen
karen@ip-10-10-141-89:~$ getcap -r / 2&gt;/dev/null |grep vim
/home/karen/vim = cap_setuid+ep
karen@ip-10-10-141-89:~$ 
</pre>


### Cron Jobs

Cron 作业用于在特定时间运行脚本或二进制文件。默认情况下，它们以其所有者而不是当前用户的权限运行。虽然正确配置的 cron 作业本身并不容易受到攻击，但在某些情况下它们可以提供权限升级向量。
这个想法很简单;如果有一个以 root 权限运行的计划任务，并且我们可以更改将要运行的脚本，那么我们的脚本将以 root 权限运行。

Cron 作业配置存储为 crontabs（cron 表），以查看任务下次运行的时间和日期。

系统上的每个用户都有自己的 crontab 文件，无论他们是否登录，都可以运行特定任务。如您所料，我们的目标是找到一个由 root 设置的 cron 作业，并让它运行我们的脚本，最好是 shell。

CTF 机器可以每分钟或每 5 分钟运行一次 cron 作业，但您更经常会在渗透测试活动中看到每天、每周或每月运行的任务。

    /etc/crontab


可以尝试修改具有高权限的的crontab运行的脚本文件，可以改成reverse shell，我们这边就可以监听,getshell

Crontab 总是值得检查的，因为它有时会导致简单的权限升级向量。以下情况在没有特定网络安全成熟度级别的公司中并不少见：

    系统管理员需要定期运行脚本。

    他们创建一个 cron 作业来执行此操作

    一段时间后，脚本变得无用，他们将其删除

    他们不清理相关的 cron 作业

    此更改管理问题会导致利用 cron 作业的潜在漏洞利用。

如果crontab中任务还存在，但执行的脚本文件已经不存在了，我们可以尝试在crontab中指定的目录创建一个自定义的脚本文件 如 反向shell，这样我们的脚本将会被定时运行
