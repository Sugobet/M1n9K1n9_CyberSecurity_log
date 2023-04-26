# CMSpit

你已确定 Web 服务器上安装的 CMS 存在多个漏洞，允许攻击者枚举用户并更改帐户密码。

您的任务是利用这些漏洞并破坏 Web 服务器。

---

## 端口扫扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/2738205c65e542e09223f85207e2978e.png)

## Web枚举

进80

![在这里插入图片描述](https://img-blog.csdnimg.cn/a65a3e011f7048e9b54791ff67eb9a3e.png)

很明显，cms就是Cockpit, 版本通过查看源代码的js版本可以得知是0.11.1

![在这里插入图片描述](https://img-blog.csdnimg.cn/fddd347c2df14a69b0322e71f41296df.png)

searchsploit发现有几个洞

![在这里插入图片描述](https://img-blog.csdnimg.cn/ff89a935cedf4c0ea5904e35045c3a5f.png)

查看exp是存在sql注入导致的数据库信息泄露，从而能够利用账户信息来进行重置密码之类的操作

![在这里插入图片描述](https://img-blog.csdnimg.cn/ee713fc0ecab45bbb9005b476f9d8e31.png)

直接运行它得到四个账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/4633fb2e2ade4c81bcf001c853a94475.png)

继续利用其重置admin的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/97e9f454a1c244b2832bad45abef3b5f.png)

直接登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/921b19fefe2d43bfac8a80c0b6832b56.png)

在后台左上角可以找到assets, 在这里可以上传文件，直接传个一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/197410b813c6430fbf38c92ff9b5604f.png)

能够被执行

![在这里插入图片描述](https://img-blog.csdnimg.cn/b0889477a11e46c5ba288d0b60045321.png)

python3可用，直接pythongetshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/93fe97d1ccec4f6a8f33de5c954aa500.png)

web flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/1d87b42ae0ee493baadac5bd20639249.png)

## 横向移动

发现27017端口在监听，那是mongodb

![在这里插入图片描述](https://img-blog.csdnimg.cn/99105bc4b8a345a38fea210ee47776f1.png)

mongo进入命令行在sudousersbak库中存在flag集合，直接拿到secret flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea8a43b75a674f2abd1efec496e7c6ba.png)

在user集合下有一组明文的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/9e72f63db528456e842a37c23dbd1818.png)

直接登ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d9b91419eab45928d1a0c3dea672de4.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4538c317186470ead22fba5757f2fb3.png)

## 权限提升

查看sudo -l, 有一个exiftool

![在这里插入图片描述](https://img-blog.csdnimg.cn/a609af566a1741679b4e5857ced40f44.png)

searchsploit发现一个洞, ExifTool 版本 7.44 及更高版本中 DjVu 文件格式的用户数据中和不当允许在解析时执行任意代码

![在这里插入图片描述](https://img-blog.csdnimg.cn/8908f7b428354a0eadad54507c7a39e7.png)

由于靶机的python3是3.5的远古版本，不支持f-string，需要自己对exp进行一些修改

![在这里插入图片描述](https://img-blog.csdnimg.cn/81784e21a41040e0ab34711a23678607.png)

命令能够被成功执行

直接cp bash

![在这里插入图片描述](https://img-blog.csdnimg.cn/03ec4e2acfa04cf7a39bee3d2fd15e27.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/251d8a79550c487db1652e9c5422ece1.png)

getroot
