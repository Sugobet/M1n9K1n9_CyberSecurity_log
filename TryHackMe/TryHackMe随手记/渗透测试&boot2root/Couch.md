# Couch

入侵以基于 JSON 的文档格式收集和存储数据的易受攻击的数据库服务器.

---

做点简单题放松放松

## 端口扫描

循例 nmap 扫:

	nmap -sV 10.10.83.34 -p 1-10000 -T5

![在这里插入图片描述](https://img-blog.csdnimg.cn/0589098a921f4a3b99cf207e25118d4a.png)

## CouchDB

百度找couchdb相关文章：

![在这里插入图片描述](https://img-blog.csdnimg.cn/0e8a6f0abbc04bfeb58cf201e3eb9c81.png)

访问/_utils

![在这里插入图片描述](https://img-blog.csdnimg.cn/b4e42a279f114aeabf069b7b897521fc.png)

在secret中发现了一组凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/ac352c2cdc7a48f783b88d63e1b47127.png)

利用这组凭据尝试登录ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/0047117a02e44ccdae76c907e8ab2644.png)

## Docker 守护程序

在atena的家目录下发现发现.bash_history文件有东西：

![在这里插入图片描述](https://img-blog.csdnimg.cn/2001bc34cba04c0b81b1f5598f00d199.png)

使用ss命令查看到内网确实开了2375，通过bash_history我们可以确定这是docker daemon

## Docker利用

	docker -H 127.0.0.1:2375 images

发现一个alpine

	docker -H 127.0.0.1:2375 run -v /:/tmp -it alpine

挂载主机根，root.txt在/tmp/root/root.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/928f9aa395b04b02b758669d418eb9ae.png)

