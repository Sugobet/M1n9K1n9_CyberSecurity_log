# Ra 2

WindCorp最近发生了安全漏洞。从那以后，他们加强了基础设施，从错误中吸取教训。但也许还不够？您已经设法进入了他们的本地网络...

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/25d7fee65d564e8aa59117d96e52eae8.png)

域名跟Ra前部基本一样, 多了个selfservice

## SMB枚举

smbmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/30cc990e233f4a96ad7e0218249c5868.png)

enum4linux也没什么信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/59b6f11776624f3a953331267ced88b5.png)

## DNS枚举

dig枚举，txt记录发现flag1，并且flag是一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/f48680d02f8b48729dd5dbcb22bfcf46.png)

	允许不安全的动态更新是一个重大的安全漏洞，因为可以从不受信任的来源接受更新

## Web枚举

根据Ra，尝试故技重施，重置lilyle的密码，发现失败

![在这里插入图片描述](https://img-blog.csdnimg.cn/30c31a92fa024dfe8fdec65dadb21495.png)

来到fire子域，跟主域一致，除了有个按钮，它指向了一个新的子域

![在这里插入图片描述](https://img-blog.csdnimg.cn/f0da17ca35de47eead21c56af7218b4b.png)

发现需要登录，查看包发现还是ntlm，这让我不禁想起pth2web，然而目前也没有可用凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/ad58f2baefc543eea46a3d13549b1856.png)

使用gobuster对着fire扫描有个powershell, 但目前并没有可用凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/90a424e7593840e5a150e33b0fb06bb7.png)

查看源代码发现了9090端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/1c37052d73cd4206981c469dc28c64ce.png)

进去是一个openfire 4.5.1，但没没有找到什么特别有用的公开漏洞，扫目录也没扫到啥东西

![在这里插入图片描述](https://img-blog.csdnimg.cn/1972ea20d3d84d4bacc980f6d7f0ffac.png)

剩下一个selfservice子域没扫，gobuster扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/04a95d33eef248f5ac755620f23fac75.png)

由于没登录的缘故，也扫不到东西

回到端口扫描结果，遗漏了一个dev

![在这里插入图片描述](https://img-blog.csdnimg.cn/a2aea6a0c31d4d4a86cbc33683ea81f4.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/97c43ae448724a8694b48b900b5f0974.png)

gobuster扫到个backup

![在这里插入图片描述](https://img-blog.csdnimg.cn/98b5f2eab1e04af2afef59402a4521f0.png)

里面只有一个证书，这是从未见过的未知打法

![在这里插入图片描述](https://img-blog.csdnimg.cn/09ed560518e443b8840c568f77f11ca0.png)

## DNS缓存投毒

其实回到开头获得的第一个flag给出的信息，其实很明显，这指引我们要对dns做点手脚

我参考了wp，其实我的想法也差不多，但没想到会有机器人发送登录请求这个茬

根据flag1的信息，这表明我们可以动态的更新dns服务器的缓存表项，selfservice的https需要ntlm身份验证登录，而根据wp的提示，会有机器人自动发登录请求

这意味着如果我们能通过dns缓存投毒，使selfservice子域的dns的a记录改成攻击机的的ip地址，那么机器人将会带着ntlm hash过来，我们也将能获得该hash并且进一步利用

这种攻击方式以前只学过理论，但付之于实战这也是第一次

首先需要把https搭起来，我也学着wp使用responder搭

至于证书，刚刚我们已经从selfservice.dev子域获取了，但它是pkcs格式，我们需要从中获得ssl cer和key

![在这里插入图片描述](https://img-blog.csdnimg.cn/ae537f6a3a69408b980a294535edbf56.png)

它需要密码，pfx2john + john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e6393ddbf7a434fa505bb5221ddd111.png)

获得cert.pem和key.pem

![在这里插入图片描述](https://img-blog.csdnimg.cn/eff1bc083bf94c6489b6432b7cb0bafc.png)

配置responder

![在这里插入图片描述](https://img-blog.csdnimg.cn/a6f8f7dff52740848a5442de1f1b89b8.png)

开responder，确保https没问题

![在这里插入图片描述](https://img-blog.csdnimg.cn/8625b43ba0304ce5aece7accc312476a.png)

手动连接到本地443，查看一下证书，没问题

![在这里插入图片描述](https://img-blog.csdnimg.cn/e861b0567170405688d585feb8c3fe48.png)

使用nsupdate向靶机即dns服务器进行投毒

![在这里插入图片描述](https://img-blog.csdnimg.cn/ffd3591ffa7c468dbe0214f1a658a889.png)

dig看一下，确定修改成功

![在这里插入图片描述](https://img-blog.csdnimg.cn/7a0a2eab2d1e4cab98e40565c883cc75.png)

不一会，机器人就带着凭据过来了

![在这里插入图片描述](https://img-blog.csdnimg.cn/f68c657b369042d0bc5904289c81c4ed.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/0ab60140b08a4af3ae26e540386d8e9d.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/14fe326f72c24124b35dffeb4886e433.png)

## 立足

回到刚刚的fire子域下的/powershell，拿着凭据直接登录

成功进来，并同时获得flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/a32830b2d5144ae6b52c3cb019e20434.png)

## 权限提升

查看whoami /all，有许多让眼前一亮的信息，其中最值得注意的依然是老朋友SeImpersonatePrivilege

![在这里插入图片描述](https://img-blog.csdnimg.cn/cd274cb16b4648c49424fa8c83232cfd.png)

传个PrintSpoofer

![在这里插入图片描述](https://img-blog.csdnimg.cn/855161ac628b4cdcb0355745c0ad8ce4.png)

添加账户并加入admins组

![在这里插入图片描述](https://img-blog.csdnimg.cn/72d1a93b838747839c9e195ffc16a568.png)

xfreerdp直接登

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a0a38a3964f4b548928b046097cd83f.png)

flag3

![在这里插入图片描述](https://img-blog.csdnimg.cn/46890dc2cee14df795249ed11fd205f9.png)
