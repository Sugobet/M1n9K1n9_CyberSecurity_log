# Year of the Pig

有些猪会飞，有些有故事要讲。开始吧！

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/1f5368037bb943819e386d09953c4efb.png)

## Web枚举

进入80

![在这里插入图片描述](https://img-blog.csdnimg.cn/534721ec42e44727875ab5bf5d885167.png)

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/d08831fd246c483d9298c0ea3ed9a852.png)

进到/admin，尝试弱口令，给出了密码提示

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f7d2c95afa3453f86dd3608f08d4e9c.png)

密码本身的一些很简单的单词，密码的后三位是两位数字加一个特殊字符

我们利用cewl去爬取网页，获取单词表

![在这里插入图片描述](https://img-blog.csdnimg.cn/90eeeb34603a4bddb4ae067dbbac5854.png)

这里可以利用john的rule去生成字典

![在这里插入图片描述](https://img-blog.csdnimg.cn/39bc803e7b174ddbac64af254d222b3e.png)

生成保存

![在这里插入图片描述](https://img-blog.csdnimg.cn/ebc47f8be1e946998e6874928b92303f.png)

由于登录时密码是经过md5的，那么我们也需要对明文密码字典处理一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/b0d3859173fb4a16a4238f0d230b0a7c.png)

python把明文密码给MD5，由于区分大小写，默认获取的字典爆了没爆出来，于是进行全小写

```python
import hashlib


f = open('pass.txt', 'r')

for pwd in f.readlines():
	obj = hashlib.md5()
	obj.update(pwd.strip().lower().encode("utf-8"))
	print(obj.hexdigest())

```

![在这里插入图片描述](https://img-blog.csdnimg.cn/c6ce4564177e4ecf9125a87217fa0bdd.png)

hydra在这里似乎有些问题，直接换ffuf

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c1e922640284a89bd069a9834260d27.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/5bbbd12f4e6e46a9be3d57b8e4cece0d.png)

修改一下python脚本，让他把明文密码也输出出来，直接拿着hash去比对

![在这里插入图片描述](https://img-blog.csdnimg.cn/af9ef59670ab4e6c9a4abed4bc501c48.png)

登进后台，可以执行命令，但有限制，getshell似乎几乎不可能

![在这里插入图片描述](https://img-blog.csdnimg.cn/861a04035baa4bf29e241adbb3f9f64e.png)

拿着marco的凭据，尝试登ssh, 成功，同时拿到flag1

![在这里插入图片描述](https://img-blog.csdnimg.cn/9dae66caf4a24c93afb8cbf81802d612.png)

## 横向移动

查找marco所在的web-developers组有权限管理的文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/ae77eea8776943d9b4cf25aa33fa64bc.png)

显然整个Web我们都有权管理

/var/www下有个db，想必里面就存放了另一个账户的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/1b3bcc97ac3f47f2aa04cef1d0bf6443.png)

但该文件不归我们所有

除了数据库文件以外，其他Web的文件我们基本都有权限读写，而web服务是由www-data用户启动的

这意味着我们可以直接往网站根目录写shell.php，然后获得www-data的shell，再读取db文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/c27ad87a90e9425b8d678430c2271a5f.png)

利用she11.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/1318a34ea7fc4dc8bb968f85e5f5da4e.png)

给admin.db个777的权限然后这个shell就可以丢掉了

![在这里插入图片描述](https://img-blog.csdnimg.cn/7040b2fa082944e1baaa8bbe9f062222.png)

开启http服务把admin.db传回攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/ced53d52d5024badac2f494f3c91b631.png)

拿到curtis的md5 hash，直接用CrackStation秒出

![在这里插入图片描述](https://img-blog.csdnimg.cn/91fbdcb20e4947b4857e702caf75e9fc.png)

直接su过去，同时拿到flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b88f5bae1f540d29dfdc3b239d41417.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/91b2449ed9dd48f8a0c4de6d65603092.png)

很简单的提权，我们需要先回到marco，因为只有它我们才能再/var/ww/html下操作

创建两目录，然后ln创建个链接文件指向passwd

![在这里插入图片描述](https://img-blog.csdnimg.cn/3c7817da4de34fa39c9e9222bace7e53.png)

openssl生成密码hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/55d5d51a32ce486c8e45bef94ec4c808.png)

利用sudoedit，添加账号

![在这里插入图片描述](https://img-blog.csdnimg.cn/7418ab56238444d4af2313167d8e3f7c.png)

保存退出，直接su过去，成功拿到root

![在这里插入图片描述](https://img-blog.csdnimg.cn/ee2631aae13e43c68abf9c419bb0075f.png)
