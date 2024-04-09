
学完、打完后的复习

# HTTP 1

这部分比较简单，直接略过

# HTTP2请求走私

首先要了解HTTP2的结构，与HTTP1之间的一些差异

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/fe5ed1a00b7b406095b38dadb94e2bb5.png)

HTTP2中不再使用CRLF来作为字段的边界限定，而是在二进制中直接通过长度、名字、值长度、值，来确认边界

而这里教导的主要场景是在前端代理使用HTTP2，而后端使用HTTP 1.1

虽然HTTP2并不会处理Content-Length和Transfer-Encoding，但在上述场景下，前端代理将把http2转为http1.1然后转发给后端处理。

所以一旦我们为http2请求添加CL或TE，并在post form添加http 1.1的请求头，即常规http1的请求走私打法，前端代理将http2转http1.1交给后端后，我们的走私请求将会逃出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/c81e7d10e78847dfa1a48c4de80c8b16.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/edb31810286d4ac18bb31d94a348a4df.png)

## CRLF

除了CL和TE，还有另一种方法在上述场景中实现请求走私，就是CRLF，通过在http2请求头中的请求头里面注入CRLF并构造走私请求payload，那么在前端代理转发给后端时依然能够实现http请求走私

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/415e94f6c8cb478398bddd8ed12d24bf.png)

在某些代理实现中，每个用户将获得自己的后端连接，以将他们的请求与其他用户分开。每当发生这种情况时，攻击者将无法影响其他用户的请求。乍一看，如果局限于我们自己的连接，我们似乎做不了多少事情，但我们仍然可以通过前端代理走私请求并取得一些结果。由于我们只能将请求走私到我们的连接，因此这种情况通常称为请求隧道。

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/5c2d82165e93407b8bba7147d00b9d6a.png)

## 泄露内部标头

这一点也非常简单，前提是存在回显点，后面的靶机中有这个例子

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/9c99a1d5c3254d5db09cde309c2af30e.png)

## 绕过前端代理限制

同上，前端代理做了访问控制，但后端没有，我们就可以通过请求走私来绕过前端代理，将走私请求送到后端，此时我们再次发起http请求 接住走私请求以获得走私的响应

# WebSocket 走私

第一种就是简单的欺骗前端代理

	Sec-WebSocket-Version: 777
	Connection: Upgrade
	Upgrade: websocket

将Sec-WebSocket-Version字段设为目标不支持的版本，此时，前端代理不验证后端是否升级websocket成功（code 101）和失败（code 426），所以只有前端代理与我们使用websocket进行通信，而前端代理到后端依然使用http进行通信

我们就可以在websocket中携带恶意http请求头以实现走私

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/ccaae515d827494cb609488bd305f001.png)

**请注意，某些代理甚至不需要存在 WebSocket 端点即可使该技术发挥作用。我们所需要做的就是欺骗代理，让其相信我们正在建立与 WebSocket 的连接，即使事实并非如此。看看如果您尝试发送以下有效负载会发生什么（请确保在 Burp 中的有效负载后添加两个换行符）**

## 绕过安全代理

那么，如果前端代理会验证后端是否升级成功（code 101），在这里，thm教导我们可以寻找SSRF来帮助我们做到这一点。

通过ssrf访问我们托管的http服务器，当我们触发ssrf时，目标访问我们的恶意http服务器，我们就可以控制我们的http服务器返回 code 101，表示升级成功，此时前端代理就会认为升级成功，后续攻击者到前端代理都将使用websocket通信，而事实上后端仍然使用http

# HTTP 浏览器异步

keep-alive: 允许对多个 HTTP 请求和响应重复使用单个 TCP 连接

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/11a7cadd98dd40d68b37c7d26a789b30.png)

http 管道： 如果后端服务器启用了 HTTP 管道，它将允许同时发送两个请求和相应的响应，而无需等待每个响应。区分两个请求和一个大请求的唯一方法是使用 Content-Length 标头

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/b314c05275ec434cb0664736eb730d82.png)

HTTP 浏览器异步利用链接 XSS，也比较简单，略过

# El Bandito

这里是打完靶机后的复盘，只有细节部分

nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/b956ac94566c430a9a9d2d999fe2e6a9.png)

我们在8080中有一个SSRF

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/c6ac84bcac4844c6956089086819def4.png)

8080存在websocket走私，前端代理会验证websocket是否升级成功

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/894c0ce9f8cf4fb898e9b66fc41925c8.png)

结合前面的ssrf，我们就可以完全照搬前面thm教导的技巧来绕过前端代理的验证

最后payload如下图，我们可以得到一组凭据以及靶机的第一个flag：

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/2c4359d204ae4d649dc9aae14cb0b772.png)

最后回到80端口，存在http2请求走私，通过CL或者是http2请求头CRLF注入来实现走私，结合/send_message端点可以发送消息，借此通过走私来获取受害者标头，通过/getMessages来获取回显信息。

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/cfb595d6424c4be090b5bcab6b714d2c.png)

最后一个flag则在标头中

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/2619561b9b8e4317ba22ffaf1087eac5.png)

