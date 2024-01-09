# Shared

Shared 是一台中等难度的 Linux 机器，它具有通向立足点的 Cookie SQL 注入，然后通过对 Golang 二进制文件进行逆向工程并利用两个 CVE 来获得 root shell 来提升权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6f1e2777-6df2-6756-8ac3-4e715859b52a.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3e5e5cfa-a204-3c9d-e451-bd29b2d86543.png)

查看证书

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/26267a86-f1e3-0d05-0e71-a53745b026ac.png)

看到这个扫了一下vhost

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/160ab9c1-a4e0-b014-193d-1ee5936b18b5.png)

checkout子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b66fadcc-eb34-bfae-e169-314431fca657.png)

从主站商店选择一件商品加入购物车

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fcfdb23c-3e5c-2375-6215-6e8683417769.png)

结算后会跳到checkout子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/203f7cc4-ba4d-bd7a-899f-8f4647a55a3a.png)

## Foothold

从Cookie中的custom_cart带过来的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8e81e01f-0dc5-45a6-eb7d-9d776b48bcf4.png)

它受sql注入影响

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e47c8df6-181a-a72a-15ac-d51fc24171b7.png)

接下来就是常规操作

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fe028c34-f113-7429-a14b-e904f410eec5.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/30610bb9-d075-eda6-89ff-06e60211a799.png)

得到james_mason的密码hash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ffde18c8-a357-dfc9-8810-c899b4834e30.png)

在线爆得到明文密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f76270fe-f11c-0688-abdb-a2380fe55418.png)

这次的ssh username没有变化，直接就是数据库这里的username

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6d6ea34c-2fc0-0986-b787-601e43aa1288.png)

## 本地横向移动 -> dan_smith

传个pspy过去看

```shell
2024/01/08 22:33:01 CMD: UID=1001  PID=2469   | /bin/sh -c /usr/bin/pkill ipython; cd /opt/scripts_review/ && /usr/local/bin/ipython 
2024/01/08 22:33:01 CMD: UID=0     PID=2472   | /usr/sbin/CRON -f 
2024/01/08 22:33:01 CMD: UID=1001  PID=2473   | /bin/sh -c /usr/bin/pkill ipython; cd /opt/scripts_review/ && /usr/local/bin/ipython 
```

ipython版本是8.0.0

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fbf2277f-80a9-51e8-dc7a-421ee5b3eff8.png)

谷歌得到一个相关的cve

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3dcb97db-b70d-6c1b-dd2b-0c1b48c365a9.png)

这个版本在运行ipython时ipython总是会在当前目录查找配置文件，官方解释：

	几乎所有版本的 IPython 都在当前查找配置和配置文件 工作目录。由于 IPython 是在 pip 和环境之前开发的 存在，它被用来在项目中加载代码/包的便捷方式 依赖方式。

	在 2022 年，它不再需要，并且可能导致令人困惑的行为，其中 例如，克隆存储库并启动 IPython 或从 任何将 ipython 设置为内核的 Jupyter-Compatible 接口都可能导致 代码执行。

通过它，我们能够在dan_smith执行ipython时进行reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/539a9137-c233-4e4b-47ed-cf735bcf8331.png)

在/tmp创建个一样的目录结构，在startup/下写shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/665579f5-1ce5-cb37-5cb8-e5f49bdd0822.png)

cp过去/opt/scripts_review/

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/95bc9e80-9e8a-e211-7d4d-4cae673f0635.png)

我们会得到它

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/db36e3c3-d166-f3fc-bc16-fb692fc317ec.png)

## 本地权限提升

find

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a918daad-ff56-4213-e83d-c80765695d4e.png)

运行，发现它是登录了redis，密码估计是硬编码写代码里了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e156612f-1455-7116-44af-390483008161.png)

传回攻击机

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0be5efc8-1896-bb46-2422-cf04b0fc3538.png)

ida一看密码就出来了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2e1e4240-f676-9c91-efd6-397850259adb.png)

hacktricks告诉我们可以尝试load module

	https://github.com/n0b0dyCN/RedisModules-ExecuteCommand/

make之后将so传过去

module load

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/62fe32b5-a096-8856-b723-6a47c539d55f.png)

root flag

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b08d01ca-5014-0dbe-9b2e-d08cb0c1d8e5.png)
