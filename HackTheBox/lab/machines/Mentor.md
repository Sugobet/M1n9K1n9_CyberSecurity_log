# Mentor

Mentor 是一台中等难度的 Linux 机器，其路径包括在到达 root 之前在四个不同的用户之间切换。使用可暴力破解的社区字符串扫描“SNMP”服务后，会发现用于“API”端点的明文凭据，该端点被证明容易受到盲目远程代码执行的影响，并导致在 docker 容器上站稳脚跟。枚举容器&#039;的网络在另一个容器上显示“PostgreSQL”服务，可以通过使用默认凭据进行身份验证来将其用于 RCE。检查“PostgreSQL”容器上的旧数据库备份会发现一个哈希值，一旦破解，该哈希值将用于“SSH”进入计算机。最后，通过检查主机上的配置文件，攻击者能够检索用户“james”的密码，该用户能够以 sudo 权限运行“/bin/sh”命令，从而立即丧失“root”权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5894a36b-fdb8-2d1b-530e-f34caf6a218d.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/77eb9825-101f-1d37-742e-f09f856b778d.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/19618436-6837-6faf-88a1-6750bbafa633.png)

ffuf扫vhost

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/424fa3cb-176a-c96c-a9d5-b966bbb1bfc0.png)

api子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c6a8bba6-c606-552c-12f4-09974ca4c40a.png)

feroxbuster扫一下

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0133baee-9c74-77b2-55bf-90e6bedc1808.png)

/docs

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/39e00fc1-2d4c-edaa-168e-624afe2406c9.png)

/openapi.json

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/343fe036-1f14-de45-23e7-ea54c13d35de.png)

### SNMP

snmpbrute

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/32276242-1d74-309d-b227-b07e09766382.png)

跑snmpbulkwalk

```bash
snmpbulkwalk -v 2c -c internal 10.10.11.193 > ./res
```

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7c6edb8c-8680-0cb1-7bc0-2f5b406d8f54.png)

## Foothold

login.py后的参数大概就是密码，前面给了james

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3310ede0-954c-b2e8-f15a-a0b603ba96be.png)

前面的/admin还有两个端点

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/368a048b-9ab3-fdee-6663-b7b5617702b2.png)

在/admin/backup中存在blind rce

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/832d6153-e694-5379-5d3e-dd6b3f2a8b12.png)

reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f1e3303a-529b-1c70-7560-b6e33242d318.png)

## Docker逃逸

app/目录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7447dbdc-d9c3-c20b-a1f4-031cfa7ee12c.png)

这里有一组数据库的凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/aab40cef-08af-d109-e6a8-3198288edda7.png)

chisel把postgresql转出来

攻击机

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/76b4a888-df4f-9777-4dce-433e323f227e.png)

目标机器

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0ddbbbfc-8230-f27d-64f5-f223d5e8edc6.png)

通过那组凭据，我们能够进入数据库

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a95151b9-e0b2-86a1-40c6-6ac09e9565b6.png)

有三个表

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/25864e04-8688-1019-6896-422082fbb008.png)

users表有两个hash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3b10737b-7cb9-9efa-11bc-0d0cf44bb602.png)

CrackStation爆出来一个，即svc的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a06d23ef-8a6a-a392-5c80-696ddcb602d9.png)

我们能够通过这组凭据来登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/de2dc4b3-0334-28cb-f9be-2cb1b1cc4f82.png)

## 本地横向移动 -> james

跑linpeas

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8da1599b-86e4-0455-f211-610d119ea835.png)

/etc/snmpd.conf里有一组密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/88dcd142-302d-6bb8-89ad-299189283406.png)

这密码是james的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5b5bd5b4-069a-8c72-bfcc-8c5172ece8f6.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2b6a43f5-5a31-4e41-4b7f-362ea4481eb7.png)

它会向我们妥协

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/76acb0b4-bac9-95ee-eac2-35549f46eb7c.png)
