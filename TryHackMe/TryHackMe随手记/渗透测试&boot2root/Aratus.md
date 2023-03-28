# Aratus

你喜欢读书吗？你喜欢浏览大量的文字吗？阿拉图斯有你需要的东西！

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/71ae33d318dd4ab0a8d9c98025f32119.png)

## FTP枚举

anonymous进到ftp，啥东西也没有

![在这里插入图片描述](https://img-blog.csdnimg.cn/36ae581573cd4473968782df755698e6.png)

## SMB枚举

smbmap看一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/e1dc9314dd56471d8d9f645be106d530.png)

进入这个可读的share

![在这里插入图片描述](https://img-blog.csdnimg.cn/c1c3ca3929ec42ec9a6a898bbe831424.png)

查看.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d77b7918e5c4696b57a849aaccc1304.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/0da96e5e7f544df78910990674f0e7bc.png)

获得两个用户名，以及重要信息，这说明Simeon的密码可能不安全，并且可能以未知的形式散落各处

还有一堆名字差不多的文件夹，数量比较多，先下载

```bash
smb: \> prompt off
smb: \> recurse on
smb: \> mget *
```

文件夹下还有几个子文件夹，子文件下都是txt，使用bash一句话读取所有txt文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/4cf0c30bde3e4ead81dcdf284202778b.png)

果然有东西

![在这里插入图片描述](https://img-blog.csdnimg.cn/15fa809b098d450ba8f6e79249af2848.png)

保存下来尝试直接登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/fb0b273272ca4d4882845b7bd734dbb5.png)

ssh2john+john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/a02b856d7fd24c4b953e78892b490dd1.png)

成功进来

![在这里插入图片描述](https://img-blog.csdnimg.cn/f84355457ca7406fba4bc03ed6b4747a.png)

## 横向移动

在/var/www/html/test-auth中的.htpasswd文件找到了另一个账户的密码hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/99959e820e4b4dc7bdc655a75df065d6.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/6c39a30d6a9a48a6877788340594beb0.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/71ff07b8d6934ea6b0442b6fe023c717.png)

但这个密码似乎没用

![在这里插入图片描述](https://img-blog.csdnimg.cn/94b7d87a3ed44797ac5d986e32023bab.png)

阅读test-auth下的index.html

![在这里插入图片描述](https://img-blog.csdnimg.cn/905a51323c224627b15aba46742371cb.png)

不知道它在暗示些什么，难道是要我传脚本过去吗

找了很久，都没有什么发现，于是看了眼wp

这里需要利用pspy

pspy 是一个命令行工具，旨在窥探进程而无需 root 权限。 它允许您查看其他用户运行的命令、cron 作业等。当他们执行时。 非常适合在 CTF 中枚举 Linux 系统。 也很高兴向您的同事展示为什么在命令行上将机密作为参数传递是一个坏主意。

该工具从 procfs 扫描中收集信息。 Inotify 放置在文件系统选定部分的观察程序会触发这些扫描以捕获短期进程。

将pspy通过curl传过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a7ebf60d0a7460bb3e60993f72504f5.png)

运行它，观察到会有个py脚本在定时运行

![在这里插入图片描述](https://img-blog.csdnimg.cn/2bab29b14a6646c480e20300435c83ac.png)

这个脚本名称跟我们刚刚从/var/www/html发现的那个文件夹，目录名相似度99%，如果站在脚本开发者的角度，将test-auth的index.html那句话联系起来

或许这个脚本的功能就是用于测试curl是否能用又或者说测试网络是否连通，而pspy当中还有一个ping，这让我更坚信这个想法

使用tcpdump抓包

![在这里插入图片描述](https://img-blog.csdnimg.cn/976fce29f7484cc6bd10290dc5e2131b.png)

base64解码，得到了另一个账户的明文凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/affd0704ab1d4d32a58ead54c46551a8.png)

su过去，成功拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/b232769f09b642febe458342b90ba2d6.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/6a1de69fb11e435ab7d1260ee96a3056.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/030501b3798a4f1f8a2d88fed3180363.png)

playbooks下有些这么些文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/bd9c7c9a27654a018e5f18b82ca2dc17.png)

读取其中一个，发现有个roles

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4865bc94f60436a8d368736d7876a77.png)

在上级目录下也有一个role文件夹，过去那边看看，也有相同名字的目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/c8054147f9e9486792b373bf9bbbb499.png)

在该目录下有个tasks，然鹅上面那个文件里面也有, 名字是配置防火墙

![在这里插入图片描述](https://img-blog.csdnimg.cn/40a642f42edf4a10b171849ee2d5e40f.png)

查看tasks目录时发现有个文件权限跟其他文件与众不同，并且这些文件名都附带了一些系统名，我立刻查看了当前靶机系统是什么

![在这里插入图片描述](https://img-blog.csdnimg.cn/edaef95dcdd64bb3a2018b0e7b338066.png)

这一切说明与那个可疑文件名有联系，可以大胆猜测，当这个程序执行时，会在tasks目录下寻找相应系统的yml

那么问题来了，那个“+”是什么东西呢，让大牛来解答一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/6d47cbc0fff041a2a68148ec0d3e9fe9.png)

根据大牛的解释，能看出linux的acl应该类似于windows上的acl，知识+1

使用getfacl查看一下这个可疑文件的acl

![在这里插入图片描述](https://img-blog.csdnimg.cn/625509983a2d4e44b3006068c4d7ff26.png)

果然，我们当前用户theodore可写

查看该yaml文件，可以执行命令，直接改，这里似乎无法执行多段shell命令，所以写个bash脚本

![在这里插入图片描述](https://img-blog.csdnimg.cn/455de6c3b2934f208db0ab807b621d74.png)

修改配置文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/4a1f7161293642698b35da18ccbc5417.png)

然后sudo

![在这里插入图片描述](https://img-blog.csdnimg.cn/b4aae5302e4e408180e0205813912385.png)

**注意，这里需要使用theodore的凭据通过ssh重新登录，否则这里sudo似乎将无法正确执行**

![在这里插入图片描述](https://img-blog.csdnimg.cn/868485e1c62f4313a461b9e0a4c3520f.png)

竟然是root的suid

![在这里插入图片描述](https://img-blog.csdnimg.cn/6ff408cc942848b39b57052c716c0a53.png)

结束