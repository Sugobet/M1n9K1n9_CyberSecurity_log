# Willow

柳树下有什么？

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/7bf39e49bd394aec92c4c5abfd80d8b2.png)

## NFS枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/0a899f0c4d86425f9fc6b362ce38eecb.png)

直接挂载进来

![在这里插入图片描述](https://img-blog.csdnimg.cn/9a68494a57d64a7ba37131778a94a37d.png)

存在一个rsa_key

![在这里插入图片描述](https://img-blog.csdnimg.cn/353cad9cdcdf4703befcd937c79396ad.png)

暂时不知道有啥用，先去看80

## Web枚举
![在这里插入图片描述](https://img-blog.csdnimg.cn/d02f053317934cb493e32e62ce688ebb.png)

进入80

![在这里插入图片描述](https://img-blog.csdnimg.cn/80e9061ca889432fa9e0eb7d709ac4b1.png)

看起来像是16进制，使用xxd转换

![在这里插入图片描述](https://img-blog.csdnimg.cn/cdcb1e7182ec4289b8f9cca51ccdef56.png)

得到了用户名和rsa密文

[在线计算器](https://www.cs.drexel.edu/~jpopyack/Courses/CSP/Fa17/notes/10.1_Cryptography/RSA_Express_EncryptDecrypt_v2.html)解密一下得到ssh的私钥

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea04ee51bdb940208112d841593c6e33.png)

需要密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/e83c58f3b93c406280ede5418440bf98.png)

ssh2john+john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/b712d72759874c8eb3a79b16c092d1b5.png)

登录，这里需要加参数 **-o PubkeyAcceptedKeyTypes=+ssh-rsa**

![在这里插入图片描述](https://img-blog.csdnimg.cn/b2cde6ae7f6b4276b92e12e079faf8d2.png)

user flag，使用scp将user.jpg传回攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/c28ba50377ea4d8cb6428cfcb04cee19.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e935da923774c6eaa9e1d55b210376b.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/716edc02d8cc4f5e94a18339fa5d3278.png)

在/dev下发现hidden_backup

![在这里插入图片描述](https://img-blog.csdnimg.cn/7ffd4a67a44d4c209fdf671dde17cf2c.png)

将它挂载到tmp

![在这里插入图片描述](https://img-blog.csdnimg.cn/782c6f87cc3d4fa299bc142d557015da.png)

这里给了root和willow的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/eaa09a6e79d6439a9415ba34fa04ec95.png)

直接su过去，getroot

![在这里插入图片描述](https://img-blog.csdnimg.cn/99bbdf6c9ac246d99e74e606e6c7b49c.png)

然鹅还未结束，我们并没有得到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/93c3224131114d548609dd41b2a2cec8.png)

最终的flag在user.jpg，有隐写，使用root的密码就能提取出真正的flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/911d3e7419d84ba9bd8ee1c2442f4172.png)
