# Year of the Fox

你能熬过狡猾的狐狸吗？

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/8ede88899ea84e00aa01e22bfad68578.png)

有个域名，加入hosts

## SMB枚举

smbmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/a3be80d68774494fbdf0ffce41595bd7.png)

enum4linux -a，枚举到两个账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/14c0daedaca24dedb1368c0231495099.png)

## Web枚举

进80发现需要登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/c0c902fa2f9844d6b185880ad85a7c57.png)

上hydra

![在这里插入图片描述](https://img-blog.csdnimg.cn/6169171581bc45ad9f4b06f9f2015814.png)

## RCE to Getshell

进来可以查看一些文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/5e99c9e019a24624ae9da46a07d29feb.png)

bp发现这里存在过滤

![在这里插入图片描述](https://img-blog.csdnimg.cn/0b50e5344d9b441cacd44f4f355c7d57.png)

burpfuzz一遍，只有两个字符进黑名单

![在这里插入图片描述](https://img-blog.csdnimg.cn/ed478639774d40079af82d658a98f106.png)

通过\\符号逃逸出双引号再利用\\n换行，然后执行我们的命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/51f7175a29724931acae5d2bc218c96e.png)

事后查看源码

![在这里插入图片描述](https://img-blog.csdnimg.cn/82c95c7ed1e148d2829947a556b51b40.png)

本机复现命令大致是这样：

![在这里插入图片描述](https://img-blog.csdnimg.cn/7e9b6b19938c4aaa94ea4f3dc2a21dd5.png)

我们首先\\"逃逸了双引号，但由于后面还有一个*符号，会导致xargs执行不成功，所以需要换行一下，也可以直接添加;符号来绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/0251c627f9d54356b8f65c3b7552ec63.png)

由于&被过滤了，并且靶机似乎没nc，mkfifo的payload get不成功，这里可以通过base64来绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/c018036fa72b40158ddfc2bcd16c803a.png)

reverse

![在这里插入图片描述](https://img-blog.csdnimg.cn/fc72b86165f745a6b134c5da3ebdc158.png)

getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e5c2b4fdd974af1a9b55fcec3bcac84.png)

web flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/1f255124caba46f69c8da426911bacbb.png)

## 横向移动

查看/home发现有刚刚的两个用户，我们已经获得了rascal的密码，尝试通过su过去，发现居然没权限，并且ssh开在了内网，并且靶机内的ssh也无权使用

![在这里插入图片描述](https://img-blog.csdnimg.cn/7f7883011bb2442fac703c9493162321.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/8eecacfa7b6046698bcab3599fd0a5ed.png)

这里需要做一下端口转发，在现在这种环境下，socat应该是最适合的（其实我的linux武器库也只有这个东西能做端口转发，除了frp和chisel外）

![在这里插入图片描述](https://img-blog.csdnimg.cn/64966ff906ca40bab2fa195fd68fbcc4.png)

登录ssh，但密码却不对

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf01c977e74e48dab8bd528a51d6046f.png)

rascal似乎爆不出来，尝试爆破fox

![在这里插入图片描述](https://img-blog.csdnimg.cn/5e7f84a9158c41ac8dec4c4df3b9d72c.png)

直接登ssh，拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/2d5afdf02dff4639b097033e14b5c17e.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/854139def6ed4b5eb3ec51d8f631d875.png)

靶机缺少工具，把shutdown下载回攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/fcea2500e809463fb38be8dad0555266.png)

strings和ltrace，发现以相对路径调用了poweroff

![在这里插入图片描述](https://img-blog.csdnimg.cn/7e7d55312827464f8b94a41f71ac61a1.png)

还是老思路，直接改path

先创建poweroff

![在这里插入图片描述](https://img-blog.csdnimg.cn/595f60f3b5444ef2b9f0fcc446531b3b.png)

改path变量

![在这里插入图片描述](https://img-blog.csdnimg.cn/53a4ed52b9ee431eac0c93bbca348379.png)

sudo执行

![在这里插入图片描述](https://img-blog.csdnimg.cn/fcad25ff9ee54372811a255edfa86ebc.png)

然而root flag不在root

![在这里插入图片描述](https://img-blog.csdnimg.cn/637286f0fc3940619f4e2644a11d87c0.png)

在rascal的家目录下找到了它

![在这里插入图片描述](https://img-blog.csdnimg.cn/eda50f7f63a647a78294ea1debdc45d0.png)
