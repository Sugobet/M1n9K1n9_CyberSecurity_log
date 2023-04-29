# Mnemonic

I hope you have fun.

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/d6314716a5984f138e7ccda637f4f0d6.png)

## FTP枚举

尝试anonymous

![在这里插入图片描述](https://img-blog.csdnimg.cn/cf22ffce1abc46febe4392fb33edd599.png)

## Web枚举

进80

![在这里插入图片描述](https://img-blog.csdnimg.cn/30d79b3efe3c448d930adb48385fbdb7.png)

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/79a1313ae1ec41fd9abc1c1d50918113.png)

对着webmasters再扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/2d067a97752e4991a5a6270bad70402c.png)

对着backups继续扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/cdaa4dfbeb954ccca75cecb061db0f59.png)

下载zip文件，发现有密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/fd9aae2442894a1a9475f0301c683b61.png)

zip2john + john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/199118036aa1429ab8cfe3b342d8d625.png)

查看note.txt, 给出了ftpuser

![在这里插入图片描述](https://img-blog.csdnimg.cn/525c1bea3ac6447c82e9ffb823fafd0c.png)

hydra直接爆ftp

![在这里插入图片描述](https://img-blog.csdnimg.cn/de8047c63ac8475babae4b9f84ec1804.png)

进到ftp

![在这里插入图片描述](https://img-blog.csdnimg.cn/d9e4a97bdfec444f904ff83ecf087e23.png)

用wget下载所有文件夹和文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/16b75106d1cc448fa785711de6df0af9.png)

发现了id_rsa和not.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/a355283da88b42a9872f62d45c66dafc.png)

not.txt

	james change ftp user password


这应该是james的ssh私钥，尝试直接登

![在这里插入图片描述](https://img-blog.csdnimg.cn/7b870f1ad8a340d6916f79eae39affba.png)

ssh2john + john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/405cf054b44d4576b0abd8c977de522f.png)

直接登录发现，ssh私钥的密码就是james的密码

## 横向移动

进来发现又有rbash限制

直接bash获取bash

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a9ebc50da9143a5991ad2e9347c4594.png)

noteforjames.txt

	james 我发现了一个新的加密 İmage based name is Mnemonic
	
	我创建了神鹰密码。 别忘了周六的啤酒

6450.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/cdd57a4d3b0c420e8d65746749151358.png)

当访问/home/condor时，被拒绝了访问，但仍然得到了两串base64的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/430b1e3bd87c4946bfe8c65377446a6a.png)

解码得到一个flag和图片名

![在这里插入图片描述](https://img-blog.csdnimg.cn/26e708074710466fb8d27bfec08d8034.png)

联合上文的noteforjames.txt，在谷歌搜索İmage based name is Mnemonic

找到了它的github

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e94e92f20164e4d9ceb8d3b6afde640.png)

直接clone下来

![在这里插入图片描述](https://img-blog.csdnimg.cn/43850132b21d42e4b888256431470852.png)

注意需要在脚本添加一行代码，否则会报错

	sys.set_int_max_str_digits(9999999)

![在这里插入图片描述](https://img-blog.csdnimg.cn/4da020a512814c1998346fe2e679140f.png)

运行脚本

![在这里插入图片描述](https://img-blog.csdnimg.cn/7eff9946dc0d44f79f9d51eadbb04aea.png)

前面获得的6450.txt是一堆数字，它应该就可以用来解密，得到了condor的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/3ae432b373454303baf6abbb85ec959d.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b0f8723c8be4153877eb8bb4d591297.png)

查看此文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f4c4f6168ee40bda81623ca91d6203b.png)

值得关注的是这些代码

```python
		if select == 0: 
			time.sleep(1)
			ex = str(input("are you sure you want to quit ? yes : "))
		
			if ex == ".":
				print(os.system(input("\nRunning....")))
			if ex == "yes " or "y":
				sys.exit()
```

很简单的逻辑

![在这里插入图片描述](https://img-blog.csdnimg.cn/ec0ee24341844bc0bfb3c8708f162db4.png)

直接getroot，拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/cd4bcded306140afbf32febfd243b8be.png)

这里还需要对flag的内容进行MD5才是真正的root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/d5e332637bf742b391c33267ab8b8c4b.png)
