# Include

使用服务器利用技能来控制 Web 应用程序。

## 外部主动信息收集

### nmap

循例nmap

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e876372cc79948589c16a3bc4dd16e9d.png)

## Web枚举

### 4000端口 - 目录扫描

feroxbuster扫

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f4b4607c547245c4a89a6439b908786d.png)

### 50000端口 - 目录扫描

feroxbuster扫

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a82f04eb2f69417d88d4e8e23cb19920.png)

### 4000端口 - 越权

可以通过直接修改url的id访问到其它用户信息

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/12885feabc1841d9be6c50c4f840b3d5.png)

不过这并没有提供更多信息，但有一个引人注目的字段属性`isAdmin`

但很遗憾我们已知的三个用户都不是admin

经过id枚举也依然没有枚举出更多用户

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d1e987ac36f4409ca7061579e47a6655.png)

在profile的最下面有一个表单，随便输点东西并提交它，发现可以新增字段，并且可以修改原有的字段

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/7d6ed6e516334dfb94303c55b59556af.png)

那么接下来就是常规操作，直接修改guest的`isAdmin`字段为true，看看权限是否发生变化

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/081372863bb0493aade4ad0410bfc977.png)

当我们刷新页面后，我们的页面右上角将会出现我们期待的东西

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/efbda1ebd6d742628e692511762b8fde.png)

## SSRF

有个开在内网的api

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5362458ee2af41afbe6270713f6127c8.png)

在setting中可以看到可以设置url，服务端将访问url下载image

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a8420e853b9f4344aac42fda5b9267f9.png)

随手开个nc，没有问题

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c52af4817745453986f95419f3684aa3.png)

给个.php文件，发现它把文件内容读了出来，并且进行base64

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0aca744798974cf897d3ccd6c67098fa.png)

那么思路也很显而易见了，直接访问internal api获取administrator的密码

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a424f07a481a4592a6bcdf983847d262.png)

有了它我们能够访问50000端口的sysmon，同时拿到第一个flag

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f7e97a06464f49bda27b384858a4ada4.png)

## LFI -> RCE

burp logger可以看到profile.png图片是通过文件包含出来的

但这里有过滤，不过只是简单的进行了两次的`../`replace，进行三次`../`就能绕过去

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/fa93dea9310847d1881a1ec283a2f94b.png)

但没有日志

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/671fe5214c0a4275b5b8b33fbfc2ccbf.png)

### RCE

在最初的端口扫描中，存在smtp、pop3、imap那一堆服务，并且在最开始我尝试用户枚举但并没有什么结果

现在我们可以尝试读smtp的日志文件`/var/log/mail.log`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/282a0f87eef84963998ccfcd529a09c4.png)

没有问题，接下来就是常规的登录恶意用户名达到控制log文件内容从而实现rce

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/9813c3501ac0493281b059eff2623928.png)

php代码能够被解析

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/05a61cd04b3d43ada76faf2889861432.png)

直接读flag下机

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4dbdbccdbbec4a1faa21a9bdd1d875ab.png)
