# Inferno

现实生活中的机器+CTF。该机器被设计为现实生活（也许不是？），非常适合刚开始渗透测试的新手

“在我们人生旅程的中途，我发现自己身处一片黑暗的森林中，因为直截了当的道路已经迷失了。我啊！说这森林野蛮、粗犷、严厉，这是多么难说，这在一想到中又让人感到恐惧。

机器上有 2 个哈希键（用户 - 本地.txt和根 - 证明.txt），你能找到它们并成为 root 吗？

**请记住：在地狱的九个圈子中，您会发现一些恶魔会试图阻止您的访问，忽略它们并继续前进。（如果可以的话）**

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/7aa4c4f553da492ea335c1f237f6b679.png)

开了一大堆端口

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/206ec315506644f1a83c5f6169f3ec38.png)

### 目录扫描

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e59fca183084613893a46bed5d1ad6b.png)

一个登录框

![在这里插入图片描述](https://img-blog.csdnimg.cn/42bb6ca136424d699fe96fecdce0f696.png)

由于扫描也没有扫到太多东西，没有什么信息，这里选择爆破admin

![在这里插入图片描述](https://img-blog.csdnimg.cn/aa58e06da4d74c47b942ece9439ad0ff.png)

登录进去又是一个登录框，使用刚刚的凭据就可以登进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/b80cf7976aed43acaeb3cc86a6077adf.png)

登录进去一个web ide

![在这里插入图片描述](https://img-blog.csdnimg.cn/d98e7c2a25d54ca88963c9accb09e602.png)

但是尝试编辑php写入shellcode的时候，却无法保存

## RCE to Reverse Shell

使用searchsploit发现存在rce

![在这里插入图片描述](https://img-blog.csdnimg.cn/97187701176b46448301471a432b3aaa.png)

但是由于进入/inferno需要http登录，这个exp不能直接用

需要为exp中的所有http请求添加认证的请求头：

```python
    headers = {
    		'Authorization': 'Basic Y**********x'
    }
```

执行exp

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d221a55e9b94d2e84bcba873befb8d4.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/508bb5928d11479280612de8b8b18038.png)

但是这个shell没过多久就会被杀死

![在这里插入图片描述](https://img-blog.csdnimg.cn/d4d847c6141a4200a4c9113bcc0c1f66.png)

这里使用msfvenom的-k参数生成一个shellcode

![在这里插入图片描述](https://img-blog.csdnimg.cn/dc78fce79277463d8b24fe331e134277.png)

再次运行exp之后，利用msfvenom生成的shellcode

![在这里插入图片描述](https://img-blog.csdnimg.cn/a2846f98cf4a4929af0097f3ced5d539.png)

此时，shell已不会再被杀死

![在这里插入图片描述](https://img-blog.csdnimg.cn/40eff94ee223485b98d9cb38a328394c.png)

## 横向移动

在我使用pty升级shell为bash的时候，我发现没过多久这个bash就被自动执行exit，但我使用/bin/sh就不会这样，**这意味着/bin/bash可能被监控**

不过没关系，使用/bin/sh也可以

![在这里插入图片描述](https://img-blog.csdnimg.cn/9cc72c63cab14180bdde58ca4f5b6019.png)

在dante家目录的Downloads下发现一个可疑文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/ebd26c9450084e8982dfd6b31fb7d37d.png)

查看这个文件，发现是一些长得跟16进制一样的数据

![在这里插入图片描述](https://img-blog.csdnimg.cn/82d5451fc3c84d46a2c839646bf1009b.png)

使用xxd转换

![在这里插入图片描述](https://img-blog.csdnimg.cn/7416f5cf259a45a1b93d4f1c6d5dfccd.png)

直接得到了一串似乎被打乱了的英文和dante的密码

但似乎并不是凯撒密码之类的，先不管了，su过去再说

![在这里插入图片描述](https://img-blog.csdnimg.cn/b6bd333cc398423897abead18925284d.png)

su过去之后发现又会自动exit

![在这里插入图片描述](https://img-blog.csdnimg.cn/f51d27a52ed44a9388da8a0771a577c9.png)

直接/bin/sh使用sh就好了

## 权限提升

有密码做的第一件事应该是查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/ac4df7339fa24eee9081e5797e19e3c8.png)

查看linux的living off the land

![在这里插入图片描述](https://img-blog.csdnimg.cn/2195070b3aa44bf2b02c38bc338dd168.png)

可以越权写入文件

首先使用openssl生成密码hash，然后组装

![在这里插入图片描述](https://img-blog.csdnimg.cn/395983a6f8bd40219da50074ed5aa135.png)

	hackerM:$1$hack$eu7wA.3faDMt9Z2srODT9/:0:0:hackerM:/root:/bin/bash


利用tee写入passwd

![在这里插入图片描述](https://img-blog.csdnimg.cn/9e880605c0144366b9c1ed88ca1e7c60.png)

su过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/12d3c32a656342909bf75cbb47ae0d8c.png)

getroot