# Socket

Socket 是一台中等难度的 Linux 机器，其特点是反转 Linux/Windows 桌面应用程序以获取其源代码，从那里发现其 Web 套接字服务中的“SQL”注入。转储数据库会显示一个哈希值，一旦破解，就会产生对该框的“SSH”访问。最后，可以使用提升的权限运行的“PyInstaller”脚本用于读取“root”用户的私钥“SSH”密钥，从而实现对计算机的“root”访问。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/01699fa8-fec5-5dde-472f-c85098516c7f.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0a363326-a998-8853-9b53-79c9f977db50.png)

下面可以下载它的应用程序

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/874a62d6-99fd-7a09-b0ac-7014f4900b05.png)

strings可以判断它应该是python打包的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6c6e0c35-de3c-5d4a-cba0-49dd81136a55.png)

pyinstxtractor

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/11b14f05-d201-3a85-9519-e3205e252dea.png)

随便找了个[在线工具](https://www.lddgo.net/string/pyc-compile-decompile)将pyc转明文

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2b109e4a-6e4a-5d19-3455-0a960ae6f946.png)

wscat连接5789

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d23ba71d-56bb-e933-e1fe-a898042eedb6.png)

## Foothold

测一下可以看到存在sql注入，常规操作

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/52854328-8555-9b87-0cb1-2691cdae9ae3.png)

查表

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/92e73b32-6905-689e-f062-37213d5ee1b3.png)

查列

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2257ef96-89d8-8160-3058-f165e7e8157e.png)

读数据，得到admin的密码hash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ffd11be3-f82e-fe5a-57cf-5ac456dbedbf.png)

CrackStation

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8242ce33-6b27-acd8-f05a-cc86ca7bbfd7.png)

但是没用户名，用hydra做ssh密码喷射太慢了，从answers表中得到名字，在linux下用最常见的姓和名组合尝试登ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/dc00c1f9-77e1-d05c-a6d2-ae4f25e6f0a8.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4cbce724-6b67-2dfb-40ee-34a39766e21a.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/06f563c6-2d41-a5b9-5142-d37d5d2162a9.png)

```bash
...
if [[ $action == 'build' ]]; then
  if [[ $ext == 'spec' ]] ; then
    /usr/bin/rm -r /opt/shared/build /opt/shared/dist 2>/dev/null
    /home/svc/.local/bin/pyinstaller $name
    /usr/bin/mv ./dist ./build /opt/shared
  else
    echo "Invalid file format"
    exit 1;
  fi
elif [[ $action == 'make' ]]; then
  if [[ $ext == 'py' ]] ; then
    /usr/bin/rm -r /opt/shared/build /opt/shared/dist 2>/dev/null
    /root/.local/bin/pyinstaller -F --name "qreader" $name --specpath /tmp
   /usr/bin/mv ./dist ./build /opt/shared
  else
    echo "Invalid file format"
    exit 1;
  fi
...
```

随便运行一下看看效果，生成了一个/tmp/xxxx.spec

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/74f9a3ad-01ba-6712-43cf-175dd419c0ff.png)

查看.spec文件，发现这不python嘛，我猜它会被当成模块导入

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4b288616-96dc-3f72-627d-9ae26ffb78ee.png)

cp一份

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b40aae79-8104-afd7-630e-fe76ec901442.png)

写payload

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/46f05033-1d78-149e-bee4-88f6cd403928.png)

sudo build这个.spec，我们的老朋友如期而至

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fd7749a8-35dd-ae15-219e-0cad4b9e73bc.png)
