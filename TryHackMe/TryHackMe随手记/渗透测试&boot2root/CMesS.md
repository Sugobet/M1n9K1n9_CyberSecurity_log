# CMesS

你能扎根这个吉拉CMS盒子吗？

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/c9c1f71ee3be4d33a95b96c1cf24d8f6.png)

## Web枚举

进80端口http

![在这里插入图片描述](https://img-blog.csdnimg.cn/fba1fa76958c4023b55051ccd7431931.png)

没什么信息

### 目录扫描

gobuster开扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/0de81f5b602e4cad8fc85fb1ad94c8d8.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/7e595d40abb245de904eed8b5b313dd9.png)

虽然有很多，但是并没有获得许多有用的信息，admin登录需要使用邮箱，这无疑是增加了枚举难度

![在这里插入图片描述](https://img-blog.csdnimg.cn/f82cf369a026414f902396e6414177ef.png)

### 子域枚举

这里thm开局给了域名，循例也得该扫扫子域

![在这里插入图片描述](https://img-blog.csdnimg.cn/02072c35ab144d33a4c5cab48f3967e5.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/ab5c8eac9aad4c47a497cf65ef49dd0b.png)

将其添加进/etc/hosts

## Reverse Shell

访问这个子域，这是一段对话，并且在从中发现一组凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/537d09aec484491583e2dd0a3827356e.png)

在刚刚的admin登录进去

后台有个任意文件上传点，直接传个reverse shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/d0fa4fe5c43c4ef38204b90850c2f51a.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/f95ee9882fdd408dabe63c83188d7110.png)

getshell

## 横向移动

升级shell

	python3 -c "import pty;pty.spawn('/bin/bash')"

简单枚举一下, 在/opt下发现了password.bak

![在这里插入图片描述](https://img-blog.csdnimg.cn/0b1345d30eae4e80be374ffd49802d1a.png)

利用此密码移动到andre并拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/fff933a5542e46288eb305f70465bb36.png)

## 权限提升

crontab

![在这里插入图片描述](https://img-blog.csdnimg.cn/889525be47c948e5b3e2e0c4fce098f0.png)

还是老熟人tar通配符注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/d7b2082ef0fe41149530e2b1579c941b.png)

hack.sh

![在这里插入图片描述](https://img-blog.csdnimg.cn/f418532dc88b4e3e97752e42b042e539.png)

静等一小会，带root的suid的bash就出现了

![在这里插入图片描述](https://img-blog.csdnimg.cn/01f400cf32f84e8a97f6c56bb80f7078.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/14502854b3bf4d9680486cbc0346d020.png)

getroot