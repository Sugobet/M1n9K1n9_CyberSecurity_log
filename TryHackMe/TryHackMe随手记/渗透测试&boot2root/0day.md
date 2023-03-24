# 0day

![在这里插入图片描述](https://img-blog.csdnimg.cn/b3603dbfdbcb422abfa9f26cbef51e65.png)


扎根我的安全网站，进入黑客的历史。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/6053d7712f854d519540c9a03134ebe9.png)

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/baeeac59fd274e4eb02a9e20b184fa0c.png)

### 目录扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/b0a3dbd6a3524a528662e3dc753d3513.png)

- /admin是空页面
- /backup是一串rsa私钥
- /secret是一个乌龟图片，我以为有隐写，但事实并没有
- /cgi-bin

将私钥下载，不难看出这或许是0day的，尝试john爆破私钥密码并利用

![在这里插入图片描述](https://img-blog.csdnimg.cn/199e2f787e724f368bd124e3a70add1b.png)

好吧，这并不管用

### CVE-2014-6271

上nikto

![在这里插入图片描述](https://img-blog.csdnimg.cn/d5fd0132008844469f3df5cd9099798b.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/ccc72c2b20064433a9888eb32a108f26.png)

阅读exp和一些[文章](https://www.antiy.com/response/CVE-2014-6271.html)，我们可以了解其漏洞大致原理：导致漏洞出问题是以“(){”开头定义的环境变量在命令ENV中解析成函数后，Bash执行并未退出，而是继续解析并执行shell命令

而test.cgi恰好是利用了存在漏洞的bash编写的，故受此漏洞影响，我们也将通过它来getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/34007302380f4b2a8859fb1249d9467b.png)

## 权限提升

题目提示：这是一个很久的操作系统

查看uname -a

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea7e98ae14114d37bbdff1cfafb12ef5.png)

这个内核版本看着真眼熟，还是Ubuntu。昨天刚做了类似的房间

CVE-2015-1328，关于overlayfs的漏洞

传到靶机上编译，会报错，看了相关文章，解决方案是

![在这里插入图片描述](https://img-blog.csdnimg.cn/65517b8c6eee478cb7c6f5f94a6480e2.png)

使用export将环境变量的当前目录(.)删掉

即

![在这里插入图片描述](https://img-blog.csdnimg.cn/e5206a5e3b8d46c0a6eadd972a78eeba.png)

再次gcc将能成功通过

![在这里插入图片描述](https://img-blog.csdnimg.cn/c35ae8e5d3934cdd9e4ef9c696e8c672.png)

getroot

root flag还在老地方