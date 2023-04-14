# Ra

您已经找到了WindCorp的内部网络及其域控制器。你能打开他们的网络吗？

您已经获得了WindCorp的内部网络的访问权限，这家价值数十亿美元的公司正在运行广泛的社交媒体活动，声称自己是不可破解的（哈！这个说法太多了！）。

下一步将是拿走他们的皇冠上的宝石并获得对内部网络的完全访问权限。您已经发现了一台新的Windows机器，可能会引导您实现最终目标。你能征服这个最终老板并拥有他们的内部网络吗？

---

## 端口扫描

循例 nmap , 扫到不少端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/8edf4a9efc77498db78908dd3e566808.png)

在扫描结果中还有一个windcorp.thm域，将其添加到hosts

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/1386ccc6f9c9494fb3fb7dd27df7e3bb.png)

在主页列举了IT Support人员的邮箱，这或许会在后面的域渗透中有用处，先保存

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a44beb8d68c4d18b1ba8f55048de94d.png)

这里有个重置密码按钮非常显眼，获得一个子域将其添加到hosts

![在这里插入图片描述](https://img-blog.csdnimg.cn/bcfbeb9a857540e798d3e4b2de90c433.png)

重置密码需要回答一些问题，然而就在mainpage

![在这里插入图片描述](https://img-blog.csdnimg.cn/ac190156efae445baa074156686a43f8.png)

主页暴露了员工信息，但不多

![在这里插入图片描述](https://img-blog.csdnimg.cn/ca3811ec701a4feb9d5fe5d83e9b3614.png)

但查看源代码，我们将会发现猫腻

![在这里插入图片描述](https://img-blog.csdnimg.cn/21d542d1cd2d417db752ff571b9e748a.png)

从lilyle的图像和图像文件名来看，不难猜测，它的宠物狗名字应该是Sparky，而这正是我们重置密码所需要的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/b63e533ab4c340cb9fe45a1835f8dd3c.png)

我们获得了密码，但我找不到登录页面，尽管用gobuster扫了一圈

![在这里插入图片描述](https://img-blog.csdnimg.cn/caf2185af7d24f9a8d201f5799e30d4d.png)

到443端口的https，直接就是一个登录框，利用刚刚获得的凭据，能够登录进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/eaf570b368c34567b77c6d98b82f9ea0.png)

稍等一会，将会进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/59950e30b49a4a93acca55b95ca7aa39.png)

服务器管理这里有一台fire

![在这里插入图片描述](https://img-blog.csdnimg.cn/a7fec008e79744a1bdadf8705e0edba4.png)

然而我们现在暂无凭据能连接上去

## SMB枚举

使用lilyle的凭据，smbmap查看

![在这里插入图片描述](https://img-blog.csdnimg.cn/e3c8cc9dc3a142e2b48250bf4bf0b1e5.png)

flag1在Shared里

![在这里插入图片描述](https://img-blog.csdnimg.cn/2eeedef9826446de8fbd1b19eab7465d.png)

## 立足 - CVE-2020-12772

还有一些spark的文件，下载linux的版本看看

![在这里插入图片描述](https://img-blog.csdnimg.cn/7cffcf7c75764ddfab9d5cdbaa812b84.png)

尝试了其他文件，spark都无法运行起来，浪费了我许多时间

在NVD能找到一个有关spark 2.8.3的cve

![在这里插入图片描述](https://img-blog.csdnimg.cn/cd40c4f1f9cb418281e1861f7dbcf824.png)

通过向某个用户发送poc，只要该用户访问它，那么我们将能获得ntlm hash, 我们在进行web枚举的时候获得了一大堆账户名邮箱

由于我的环境问题，无法实现，但查看wp可以得知用户名是buse以及hash

通过hashcat爆破得到明文密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/41b3bd5949b740a79fad830330c4f79a.png)

evil-winrm直接登

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b88b32cb5264de9981464326ea6b605.png)

flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/c6637c7644c4426cbc012ed0899e307c.png)

## 权限提升

发现buse在Account Operators组中

![在这里插入图片描述](https://img-blog.csdnimg.cn/e13e504b65fc4a46825eb91fb4abe207.png)

查看一下官方文档对Account Operators的解释

![在这里插入图片描述](https://img-blog.csdnimg.cn/98d3157be9794d3e85dd2133bb7a2dda.png)

好吧，它似乎对我们暂时没有什么用，在c:\\scripts下有个ps1

![在这里插入图片描述](https://img-blog.csdnimg.cn/59617281c85a4744babd04b7f0c01ef2.png)

查看该文件，会读取hosts.txt内容，最终会读取每一行并通过Invoke-Expression执行

![在这里插入图片描述](https://img-blog.csdnimg.cn/8fa21d5bc8394da3abfcb4f304cd9bcc.png)

虽然我们当前用户buse无权查看hosts.txt文件，但我们可以直接修改brittanycr的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/c96eaad1f2ef416d98a64edf3345a0ad.png)

用smbclient进Users的share

![在这里插入图片描述](https://img-blog.csdnimg.cn/a91f78f6ba924a1eab83e5c2a496b5e8.png)

put回去

![在这里插入图片描述](https://img-blog.csdnimg.cn/0c187f2a07c24d608206396359104784.png)

稍等一会

![在这里插入图片描述](https://img-blog.csdnimg.cn/03011d2afb5e493a9554fdf27ee04dda.png)

flag3

![在这里插入图片描述](https://img-blog.csdnimg.cn/48080aa791924058b66582f7175122a9.png)
