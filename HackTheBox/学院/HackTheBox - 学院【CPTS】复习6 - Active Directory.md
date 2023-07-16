# ACTIVE DIRECTORY ENUMERATION & ATTACKS

这个模块其实与thm的AD教程相比，还是thm更适合刚开始接触AD以及学习从枚举到持久化的全阶段（红队）。而htb学院这个模块更注重于枚举和各种攻击手段，有点纯渗透的风格，弱化了每个阶段之间的概念，所以这两家平台的AD教程形成一种互补。

当有了thm的AD全部知识，之后再来到这个模块，就会发现两家的AD教程各有各的优点，thm有的知识，htb学院的这个模块不一定也会有，反之亦然。所以我仍然强调的是形成互补之势，而不是哪家的教程更好，盲目比较这两家谁更好，只能说明这个人非常愚蠢。

在这个模块，在我thm原有的知识基础上，进一步加深了我对AD以及Kerberos、ACL、Trust之类的了解，还有PowerView、Rubeus之类的热门工具的使用

我们会发现这个模块部分内容根据linux、windows两大平台进行分别教程(TTP)，意在：如果我们立足于linux或者是我们的攻击机kali上，我们能做什么，用什么做；如果我们立足于windows，我们能做什么，用什么做

## LLMNR & NBT-NS

当dns发生故障无法正常服务或用户使用了错误的域名访问导致dns查询失败时，会采用LLMNR向链路本地的其他主机进行查询，如果LLMNR失败，则会采用 NBT-NS，这将可能导致获取密码 hash甚至是ntlm中继（非强制smb签名的情况下）

常用的两种工具linux下的responder和windows的Inveigh，Inveigh有powershell版本和C Sharp版本

## Kerbrute用户枚举细节

Kerbrute使用Kerberos预身份验证来枚举用户，所以枚举的时候如果有已禁用预身份验证的账户，Kerbrute会直接请求并输出。因此不会生成4625登录失败事件，但会生成4768Kerberos TGT请求事件，这也能够在严格的4625事件监控下逃脱

## Internal Password Spraying

在域内的windows主机上可以使用DomainPasswordSpray.ps1和Rubeus，甚至是Kerbrute来进行spray

此外我们还应该关注密码重用的问题，这将能使用明文密码或者hash进行spray

## 已登录账户

crackmapexec的--loggedon-users参数可以让我查看到有哪些用户已在这台机器登录，我们将可以尝试通过内存提取其凭据

## wmiexec & smb/psexec

wmiexec可能会导致频繁出现4688创建新进程事件日志，而smbexec、psexec通过IPC\$和ADMIN\$，传递文件并通过svcctl创建服务，而这一行为也会被Win Defender检测到

## net1 - net

## setspn.exe

通过setvpn可以帮助枚举所有具有SPN的账户

	setspn -Q */*

## 受支持的PowerView - Empire

	https://github.com/BC-SECURITY/Empire/blob/main/empire/server/data/module_source/situational_awareness/network/powerview.ps1

## ACL

![在这里插入图片描述](https://img-blog.csdnimg.cn/050d998a238042f6bf50889a6f9a10ae.png)

在bloodhound文档当中，也有非常多可滥用的ace type文档，并且描述了如何通过powerview去利用

	https://bloodhound.readthedocs.io/en/latest/data-analysis/edges.html

## 查询指定ACL

	Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}

## GenericWrite

powerview：

```powershell
Set-DomainObject -Identity <obj> -Set @{serviceprincipalname="hacker/M"} -Credential $cred
```

此外还可以使用[targetedKerberoast](https://github.com/ShutdownRepo/targetedKerberoast)在linux机器上执行此操作

## PowerView查找能够dcsync acl

```powershell
Get-ObjectAcl "DC=inlanefreight,DC=local" -ResolveGUIDs | ? { ($_.ObjectAceType -match 'Replication-Get')}
```

	如果我们对用户拥有某些权限（例如 WriteDacl），我们还可以将此权限添加到我们控制下的用户，执行 DCSync 攻击，然后删除权限以尝试掩盖我们的踪迹。

## 设置了可逆加密密码的账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/92c7e884405c4d3d99b3c3f42ad512d2.png)

当启用的该设置时，会使用RC4进行加密密码，而密钥存储在注册表中

使用PowerView枚举UAC为ENCRYPTED_TEXT_PWD_ALLOWED

```powershell
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}
```

## Kerberos Double Hop

![在这里插入图片描述](https://img-blog.csdnimg.cn/01dbeeb2bb6e4d04b878f450760c5066.png)

这个问题我们可能会遇得到，通过winrm进行远程连接时，只会携带winrm需要的tgs（http，cifs）进行连接，此时想要在目标上访问AD资源时，这将会显示拒绝访问。因为在这种情况下进行tgs请求时，由于它不会携带tgt,因为机器上可能没有，我们连接winrm的时候没有把tgt携带过去，所以后续我们无法通过kdc的tgs请求的tgt验证，所以我们无法访问其他AD服务。

1. PSCredential，通过powerview的-Credential参数传递凭据以访问服务
2. 注册新的会话配置

```powershell
Register-PSSessionConfiguration -Name backupadmsess -RunAsCredential inlanefreight\backupadm
Enter-PSSession -ComputerName DEV01 -Credential INLANEFREIGHT\backupadm -ConfigurationName  backupadmsess
```

## NoPac

创建一个与dc主机名一样的计算机账户，不带$后缀。使用此账户可以欺骗kdc，令其匹配dc的计算机账户，以获得dc访问权限。前提是我们的账户具有创建计算机账户的权限

## PASSWD_NOTREQD

设置了此UAC，则该用户将不被密码策略限制，这有可能为弱密码甚至是空密码

```powershell
Get-DomainUser -UACFilter PASSWD_NOTREQD
```

## GPO枚举

```powershell
Get-DomainGPO | Get-ObjectAcl | ?{$_.SecurityIdentifier -eq $sid}
Get-GPO -Guid <GPO Guid>
```

我们可以使用[SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse)来帮助利用GPO

## Trust

![在这里插入图片描述](https://img-blog.csdnimg.cn/3071574c01cb4603aa751d644e5ab05d.png)

```powershell
Get-ADTrust
Get-DomainTrust
Get-DomainTrustMapping
```

## 从子域到父域

### 金票细节

我们知道当域账户登录的机器时，通过sid生成access token，并使用该token确定所具有的权限。而具有SIDHistory也会参与token的生成。

当访问旧域时，sidHistory就会被添加到TGT的PAC的ExtraSids字段中，所以我们最终会具有该sid所具有的权限，这也是金票制作的核心，通过mimikatz直接伪造tgt，同时把PAC里的ExtraSids字段改成EA组的sid，这样我们就得到了一张**域间**（子域-父域）金票

所以很容易想到制作这张票需要什么：

1. 子域的sid
2. EA组的sid
3. 子域的域名
4. 任意用户名（可不存在，因为后续请求tgs时都能通过，并且通过sid确认权限）
5. 子域的krbtgt的hash

mimikatz

	kerberos::golden /user:hacker /domain:LOGISTICS.INLANEFREIGHT.LOCAL /sid:S-1-5-21-2806153819-209893948-922872689 /krbtgt:9d765b482771505cbe97411065964d5f /sids:S-1-5-21-3842939050-3880317879-2865463114-519 /ptt

### 在linux我们可以使用Ticketer.py制作金票

再通过ticketConverter.py将ccache转kirbi

## 林间双向信任

	Get-DomainUser -SPN -Domain FREIGHTLOGISTICS.LOCAL

只要指定一下域
