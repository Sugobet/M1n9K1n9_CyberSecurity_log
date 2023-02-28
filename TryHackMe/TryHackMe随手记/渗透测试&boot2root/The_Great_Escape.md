# The Great Escape

我们的开发人员创建了一个很棒的新网站。你能冲出沙盒吗？

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/4cc47c73988b42728d325014b2655776.png)

## Web信息收集

robots.txt:

![在这里插入图片描述](https://img-blog.csdnimg.cn/839f3be0bd2d480b9520551002ee02b4.png)

/exif-util是文件上传点，但是绕过之后貌似没啥用

![在这里插入图片描述](https://img-blog.csdnimg.cn/01562f0cfaf44ae59dac312d9ae6572e.png)

在robots.txt当中披露了可能存在.bak.txt，现在我们已知的文件就是exif-util，我们可以尝试查看exif-util.bak.txt是否存在

![在这里插入图片描述](https://img-blog.csdnimg.cn/598f1d21e3c043dda6e8a7fd87493b75.png)

## SSRF

在这个文件当中存在一个域名，调用了8080端口的exif，但我们直接访问8080是没开的，那么说明8080端口开在了内网，并且exif-util的功能是通过调用内网的api实现的

```js
const response = await this.$axios.$get('http://api-dev-backup:8080/exif', {
```

那么就可以尝试通过这个功能访问http://api-dev-backup:8080/exif，从而形成ssrf

![在这里插入图片描述](https://img-blog.csdnimg.cn/0b7fa7a6d843404685e92437925d9a53.png)

ssrf访问到api，这里暴露了curl，尝试能不能进行命令注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/98fdffa17a01481282380a541e33fee0.png)

## RCE

使用 | 符号就能rce，但是在根目录发现了.dockerenv，这是在docker里，缺少了许多命令，能进行reverse shell的办法几乎没有，所以只能使用这个webshell

/root下发现个密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/29213770f06f4cee8e4b35978da75356.png)

## Git历史提交

在/root目录下还有个.git，查看一下历史提交

![在这里插入图片描述](https://img-blog.csdnimg.cn/516ecaee1f2c47cf8070bfefbcbce77d.png)

查看增加了flag的那一次提交

![在这里插入图片描述](https://img-blog.csdnimg.cn/66443baf0c79470997a7a3c9a388bac2.png)

我们获得的是root flag，虽然我也不知道第一个flag在哪

## 端口敲击

这里还告诉我们：

	+Hey guys,
	+
	+I got tired of losing the ssh key all the time so I setup a way to open up the docker for remote admin.
	+
	+Just knock on ports 42, 1337, 10420, 6969, and 63000 to open the docker tcp port.

这里我去百度了一下，找到了一种叫做“Port knock”

就像minecraft的红石拉杆密码锁一样，好吧，这就像对暗号

nc一把梭，docker守护进程端口2375就会放行

![在这里插入图片描述](https://img-blog.csdnimg.cn/d212fd596caf47d2b9ffc676ed95524a.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/b846ac0b5a244006a74e62c1cb1f280d.png)

## Docker 逃逸

连接到daemon，查看所有镜像

![在这里插入图片描述](https://img-blog.csdnimg.cn/218801baba2e4936ba41a285b1ebb000.png)
这里有两个值得注意的 nginx和alpine

nginx应该就是web网站的镜像，因为网站也是nginx，我们刚刚没拿到的flag可能就在那

不过我们还是先拿到最后一个flag，再回来拿这个

将宿主机的根目录挂载到容器的/tmp

![在这里插入图片描述](https://img-blog.csdnimg.cn/b8ed2d36ff7a4135bccc358338094ecc.png)

我们将能获得真正的root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/329101130de24e2dbc640b92bc3ca773.png)

再回去找找第一个flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/4c60c2b66cfc41448970bffb1dc5ffdc.png)

好吧，在ubuntu默认的nginx根目录/usr/share/nginx/html下并没有找到，换个image再看看

最终在frontend这个镜像下找到这个网站源码，并且发现一个文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/d6e906f1d919409999864db9e8ac24d1.png)

这里需要通过HEAD请求/api/fl46，这里直接使用burp就能做到

![在这里插入图片描述](https://img-blog.csdnimg.cn/541be46390934558a7237419948f0776.png)
