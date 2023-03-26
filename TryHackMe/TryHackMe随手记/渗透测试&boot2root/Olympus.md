# Olympus

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/be977414f2774fa1ac9ab195dee006ad.png)

## Web枚举

进入80端口，发现跳转到了olympus.thm

![在这里插入图片描述](https://img-blog.csdnimg.cn/fb823f37fe7d4dbea6d67dd365af0f6d.png)

将其添加进hosts，继续访问olympus.thm

![在这里插入图片描述](https://img-blog.csdnimg.cn/53b6b2b90d6e4a07a6636d99a590f2d9.png)

### 目录扫描

gobuster扫一波

![在这里插入图片描述](https://img-blog.csdnimg.cn/fefcccfce9d04e2dbc8c29e9af7fc1eb.png)

查看/~webmaster，是一个cms

![在这里插入图片描述](https://img-blog.csdnimg.cn/1fc20ee88b6d46b592207c7e7791e44f.png)

通过searchsploit发现存在一个关于文件上传导致的rce, 以及几个sqli

![在这里插入图片描述](https://img-blog.csdnimg.cn/145b83b8af924a20991e45289f7c3bdf.png)

但当我想尝试rce时，我发现并没有注册用户的页面，即使主页告诉了我们有个账户存在弱口令，但似乎也无法登录，并且爆破不在本房间范围内

所以我把目光转向了sqli，其中，cat_id页面存在，故可能受漏洞影响

![在这里插入图片描述](https://img-blog.csdnimg.cn/afc3180fdd9c445abaa8340fbf28dd5e.png)

比较简单，直接上sqlmap提高效率

![在这里插入图片描述](https://img-blog.csdnimg.cn/706d8438cd1c49a09059ce1345e85f2b.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/554b64f13e784058891a01ce6558f891.png)

由于在cms主页当中，给了一条信息就是有两个账户中的其中一个可能存在弱口令，我就明白，root账户可以直接忽视了，rce也不需要有管理员权限，所以任何有效账户都可以。直接爆另外两个账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd029b2886984155858176b3cebf1590.png)

爆出了prometheus的密码，思路没有问题

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a09d56d933e4d5d95a2c105ed8e570a.png)

按照rce的步骤，进到profile上传反向shell文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/61624ccd326b46b0b69a1710622b96ce.png)

然鹅这里上传过去，/img无权访问，getshell失败

![在这里插入图片描述](https://img-blog.csdnimg.cn/7cbef4ab05da4f3ca056c36030659e38.png)

但在刚刚sqli中的结果里有一个子域，将其添加进hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/ca316a0165034b85991beba98acb69f3.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/8e16ad5a091543a793fcdd30b98c4272.png)

使用刚刚的凭据成功登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/2a58d23be86c4b60ace9f7251b36eb97.png)

扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/449a24d8b5ce4f16a2656a3a3e962b4f.png)

虽然就像它所说的那样，名字是随机的

但从前面的sql注入当中还是能发现一个叫chats的表

![在这里插入图片描述](https://img-blog.csdnimg.cn/2f8940094dbb437481421c677d92cdd3.png)

在这个表中能找到上传后的随机文件名

![在这里插入图片描述](https://img-blog.csdnimg.cn/5f32c8a730474f25bb9a58031be15802.png)

访问它

![在这里插入图片描述](https://img-blog.csdnimg.cn/5256d6458551469f84a9248468cfee1a.png)

getshell

flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/9477df38491c4d20ada6e7cc11fc6f34.png)

## 横向移动

zeus.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf83f957c88d48658c9059d857fd3191.png)

看到这个，联想到suid

![在这里插入图片描述](https://img-blog.csdnimg.cn/6851d525f5e84a5eb587f6ac7a7414e8.png)

有一个从未见过的cputils

执行它，它会以zeus的权限进行复制文件操作

![在这里插入图片描述](https://img-blog.csdnimg.cn/3509d827765840b1981207d1f1a3e76c.png)

在zeus家目录有一个.ssh文件夹，我们可以尝试利用它

首先在攻击机使用ssh-keygen生成ssh key

然后将公钥传到靶机

![在这里插入图片描述](https://img-blog.csdnimg.cn/d5e91f72199449d49ef8ba96da622434.png)

然后利用刚刚的cputils覆盖zeus家目录下的authorized_keys

![在这里插入图片描述](https://img-blog.csdnimg.cn/dc8b91d96b6642eeb230ce30aa0bf24e.png)

好吧，登录失败，这样貌似行不通，可能出题人早已想到这个

再试试把zeus的私钥复制出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/123dd14f058b4c8e8afbf718300e7f00.png)

复制到攻击机，ssh2john+john爆破

![在这里插入图片描述](https://img-blog.csdnimg.cn/bbc6ef403dba4193abe848e24858f88a.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/6bc0b071ea6f4f59ad45717b28732219.png)

成功登入

![在这里插入图片描述](https://img-blog.csdnimg.cn/8f73863720a84d548fb1832310e22524.png)

## 权限提升

查找zeus组所有的文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/502f13fe51024d1b8545381b1e32eefa.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d72ed4645804f669151bf888a45593d.png)

查看这个php文件，看起来是一个后门

![在这里插入图片描述](https://img-blog.csdnimg.cn/4233e524b0564ca0b75eb8e940fb7bb6.png)

输入密码之后

![在这里插入图片描述](https://img-blog.csdnimg.cn/4ad4591ea522490d96a1936d59355abf.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e86151d01324edf8e3ed1518a774839.png)

getroot

- 再一次，这并不是因为linPEAS没有标记任何明显的东西，没有什么是脆弱的。
- 我们已经习惯了糟糕的用户权限管理，但是，您也可以通过您的组分配权限！
- 当你发现一个奇怪的不寻常的文件时，即使看起来不多，也要调查！可能是某种东西！

但flag只给了一半，然后shell就断开了

![在这里插入图片描述](https://img-blog.csdnimg.cn/dddad228d8774a94b6281d3cd59a981e.png)

使用grep搜索flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/c73b7e3122b1416b914a067b6c49826e.png)

root flag和最后一个flag均能被找到