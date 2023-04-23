# Services

认识团队！

**今天thm新出的房间，尝尝鲜**

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/f3825fa196ca4b139c6b0c9a4257260f.png)

把services.local加入hosts

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/c594b4c3d19c4e53ba0cc6d79ccd93e1.png)

发现员工邮箱以及一些员工姓名

![在这里插入图片描述](https://img-blog.csdnimg.cn/ad6ebf50817b4741a58b79dff49102d5.png)

从下边的邮箱中，大致可以猜测其他员工账户名跟这个一致的格式

将其保存起来

![在这里插入图片描述](https://img-blog.csdnimg.cn/719673ff66eb4e42b2897780fbba0e5c.png)

## 立足 - AS-REP Roasting

有了账户名，直接上asrep roasting，利用GetNPUsers.py

![在这里插入图片描述](https://img-blog.csdnimg.cn/029357158f4d464485bea9a602cb7aa4.png)

得到了j.rock的hash

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/e1b8610fae894af6bab39f58e4df1a99.png)

得到密码直接登winrm，同时拿到 user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/13419206d68b4bcaa448f36e0c450190.png)

## 权限提升

检索一下我们的权限

![在这里插入图片描述](https://img-blog.csdnimg.cn/fe9406c4662a42e0925458216d52d854.png)

我们在server operators组中

![在这里插入图片描述](https://img-blog.csdnimg.cn/ce185d20b82e42a9a52208502991baf4.png)

我们目前有权修改服务配置

我们需要先知道有哪些服务，但无法使用sc、get-service、wmic、accesschk查看。我们通过get-process查看进程看到ismserv，这名字看起来就像服务进程

管它是啥服务，这服务是自动运行的，并且是localSystem

![在这里插入图片描述](https://img-blog.csdnimg.cn/5e50dfb2fdb6438ca6c722d86d0bc852.png)

直接改binPath

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b3ed9417c824a9ba66c5a35b403ca60.png)

由于无权启动服务，但我们有权shutdown，可以重启机器

![在这里插入图片描述](https://img-blog.csdnimg.cn/4b0aaabd6786470a8121a4a7b92bd66c.png)

登我们添加的账户，同时拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/88850dca70b449a4b29e9bda2ede115c.png)
