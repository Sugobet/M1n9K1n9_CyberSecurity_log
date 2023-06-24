# 前言

有一个月时间没发文章了，我在6月11号进入htb学院学习CPTS，在扎实的THM基础的加持下，我学的非常顺利，其实大部分内容都相当于复习，而学到的内容只是一些可能不太常见、又或者非常细节的小技巧，这也是非常棒的。

虽说大部分内容在整个THM学习周期当中都有学会在，但htb学院仍然具有相当一部分THM可能没有的微妙的小细节，这是值得学习的。

截至到目前为止我的CPTS学习进度也已经将要接近尾声，而这也只是才过了11天左右的时间

![在这里插入图片描述](https://img-blog.csdnimg.cn/0bced17ade7546de97d12d73c2dd6176.png)

**老样子，节省时间，我只写非常值得复习的部分，而不是全部模块**

# PASSWORD ATTACKS

## 密码重用/默认密码

[DefaultCreds-cheat-sheet](https://github.com/ihebski/DefaultCreds-cheat-sheet)    直接可以查找一些cms的默认凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/1b13427c3b7a48b585277d306b3d6f53.png)

## SAM

- security文件包含域账户凭据的缓存

## CrackMapExec远程转储

```bash
crackmapexec smb 10.129.42.198 --local-auth -u bob -p HTB_@cademy_stdnt! --lsa
```

当然除了--lsa，还有--sam、--ntds一键转储

值得注意的是如果是本地账户得加--local-auth参数

## Rundll32转储lsass

```powershell
PS C:\Windows\system32> rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full
```

通过rundll32调用comsvcs.dll的MiniDump来转储lsass

## python版mimikatz - pypykatz

## MSV

MSV 是 Windows 中的一个身份验证包，LSA 调用它来验证针对 SAM 数据库的登录尝试。当然也包括以加入域的设备进行域的NTLM身份验证时候也调用MSV

## DPAPI

数据保护应用程序编程接口，主要用于一些工具软件的密码加解密，比如一些常见的浏览器。它的密钥存储在lsass内存中

## Win凭据搜集工具 LaZagne

用于检索存储在本地计算机上的大量密码。 每个软件都使用不同的技术（明文、API、自定义算法、数据库等）存储其密码。开发此工具的目的是为最常用的软件查找这些密码。

LaZagne也有python版本，也可用于linux

## Lin凭据收集工具 mimipenguin

它可以查找在内存当中的凭据以及一些常见软件工具的文件当中存储的凭据

前提是需要root

## Win pth to RDP

pth登rdp有个前提条件是开启Restricted admin模式，我们可以通过修改注册表开启

	reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f

## UAC

thm讲过

UAC（用户帐户控制）限制本地用户执行远程管理操作的能力。当注册表项设置为 0 时，这意味着内置本地管理员帐户（RID-500，“管理员”）是唯一允许执行远程管理任务的本地帐户。将其设置为 1 也允许其他本地管理员。

	HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy

## PTK

不论是NTLM还是Kerberos都有相同的尿性，都用其密码衍生的hash来加密时间戳和响应质询，所以Kerberos可以进行ptk，其实跟NTLM的pth是一致的，所以可以看到使用mimikatz的进行ptk的时候使用的命令跟pth一样

## PTT横向

ptt注入ticket后直接enter-pssession

# Linux域PTT

可以通过realm命令检查机器有没有加入域

## kinit

用kinit可以请求tgt并存储为keytab

	kinit svc_workstations@INLANEFREIGHT.HTB -k -t /home/carlos@inlanefreight.htb/.scripts/svc_workstations.kt

smblient可以使用-k参数来通过kerberos进行身份验证

## ccache

凭据缓存或 ccache 文件在 Kerberos 凭据保持有效时保存，并且通常在用户的会话持续期间保存。用户向域进行身份验证后，将创建一个存储票证信息的 ccache 文件。此文件的路径放置在KRB5CCNAME环境变量中。

ccache文件存在在/tmp目录下，并非所有ccache文件都会有效，仅活动的ccache才有效

export后可以通过klist查看有效时间

## KeyTab导出

使用[KeyTabExtract](https://github.com/sosdave/KeyTabExtract)可以从keytab中提取hash

## ccache to windows kirbi

通过impacket的ticketConverter进行转换

## Linikatz

该工具将从不同的 Kerberos 实现（如 FreeIPA、SSSD、Samba、Vintella 等）中提取所有凭据，包括 Kerberos 票证。提取凭据后，它会将它们放在名称以 开头的文件夹中。在此文件夹中，您将找到不同可用格式的凭据，包括 ccache 和密钥表。

## BitLocker

对于vhb文件，可以使用bitlocker2john进行转换为hash进行爆破

