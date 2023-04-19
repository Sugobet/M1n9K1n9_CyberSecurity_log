# Year of the Dog

谁知道呢？狗咬了一口！

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/2a12f9c1c9c140cfab37553ee455ad74.png)

## Web枚举

进80

![在这里插入图片描述](https://img-blog.csdnimg.cn/d17ce7c5b86641b091b749be5e7859a7.png)

用gobuster扫了一圈没有任何发现，图像也没有隐写

在主页的请求头的cookie有一个id

![在这里插入图片描述](https://img-blog.csdnimg.cn/1ec59c6b0819435d92a4efcb3ada360e.png)

改成其他错误值会导致异常，看见叫id，习惯性加个了引号

![在这里插入图片描述](https://img-blog.csdnimg.cn/5e62cae617f24e03a9e3febbbcb098b9.png)

爆库

![在这里插入图片描述](https://img-blog.csdnimg.cn/a1e5300d9892421c9f0f6182a7deda69.png)

爆表

![在这里插入图片描述](https://img-blog.csdnimg.cn/becf4a39f3094f6fbe9aedb889c5ff59.png)

爆字段

![在这里插入图片描述](https://img-blog.csdnimg.cn/47fefbef6e724825b3848dc228f65eb8.png)

获取信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/ef7b5eafab6c4c58bce3da285d9f6aa9.png)

然而这些东西并没有什么用

尝试写入文件，发现有waf

![在这里插入图片描述](https://img-blog.csdnimg.cn/e0c12cf460d64dfc8122b2f582d46aa6.png)

payload转hex

![在这里插入图片描述](https://img-blog.csdnimg.cn/eb95faf265f34d83aba427e6631b0eb6.png)

通过lines terminated by追加内容

![在这里插入图片描述](https://img-blog.csdnimg.cn/476bda8af1b34a48ab61b6eab3031d60.png)

写入成功，直接用python3reverse shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d453a2499ee4ab59243e6bd91e9982c.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/5d3d15a775c0438fb3b56acd8e847e60.png)

## 横向移动

在dylan的家目录有一个work_analysis文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/94c198db9ae94a0986a6bcc5a598fe6c.png)

这看着像是ssh日志，并且记录了被ssh爆破的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/50ef54602fc64cd29c6e6032580ac4d5.png)
过滤dylan，dylan后应该就是密码，它一定是忘记回车了

![在这里插入图片描述](https://img-blog.csdnimg.cn/561b903347584e39998089628f4448ca.png)

ssh直接登，同时拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/87f7205af5724a6abc22da12bec78c89.png)

## 权限提升

在根目录下有个gitea

![在这里插入图片描述](https://img-blog.csdnimg.cn/b97fde8f42fc492c9e2cdc0ce0393c0a.png)

本地开了个3000

![在这里插入图片描述](https://img-blog.csdnimg.cn/4da566f34d25408d8bd761991fb0ba45.png)

ssh做一下本地端口转发

![在这里插入图片描述](https://img-blog.csdnimg.cn/294d0c650828478586069fa49961a3d5.png)

进本地3000，用dylan的凭据登录，有2fa

![在这里插入图片描述](https://img-blog.csdnimg.cn/76b72bdb065d4854ae9c48bc09a6f805.png)

创建一个账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/5d1a5e28999243739fa63dece7809a62.png)

在/gitea目录下有个gitea.db文件，并且dylan是所有者

![在这里插入图片描述](https://img-blog.csdnimg.cn/2b104a4ff44c4ef799c987a34c92f4c4.png)

下载到攻击机查看

由于我们是db文件的所有者，我们可以修改数据库，将我们的账户设置成admin，再覆盖掉原文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/179ce729d5d849ca931f7f8f67548c4c.png)

但这样做似乎并不行

再找到two_factor表把2fa code给删掉，然后再登录dylan

![在这里插入图片描述](https://img-blog.csdnimg.cn/f9b44df6aaf7433abed5890d536b7c73.png)

依然不行，我不理解

从官方文档找到，gitea允许http base身份验证，这意味着我们可能可以绕过正常登录时需要验证2fa

![在这里插入图片描述](https://img-blog.csdnimg.cn/c844e8acd21943c6a3de502696ea3e9c.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/4801ac09c47748dc9cffe243e2884f52.png)

成功进来，再使用burp的匹配和修改规则为我们的每个请求自动添加上该请求头

![在这里插入图片描述](https://img-blog.csdnimg.cn/2866aa05231542699b79a9398f4b171b.png)

在一个仓库里有几个githook，这由sh脚本编写，这意味着能利用其来执行命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/7d5fec19d883445c91787a2b498d788d.png)

写payload

![在这里插入图片描述](https://img-blog.csdnimg.cn/965d6944557a46a59d3323dfe8bfc612.png)

随便修改readme.md然后提交

![在这里插入图片描述](https://img-blog.csdnimg.cn/cf335b58ca3046eb9d03bfceb06aef10.png)

同时getshell

查看sudo -l，直接到root，但在docker里

![在这里插入图片描述](https://img-blog.csdnimg.cn/449d9694e9f1493e9772e995a0b5c40f.png)

在根目录下有个/data, 与宿主机/gitea一致

![在这里插入图片描述](https://img-blog.csdnimg.cn/ff470126a2e7455cbe23d5891b5d1dc8.png)

他们是连通的, 应该是挂载过去的

在docker中我们是root，那么就可以直接cp一个带root suid的bash过去，dylan就可以利用其提升到root

由于docker里的bash在宿主机用不了，需要先在宿主机复制个bash过去再由docker里的root操作

![在这里插入图片描述](https://img-blog.csdnimg.cn/59752949821c4af0843976af25943f5c.png)

dylan利用

![在这里插入图片描述](https://img-blog.csdnimg.cn/f57f5aca78c1486eaefd6ff52c1a4393.png)

getroot
