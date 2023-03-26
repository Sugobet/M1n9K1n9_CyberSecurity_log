# Sustah

开发人员在他们的游戏中添加了反作弊措施。你是 能否突破限制以访问其内部 CMS？

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/4afa6f8654d6417c98cccbf1fdb8e37c.png)

## Web枚举

80端口没啥东西，看一下8085端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/269bdcf34a1e496da34938c90e17065d.png)

gobuster扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/3cd45d61b392417f9913a2b775762f27.png)

/ping似乎没什么东西

回来home，看看burp

![在这里插入图片描述](https://img-blog.csdnimg.cn/a0ac5dae7ce24fb59e4e265f1404bc01.png)

使用bash生成数字字典

![在这里插入图片描述](https://img-blog.csdnimg.cn/73df39aca60f483090bb01b131f19edd.png)

使用ffuf爆破时发现没有任何回显，使用wireshark发现有限速

![在这里插入图片描述](https://img-blog.csdnimg.cn/e1764cbcfe1e49c9a764a9b10199fcfa.png)

题目提示可以向请求头添加某个字段绕过限速，那大概率就是那几个ip绕过了

试了一下，X-Remote-Addr可以绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/6926622e027344e8b5f7ad9856b0b72c.png)

获得一个目录名

![在这里插入图片描述](https://img-blog.csdnimg.cn/1eac95bc290449e6b8528fe7af6f268e.png)

然鹅这个目录不不在8085端口上，在80端口上

![在这里插入图片描述](https://img-blog.csdnimg.cn/fedf53e1846445ab89531e47c5698255.png)

扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/b8e4d62e564d45f18b51030ffe07cf19.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/bc5496f3263e47bbb5a269ecbb46391d.png)

changs.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/a56fa0cf82b44f95927365aea9dd2d50.png)

searchsploit看一下，有个rce

![在这里插入图片描述](https://img-blog.csdnimg.cn/9290b0bdf43a4adbad769f3a582cbb74.png)

进到test page使用默认凭据登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/8fcf42e7f8b44063bd047313cba2f5c2.png)

然后进到dir.php这里可以任意文件上传

![在这里插入图片描述](https://img-blog.csdnimg.cn/73ff72e4fa464d44b57c42d79a73d2a7.png)

文件在/img

![在这里插入图片描述](https://img-blog.csdnimg.cn/fb190c9765a1421888f34df8814593c6.png)

getshell

## 横向移动

在/var/backups下发现了passwd bak

![在这里插入图片描述](https://img-blog.csdnimg.cn/2d17f2038e8b4ebf9bd8249c80ddaf17.png)

虽然文件中没有暴露任何密码hash，但在kiran账户的desc中发现疑似密码的字符串，尝试登录，成功

![在这里插入图片描述](https://img-blog.csdnimg.cn/a36bef114dba4a419c16c8f19197561d.png)

## 权限提升

根据题目的提示，一路找到doas.conf

![在这里插入图片描述](https://img-blog.csdnimg.cn/c80bd9e0464e4a44864ec143ac218c61.png)

查看垃圾桶，跟sudo的利用一致

![在这里插入图片描述](https://img-blog.csdnimg.cn/103e3b0ab32a4e16b9ee117f051a3338.png)

getroot