# Noter

Noter 是一种中型 Linux 机器，其特点是利用了 Python Flask 应用程序，该应用程序使用易受远程代码执行影响的“节点”模块。由于“MySQL”守护进程以用户“root”身份运行，因此可以通过利用“MySQL”的用户定义函数来利用它来获得RCE并将我们的权限升级到“root”。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3f4c45db-f5bb-178c-6e63-5d3f321d0da9.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/63ad259c-9453-c6ab-72a5-5feee4dfac1c.png)

注册个账号直接登进去

逛一圈没有常见的漏洞点

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fb42b0ad-e417-b54c-10f4-34a921c077c5.png)

base64解码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fc994629-c052-f07f-449b-e6c885d919b4.png)

flask-unsgin直接爆破

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e18683a3-2c5d-f843-6c87-f923180e6cb6.png)

生成用户

```bash
for name in `cat /usr/share/wordlists/SecLists/Usernames/Names/names.txt`;do flask-unsign --sign --cookie "{'logged_in': True, 'username': '$name'}" --secret 'secret123' | grep -iE 'ey.*' -o >> ./res.txt;done
```

ffuf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b9d760ae-7148-64ad-eae5-c2850cb31582.png)

有料

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ea1e9ba4-403d-2251-162d-8863bc04b2e4.png)

note 1

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/282ee8c0-6445-7045-11a0-7958f9556642.png)

使用这组凭据我们可以登录ftp

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/363ded72-cea7-4796-b675-6c6a9e9f945c.png)

有个pdf直接下下来

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c4a1e407-85e1-23ff-a829-6ee35916c32b.png)

前面还有个ftp_admin

	ftp_admin:ftp_admin@Noter!

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/feb113ef-e115-bfed-0353-667cef1cd075.png)

在其中一个zip的app.py发现一组mysql凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b180ee66-5c32-5273-80fc-3bf19dea81e3.png)

md-to-pdf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/814916dd-0c90-7bfe-2590-ebaf14d19b3b.png)

packafe-lock.json中找到版本号

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cc242ba3-0552-2f9d-0339-08d66268b12d.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/71ba6e85-5530-42aa-040a-80b8152de843.png)

poc:

	https://github.com/simonhaenisch/md-to-pdf/issues/99

可以RCE

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/66dafb3c-8f4a-2cef-0f29-76a14da3e406.png)

常规reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8c9d342f-4f49-9d5b-9267-56f098c4501e.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e705f6dc-3a47-5813-e0e5-34917039d8c2.png)

## 本地权限提升

前面给了mysql的凭据，而且mysql还是root运行的

udf，传过去编译

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/081fe937-4103-7054-2645-0c361c46a4b4.png)

plugin_dir

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/de02f360-9c92-5e25-12a5-fef7c713eafa.png)

照着exp加载udf就ok

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/26fe909c-279a-5293-ffda-3247968f32de.png)

suid bash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/47d2fa46-c7da-3efc-1d15-12f4edd48938.png)

它来了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/39a0f3c1-2cd3-28a3-5568-c688572244eb.png)
