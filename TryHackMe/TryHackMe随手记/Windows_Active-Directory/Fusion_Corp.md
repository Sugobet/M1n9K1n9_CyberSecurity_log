# Fusion Corp

你不久前与Fusion Corp联系。他们联系了你，说他们已经修补了所有报告的内容，你可以开始重新测试了。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/9d0b17b27640409fb42f738d510032b5.png)

将fusion.corp域名加入hosts

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf9cd5cb8bc443929ff965e4b3098b34.png)

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/8941d1de67024513b3bf73c9ee3e66fd.png)

访问backup

![在这里插入图片描述](https://img-blog.csdnimg.cn/b91299a08b2b421c869021867bc86641.png)

下载该文件，打开发现是一些用户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/54c836e46ee84c82a4063d5d82e36b1e.png)

保存下来

## 立足 - AS-REP Roasting

由于web站点上除了一个用户名列表也似乎没其他东西了，smb也没东西，通过用户名，能联想到的必然是as-rep roasting

通过刚刚收集的用户名，使用GetNPUsers.py

![在这里插入图片描述](https://img-blog.csdnimg.cn/2241cdda9cf0491e8a85a59ddb691821.png)

获得了lparker账户的hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/4054fed3c9834f4aa5b440b3a363a3a8.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/762c70a81bfb4e5a80e5ee4ff6a5cf1c.png)

直接登winrm，同时拿到flag1

![在这里插入图片描述](https://img-blog.csdnimg.cn/2238d3937ab04c8f858590d04c958312.png)

## 横向移动 - ldap枚举

ldapdomaindump转储

![在这里插入图片描述](https://img-blog.csdnimg.cn/7631acb924494d1597a94d5c177d2993.png)

jmurphy账户的desc给出了密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/331e10b0b07e46258b77c22f567120ae.png)

evil-winrm直接登，同时拿到flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/23e5a12db85740c8907e0e733ed10edf.png)

## AD利用

查看whoami /groups，发现我们在backup operators组中

![在这里插入图片描述](https://img-blog.csdnimg.cn/2312e6f1b84d4e449cd0b5d4e439096a.png)

直接从本地注册表转储sam和system

![在这里插入图片描述](https://img-blog.csdnimg.cn/020e29c4ff2b4d78acd818d902980fea.png)

攻击机开启smbserver

![在这里插入图片描述](https://img-blog.csdnimg.cn/db398306c60748c295725cbacda2028f.png)

把sam和system文件下载回来

![在这里插入图片描述](https://img-blog.csdnimg.cn/91b1b6884e4c4abf88947bb3d598380a.png)

secretsdump转储

![在这里插入图片描述](https://img-blog.csdnimg.cn/55d170a81db74261b28bd4699552eae0.png)

pth登admin，本地管理员登不进去，我想我们需要ntds

使用diskshadow

脚本内容：

	set context persistent nowriterss
	set metadata c:\windows\temp\metadata.cabb
	add volume c: alias someAliass
	createe
	expose %someAlias% d::

运行diskshadow

![在这里插入图片描述](https://img-blog.csdnimg.cn/1760f54c037648b9bf4864c498d7ef73.png)

利用robocopy使用backup的权限复制ntds.dit

![在这里插入图片描述](https://img-blog.csdnimg.cn/db6551cc9aa24f93b57cf4ace3d4ca1e.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/98729576749441a79f354b8aaa877e01.png)

把ntds.dit传回攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/b69ca03c0f0b4783b556e5c22b12426e.png)

secretsdump提取hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/66dc93df862d4acab747b9e9bf3ef53d.png)

拿DA的ntlm hash直接登

![在这里插入图片描述](https://img-blog.csdnimg.cn/951eeb19906d435287b955e772289a4e.png)

flag3

![在这里插入图片描述](https://img-blog.csdnimg.cn/2b7be9b19bb141718dd68f07b7bf524c.png)
