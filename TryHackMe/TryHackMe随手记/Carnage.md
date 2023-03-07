# Carnage

花了两天学了下wireshark

![在这里插入图片描述](https://img-blog.csdnimg.cn/a30b10cc4dfd4d169c92e35cf18f23e6.png)

顺便看一下现在我的红队进程

![在这里插入图片描述](https://img-blog.csdnimg.cn/f043b5e7913846868edf70d02855b278.png)

由于ad在进攻性渗透测试当中已经早早收入囊中，这让我在红队进度中变快

现在，红队路径剩下的room应该都算是在整个path当中比较有难度的了，我不经意的查看了剩下的部分room，我想这需要比以往更多的时间和精力去学习它

在此之前，我需要巩固过去的知识，顺便完成最近的比赛

---

Bartell Ltd 采购部门的 Eric Fischer 收到了一封来自已知联系人的电子邮件，其中包含 Word 文档附件。打开文档后，他不小心点击了“启用内容”。SOC 部门立即收到端点代理的警报，指出 Eric 的工作站正在出站建立可疑连接。从网络传感器中检索 pcap 并交给您进行分析。

任务：调查数据包捕获并发现恶意活动。

---

## 与恶意 IP 的第一次 HTTP 连接的日期和时间是什么？

调整显示时间的格式

![在这里插入图片描述](https://img-blog.csdnimg.cn/cabaec46f74845cd8aece20576b0ac11.png)

显示过滤器过滤http即可获得答案

![在这里插入图片描述](https://img-blog.csdnimg.cn/7f57191c4a1345eabb4269fded5873a4.png)

## 下载的 zip 文件的名称是什么？&& 从中下载 zip 文件的恶意 IP 的网络服务器的名称是什么？

	http.request.uri contains ".zip"

![在这里插入图片描述](https://img-blog.csdnimg.cn/02c68c2f0f8d486e9460ffd0d24a13a1.png)

## 如果不下载文件，zip 文件中的文件名称是什么？

选定上个任务中的流量，导出对象 -> HTTP，将第一条documents.zip保存到本地

![在这里插入图片描述](https://img-blog.csdnimg.cn/92dbc1429e1d44c5aeb152ba7059699c.png)

打开文件即可获得答案

![在这里插入图片描述](https://img-blog.csdnimg.cn/9076a48e2b4440759715491b3a8751ce.png)

## 从中下载 zip 文件的恶意 IP 的网络服务器的名称是什么？&& 上一个问题的网络服务器版本是什么？

查找服务器发送的http包

	ip.src == 85.187.128.24 && http

![在这里插入图片描述](https://img-blog.csdnimg.cn/9d2d892506384019bcf61e2569ad6367.png)

## 恶意文件从多个域下载到受害主机。这项活动涉及的三个域是什么？

根据题目提示，在指定时间范围内

查找tls客户端请求类型的数据包

	frame.time >= "Sep 24, 2021 16:45:11" && frame.time <= "Sep 24, 2021 16:45:30" && tls.handshake.type == 1

![在这里插入图片描述](https://img-blog.csdnimg.cn/bec40a07165b449ea2770a2cf20fcb34.png)

## 哪个证书颁发机构向上一个问题中的第一个域颁发了SSL证书？

跟到那个数据包的位置，在查找certificate类型的数据包，就能找到答案

![在这里插入图片描述](https://img-blog.csdnimg.cn/294cad07eb114c35a2643533c4b156c1.png)

## Cobalt Strike服务器的两个IP地址是什么？使用 VirusTotal（“社区”选项卡）确认 IP 是否被标识为 Cobalt Strike C2 服务器

根据题目要求，使用 VirusTotal 进行恶意分析

首先将会话统计，我觉得c2通信的通信量应该不会少，所以将数据量降序排列，丢到VirusTotal进行分析

![在这里插入图片描述](https://img-blog.csdnimg.cn/84f376c5f6a748a0b24ae4aef79500f7.png)


![在这里插入图片描述](https://img-blog.csdnimg.cn/1e707bf8158f49768e5e8c2a5fc40569.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/3b04e85a56a54700ae002a03b8eacbf5.png)

## 上一个问题中第一个CS服务器 IP 地址的主机标头是什么？

	ip.dst == 185.106.96.158 && http

![在这里插入图片描述](https://img-blog.csdnimg.cn/b770e3f81fcc4d58bb4a523eabd3bd7f.png)

## Cobalt Strike服务器的第一个IP地址的域名是什么？

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd06a695175a480684998695b8b7c117.png)

## 第二个CS服务器IP的域名是什么？

有两个，旧的是答案，最新的域名可能出在房间建立之后

![在这里插入图片描述](https://img-blog.csdnimg.cn/16a317e7e0044f37a209f5c3482729ea.png)

## 受害主机发送到感染后流量中涉及的恶意域的前 11 个字符是什么？

![在这里插入图片描述](https://img-blog.csdnimg.cn/0fbf09b3b4434d1b989dadd2bca8f9a5.png)

## 发送到 C2 服务器的第一个数据包的长度是多少？

![在这里插入图片描述](https://img-blog.csdnimg.cn/ce6b4a9bab2c486c91809fdd648b791e.png)

## 上一个问题中恶意域的服务器标头是什么？

跟过去找到响应头

![在这里插入图片描述](https://img-blog.csdnimg.cn/f7d174136eec42ea8c30f49347b7b95b.png)

## 该恶意软件使用 API 来检查受害者机器的 IP 地址。对 IP 检查域进行 DNS 查询的日期和时间是什么？ && 上一个问题的 DNS 查询中的域是什么？

	dns.qry.name contains "api"

![在这里插入图片描述](https://img-blog.csdnimg.cn/233e10720e9742149cf2bf729c0d6db9.png)

## 看起来有一些恶意垃圾邮件（恶意垃圾邮件）活动正在进行。在流量中观察到的第一个邮件发件人地址是什么？

	lower(smtp.req.parameter) contains "from"

![在这里插入图片描述](https://img-blog.csdnimg.cn/bc158b0797d04c1abffb8401e37dacef.png)

## 观察到 SMTP 通信有多少个数据包？

![在这里插入图片描述](https://img-blog.csdnimg.cn/caa48851a4b2476c8681905f85e2a8ac.png)
