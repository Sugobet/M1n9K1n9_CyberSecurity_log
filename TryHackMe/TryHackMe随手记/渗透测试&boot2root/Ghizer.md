# Ghizer

Lucrecia在服务器上安装了多个Web应用程序。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/a30fac668fcf40f3a5f1285b66cf6722.png)

## FTP枚举

anonymous进入ftp，发现登录失败

![在这里插入图片描述](https://img-blog.csdnimg.cn/8095f97fc7494f7f8a87b926ca1a3444.png)

## Web枚举

80端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/ff68ca28dd13463289843623a01e5a48.png)

443端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/92d320634cef4894bbf7ba37c3e2895f.png)

### 目录扫描

先看80，上gobuster, 扫到不少目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4ba6e99707a49849173f10e4e369cf4.png)

在/docs/release_notes.txt中，暴露了LimeSurvey版本号

![在这里插入图片描述](https://img-blog.csdnimg.cn/a76f310af9fd4211b6b0b1a575b71b3f.png)

searchsploit给出了一个关于<3.16版本的rce漏洞

![在这里插入图片描述](https://img-blog.csdnimg.cn/22e625f56ca3461d9fd7f5f62ed3d730.png)

但需要一组有效凭据，我寻找了很久，因为东西很多，但仍然没找到信息

由于有csrf的存在，爆破麻烦了点，在项目的github上找到默认凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/e91aecd992054b7d9748141b96aeea51.png)

使用默认凭据成功登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/0aee601311df43cc96ec95c4fc2ad01f.png)

有了这组凭据我们可以尝试rce

![在这里插入图片描述](https://img-blog.csdnimg.cn/3ce9849f69f4444b9e0e9bf9b481ba86.png)

利用失败

在NVD又找到两个新的

![在这里插入图片描述](https://img-blog.csdnimg.cn/31655ac3d2dd4e0da98b5bd6bf0a1cba.png)

对于CVE-2019-9960

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a92c0947a354fe68d76184057f429ed.png)

在downloadZip函数中，sZip参数未经过安全检查，导致目录穿越，最终造成任意文件下载

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f160b2dcbba471bb56aa3d3d8b1b534.png)

虽然下载的是zip，然鹅是我们读取的文件的数据本身

![在这里插入图片描述](https://img-blog.csdnimg.cn/27faaa917d9746e9b826182cfecab50b.png)

从官方存储库当中可以找到config.php所在位置

![在这里插入图片描述](https://img-blog.csdnimg.cn/16d23da9630448d181dd87b6a15fae57.png)

利用刚刚的漏洞下载配置文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/224d0e83e21b48388597d2b5aa280f37.png)

跟着任务，我们现在应该到443端口了

一下子找到了login

![在这里插入图片描述](https://img-blog.csdnimg.cn/c5019591cf6c44958bcf047cb4ba8374.png)

使用刚刚找到的凭据即可登录进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/cac77618b856450f8cd6a7abda017908.png)

## Reverse Shell

老方法写shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/1e29a224b2624bba9fef6cecec848859.png)

但是似乎有检查

![在这里插入图片描述](https://img-blog.csdnimg.cn/19165020056e4d52b9656ba578aa077d.png)

那就利用插件编辑来getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/f9999a4d1a8840c19e7a97561c4a1521.png)

访问：

	https://10.10.215.70/wp-content/plugins/akismet/index.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/5475763121e34d0da587816945ce68e9.png)

getshell

## 横向移动

在veronica家目录发现ghidra9.0，但没找到能利用的漏洞

在ss命令发现两个可疑端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/142bc8ee63794f88b83ba026ad9ada23.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/bddd017a21714f44b48d66922dad41f5.png)

现在可以确定这两端口是ghidra开启的，并且是调试模式，它可以执行代码

那么如何连接呢，让大牛解答一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/bd299710e9584259bb5380d44dd78474.png)

按照大牛的说法，成功连接上

![在这里插入图片描述](https://img-blog.csdnimg.cn/cc95868431664928b019f082dd0b0225.png)

由于不熟悉这方面，为了节省时间，瞄一眼wp

![在这里插入图片描述](https://img-blog.csdnimg.cn/145b898acac3462db4b9e963a452a2cf.png)

reverse shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/a9823b36bc9e41c9927c1fd2e13f5ad3.png)

成功过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/8f91d798d53a4551992be72f52c88f54.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/c68aa9d313f74a42bea7bcb135a7d1ce.png)

这个py文件在我们家目录下，那就好办了，我们可以直接删除该文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/ec8e73ea3a4f415eaefdb61eac8fd63d.png)

这个技巧已经用过好几次了，那为什么可以这样做呢？

根据我之前的测试得到的结果，我简单解释一下

1) 假设root在账户A的家目录创建了一个000权限的文件，账户A可以无视acl直接rm；

2) 如果root在账户A的家目录创建了一个文件夹Tests，同时在Tests里面创建了一个000权限的文件，账户A无法删除Tests文件夹或里面的文件；


 3) 如果账户A创建了个Tests文件夹，root用户账户在这个文件夹里面创建了个文件，账户A可以直接rm

4) rm的时候，rm会找上级的目录的权限，相当于这个文件的权限被忽视了

5) 貌似似乎只有rm可以，如果想对文件做其他读写执行的操作就会遵循文件本身的权限


回来，现在我们重新创建一个base.py

![在这里插入图片描述](https://img-blog.csdnimg.cn/08ab27ac5b6e4da892730dc5f13227ad.png)

sudo执行

![在这里插入图片描述](https://img-blog.csdnimg.cn/9216bdbd93f44a449d8471fce8873deb.png)

getroot