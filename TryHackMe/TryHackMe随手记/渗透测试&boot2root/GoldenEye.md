# GoldenEye

这个房间将是一个有指导的挑战，以破解詹姆斯邦德风格的盒子并获得根。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/47c9f374184a4a878e0d67563045cb84.png)

## Web枚举

进入80

![在这里插入图片描述](https://img-blog.csdnimg.cn/9d6efd7bdaa34058a23df846d8604e27.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/79e61322f0ef45179a54cb33a908ec23.png)

查看terminal.js

![在这里插入图片描述](https://img-blog.csdnimg.cn/730ed147b42447799e700047f8d38b69.png)

拿去cyberchef解码

![在这里插入图片描述](https://img-blog.csdnimg.cn/c99a979b5ddc492987c7753ee9a87a7a.png)

拿着这组凭据到/sev-home登录

高清星际大战

![在这里插入图片描述](https://img-blog.csdnimg.cn/a05048fb9e434a41b8cae9dca269f6b0.png)

## POP3枚举

使用刚刚的凭据尝试登录pop3

![在这里插入图片描述](https://img-blog.csdnimg.cn/39e74e9806724cbcbd1324d49634ce46.png)

使用hydra尝试爆破

![在这里插入图片描述](https://img-blog.csdnimg.cn/c199d614b0734f38b9f0619d3b76ed7c.png)

这里用hydra爆了两个小时，rouckyou爆不出来，当前也没有其他密码字典，那只能直接看一手wp

	natalya:bird
	boris:secret1!

用telnet连接进去查看boris的邮箱

![在这里插入图片描述](https://img-blog.csdnimg.cn/391dc5e7486540a9958ae3baad173541.png)

在natalya的邮箱下发现了一组凭据和一个域名

![在这里插入图片描述](https://img-blog.csdnimg.cn/6746e1139c984acd8909b985d66e80a7.png)

将域名添加进hosts

## WEB

访问

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd9bfc7f91614ce1962124fe9572afee.png)

一模一样的站点，拿着刚刚获得的凭据到/gnocertdir登录

发现一个新账户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e64cd861e8847658785f1eda4151332.png)

题目引导我们爆破pop3

![在这里插入图片描述](https://img-blog.csdnimg.cn/90624f8039a8415783de56005fe18046.png)

登录过去，发现一个txt文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/af1449d66a3440d2ad8b8812a4ee30b1.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/44ab171387f44a7f8b0f58fd4d00401e.png)

下载这个图片，利用exiftool查看

![在这里插入图片描述](https://img-blog.csdnimg.cn/f9c8e659f52c41f2ba87528e078fa179.png)

将base64解码，得到密码，这大概就是admin的密码，尝试登录admin

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4cfa130e4204077b2cc2559f5003da1.png)
## Reverse Shell

admin有权限做更多的事情

![在这里插入图片描述](https://img-blog.csdnimg.cn/f75df36202354904b6ec9393550fd2c2.png)

在这里能够执行命令，利用python getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/df2277d126b24760b406fb784bb65b4f.png)

这两个设置到位

![在这里插入图片描述](https://img-blog.csdnimg.cn/309fc6ece85f43c7aa3815a07db14261.png)

new entry点一下这个按钮

![在这里插入图片描述](https://img-blog.csdnimg.cn/20d12bda7ce24d069ca903a1b27b003c.png)

getshell

## 内核漏洞提权

查看uname -a，使用searchsploit搜索相关漏洞

![在这里插入图片描述](https://img-blog.csdnimg.cn/5d63ce3e345d4556bb2be8891cec9766.png)

由于靶机里没有gcc，但exp又需要使用到gcc，这里需要修改exp的gcc为cc或clang

![在这里插入图片描述](https://img-blog.csdnimg.cn/a25ae3c9188f4e03a798f7c69aeb2f2d.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/69fcc9440a9c469282463483341e2847.png)

编译后添加执行权限，并运行

![在这里插入图片描述](https://img-blog.csdnimg.cn/3c100141165b42c88513250bd3f82887.png)

root flag还在老地方