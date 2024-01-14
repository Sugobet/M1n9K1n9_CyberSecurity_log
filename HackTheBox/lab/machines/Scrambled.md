# Scrambled

最近身体有些不舒服，恐怕理论值要与现实产生较大偏差了

---

Scrambled 是一台中型 Windows Active Directory 计算机。通过枚举远程计算机上托管的网站，潜在攻击者能够推断出用户“ksimpson”的凭据。该网站还指出 NTLM 身份验证已禁用，这意味着将使用 Kerberos 身份验证。使用“ksimpson”的凭据访问“Public”共享时，PDF 文件指出攻击者检索了 SQL 数据库的凭据。这表明远程计算机上正在运行 SQL 服务。枚举普通用户帐户，发现帐户“SqlSvc”具有与其关联的“服务主体名称”(SPN)。攻击者可以使用此信息执行称为“kerberoasting”的攻击并获取“SqlSvc”的哈希值。在破解哈希并获取“SqlSvc”帐户的凭据后，攻击者可以执行“银票”攻击来伪造票并冒充远程 MSSQL 服务上的用户“管理员”。数据库的枚举显示了用户“MiscSvc”的凭据，该凭据可用于使用 PowerShell 远程处理在远程计算机上执行代码。当新用户显示一个正在侦听端口“4411”的“.NET”应用程序时，系统枚举。对应用程序进行逆向工程显示，它使用不安全的“Binary Formatter”类来传输数据，从而允许攻击者上传自己的有效负载并以“ntauthority\system”的身份执行代码。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ad112361-9fae-3ea8-a95a-b27f1c959923.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e185c54e-79b1-8842-0994-7e43984e2c6d.png)

禁用了NTLM身份认证

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/aa376831-02f4-95e9-3571-e65356edd63e.png)

在这里发现了一个username

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/850c0589-0e5b-f49c-91ce-55941ac82774.png)

初始密码策略

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9b7c7d6b-3c50-cd5d-4e4c-6cde2ded05f9.png)

### SMB枚举

请求TGT

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/41ed9b57-4ded-82ff-b935-0ee9e2df8493.png)

krb5ccache

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7a0a953f-be81-2f8b-8c93-c97a1c2030bf.png)

用kerberos协议拿ccache登smbclient

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fb8f2334-969b-ad4b-218b-567edbf720f0.png)

/public有个pdf，下下来

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a4155959-35e0-3ffd-41c3-27ab1f5d48a8.png)

### Foothold

提示与SPN有关

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c64f32fa-da37-a9ce-ebba-6036c7215f8a.png)

这里需要对GetUserSPNs.py[修补](https://github.com/fortra/impacket/issues/1206)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f198a9c7-99c2-c78d-4904-cc7b2136612b.png)

request

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/14ca694f-f1a1-cee5-803a-56e0dfbd18a2.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5c79f706-007d-b609-ecc2-f2d5ab634597.png)

hashcat直接爆

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cf959ddf-e96a-425d-9d1e-f9c7c9212dd3.png)

在/etc/krb5.conf中添加

```yaml
[libdefaults]
	default_realm = SCRM.LOCAL

[realms]
	SCRM.LOCAL = {
		kdc = dc1.scrm.local
	}

[domain_realm]
	.scrm.local = SCRM.LOCAL
```

kinit

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b9e82313-143f-654d-480b-5dceb0f592a5.png)

ldapsearch这里直接看wp配置了

	domain administrator sid: S-1-5-21-2743207045-1827831105-2542523200-500
	mssqlsvc nt hash: b999a16500b87d17ec7f2e2a68778f05

## 域权限提升

做DA的银票

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c44afa4a-ff1e-5e26-6b40-a5149ec3ff5e.png)

登mssqlclient

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c1d6510a-3fb3-063f-7a1c-508b14e69a75.png)

启用xp_cmdshell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/110f5a47-a9f0-de04-bfaa-b6461181ed99.png)

之前的靶机已经遇到过一次这种情况了，由于我们使用的是DA的ticket，所以我们可以通过mssql服务来模拟DA进行文件读取来读flag

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e5f8e2e3-495c-f2be-4ab1-177a708e0356.png)

getshell后应该也可以对sqlsvc打potato

这台机挺好的，就是身体不在状态
