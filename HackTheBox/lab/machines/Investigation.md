# Investigation

Investigation 是一款 Linux 机器，难度为中等，它具有一个 Web 应用程序，可为图像文件的数字取证分析提供服务。服务器利用 ExifTool 实用程序来分析图像，但是，正在使用的版本存在命令注入漏洞，可利用该漏洞以用户“www-data”的身份在盒子上获得初始立足点。通过分析在 Windows 事件日志文件中找到的日志，可以将权限提升到用户“smorton”。为了实现获得 root 访问权限的最终目标，用户必须对二进制文件进行逆向工程，该二进制文件可以由具有 sudo 访问权限的用户“smorton”运行，然后利用它来提升 root 权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/197f1a69-d511-e710-d1e7-d209ba77fd53.png)

### Web枚举

进80

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8dec917d-91b2-4168-766b-e833353cf39d.png)

有一个图片上传点

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/03a183ff-d80e-641a-48d2-9fbc619054d6.png)

传个正常的jpg

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/62ea9a12-4abb-3c07-8c2b-d444acd69c66.png)

查看图像分析结果，exiftool版本为12.37

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c366cb61-7ade-d0fa-257d-2ae990692431.png)

## Foothold

它有一个[rce](https://github.com/cowsecurity/CVE-2022-23935/blob/main/CVE-2022-23935.py)，将命令拼接到文件名中导致逃逸

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/410d057f-b3de-20e3-b462-1fa5906a0581.png)

上传它，我们将能得到那个东西

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/df30d3b6-a087-981c-1d66-5b26c482ced9.png)

## 本地横向移动 -> smorton

crontab -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/300e04cf-4331-8e77-603f-ebe9cf790701.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ea66f14c-3589-51c6-d22e-80d43b7ea4bd.png)

将.msg文件回传攻击机

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3db933e1-c987-b060-48c0-87e28811067c.png)

通过这个[在线网站](https://msgeml.com/)来读取.msg的内容

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/41b077f1-2911-093e-7001-22195fbeac29.png)

下载zip，我们可以得到windows event log，过滤4625登录失败事件，有个疑似密码的字符串被当成了用户名

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fd254ead-8ed3-cf40-e3bd-4ce2ff7070fd.png)

通过这个字符串，我们能够从ssh登录smorton

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4cf3137d-9ec5-1554-fad7-b435f1171c12.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/66e2003f-373b-a9ff-65e8-6a603af53fcd.png)

直接执行它似乎并没有发生什么

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fd1ed7a1-7958-7833-65ab-5bacdcd47286.png)

将文件回传攻击机，ida F5看一下

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ec5d9601-b264-cf09-bc52-7ccd762dc4e6.png)

很显然，我们需要输入两个参数，第二个参数必须是那个字符串，第一个参数是一个url，它将通过curl_easy_setopt函数请求文件，并且该文件会被perl执行

创建pl

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/899e7b89-b55b-d97d-534d-63cf669727af.png)

sudo执行

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/834844fa-10ee-c6a9-4120-c8c31b87a973.png)
