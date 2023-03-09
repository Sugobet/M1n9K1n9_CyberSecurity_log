# Lockdown

停留在 127.0.0.1。穿255.255.255.0。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/269da10a2a9f49ae8178cefd34e5fec7.png)

## Web枚举

进入80

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea1b3e6cffda4dbf9cefa9b3a7d021c9.png)

发现跳转到了contacttracer.thm，将其添加进/etc/hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/eef893339e3a40c58f8e7c638aed2768.png)

这里试了一下注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/43ebd3f7ca4940d8875a3c77c8d33c11.png)

结果这就进去了

![在这里插入图片描述](https://img-blog.csdnimg.cn/38669c5a0efd480ab3aaad1fa8df62e3.png)

在后台逛了一圈，最后还是把目光放在了图片上传点

![在这里插入图片描述](https://img-blog.csdnimg.cn/ef0afd5716e942818db450ce01cabb63.png)

试了一会，貌似是上传上去了，但是找不到文件放哪了

，先上传一张正常的图片，然后到处找找，退出登录后，在主页找到了

![在这里插入图片描述](https://img-blog.csdnimg.cn/c9574d8bab7f433499cacff1e72d4b2b.png)

现在就可以上传php reverse shell，然后退出登录访问主页

这里又有一个坑，必需在后台点击右上角的设置这里上传才行，否则不生效

![在这里插入图片描述](https://img-blog.csdnimg.cn/aec3ebf16a7348a7bb51e25ce71d4b48.png)

成功getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/6c9b49baaa5347c89374b1dcbca1aa13.png)

## 横向移动

在家目录下的config.php一路跟到了classes/DBConnection.php

并发现了数据库的明文凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/6920b35771f647a9b2272ea460d4a01a.png)

这里先加固shell然后直接进数据库

![在这里插入图片描述](https://img-blog.csdnimg.cn/febdbf3069794cd292b7c58ef6041289.png)

在users表找到了md5加密的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/f7e50c5239e54781bf82bdefbc6d489e.png)

**注意，如果你在users表里发现password字段是空的时候，只需要重开靶机就可以解决**

### hashcat

hashcat直接爆，秒出密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/b9ecb56ffaa0406fbb841186422fb6fb.png)

这里ssh只允许使用key登录，所以直接在shell进行su

![在这里插入图片描述](https://img-blog.csdnimg.cn/4ef43768e86142adbde4d25e489ad7cb.png)

## 横向移动 - 2

查看.bash_history

![在这里插入图片描述](https://img-blog.csdnimg.cn/ad630dc964de4436966bc71334663c20.png)

查看scan.sh

![在这里插入图片描述](https://img-blog.csdnimg.cn/324470aad2754b16bd5dc6d026138bb5.png)

在clamav官方文档中找到关于对--copy参数的解释

![在这里插入图片描述](https://img-blog.csdnimg.cn/2ed092f3b4094b6292eb2fab7610faa7.png)

那么现在我们就有了一个大体的思路：由于这个脚本是root权限执行的，只要让clamav将我们期望的文件被clamav识别成病毒，那么clamav将会复制这个“病毒文件”到/home/cyrus/quarantine下，从而造成**任意文件读取**

在文档中给出了如何使用yara规则来进行字符串扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/ca05a7b453a3408ab7785a7946380729.png)

根据clamav的实例，写一个rule，然后读取/etc/shadow，正常shadow里肯定有root:

	rule CheckFileSize
	{
	  strings:
	    $abc = "root"
	  condition:
	    $abc
	}

将其写到/var/lib/clamav/rule.yara

查看/home/cyrus/quarantine/shadow

![在这里插入图片描述](https://img-blog.csdnimg.cn/35b6ce0c6bd64c23bd51c5a42db69f3f.png)
拿到maxine的hash直接上hashcat

![在这里插入图片描述](https://img-blog.csdnimg.cn/c94fd655151b4e38a19f5ce9697f234b.png)

直接su过去


## 权限提升

查看maxine的sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/fae1baa998ce4f29be328f4a749f0856.png)

辛苦这么久，终于可以轻轻松松结束房间了

![在这里插入图片描述](https://img-blog.csdnimg.cn/34f925dfe79246a4aa8bcaa8856e6054.png)

getroot
