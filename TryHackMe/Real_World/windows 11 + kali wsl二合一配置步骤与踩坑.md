# windows 11 + kali wsl二合一配置步骤与踩坑

在前几天的某市攻防演练中，在攻防前期，我的虚拟机经常无缘无故出现断网、卡顿等现象，但找不出原因。

为了不影响后续的这些天的攻防演练，我选择在一个晚上通宵 在我的windows 11系统上快速搭建了wsl的kali 无缝模式，配置好之后的第二天，即通宵之后立马就开始使用它来进行攻防作战了，体验和效果还是相当不错的。

## wsl安装小问题

只要是在win系统上第一次安装wsl相信读者们应该都不会遇到什么问题，可能唯一会遇到的问题应该就是在微软商店中搜不到wsl

这里给出链接，下面的这个链接可直达微软商店wsl下载页面

	https://apps.microsoft.com/detail/9p9tqf7mrm4r?hl=zh-cn&gl=CN

## kali wsl

wsl安装好之后通过这个命令下载kali wsl

	wsl --install --distribution kali-linux

它会弹出新的窗口，让你填写kali创建的账户名和密码

安装好之后，我们有几种命令可以直接启动和进入它：

	# kali
	# wsl --distribution kali-linux

## win-kex安装配置

首先要做的就是通过apt下载win-kex

	sudo apt install kali-win-kex

当然，在开始之前，你可能需要先配置apt国内镜像源，这取决于你的网络环境

## kex无缝模式配置

无缝模式需要先安装VcXsrv

	https://sourceforge.net/projects/vcxsrv/

还需要安装vcredist140 ，这里有个值得注意的点，**必须安装**以下该链接的Visual C++ Redistributable for Visual Studio 2015 ( vcredist140 )

	https://www.microsoft.com/en-US/download/details.aspx?id=48145

如果你的机器上存在其它版本的vcredist14**x**，我的做法是在控制面版->卸载程序，直接卸载了其它版本，然后再安装vcredist140 

然后就是配置VcXsrv

打开它

display number设为0
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/9e97dc0151f6453dac8397bce1a8ff7f.png)

下一页默认

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4bc51ca256b546dd8e6328736f1c61c6.png)

下一页把禁用访问控制勾选上

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a885a56b0693447a802bec3fc5442964.png)

## 踩坑之路正式开始

当你兴致勃勃打开cmd输入以下命令，准备见证奇迹的时候

	wsl -d kali-linux kex --sl --wtstart -s

结果等了半天，发现VcXsrv一点反应都没有，会话没有建立成功

当你百度、csdn找了半天，最终找的方法都是配置网卡地址

但很不幸的是，你通过这些教程的命令，发现找不到网卡或是其它相关问题

但你通过本机ipconfig发现，其实是有的

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0b4e070802684bb59ce211a8ea69f701.png)

kali wsl

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a87a16b6a85c45cba0d0891b383b7c53.png)

## 解决方案

事实上连接不上的原因其实很简单，根据上图的kali wsl中的网络配置，你会发现有一个10.255.255.254的ip，然后再看cmd连接kex无缝模式时的**"10.255.255.254 找不到xxxxxxx"**

说明再无缝模式连接时，它寻找的ip是10.255.255.254，而这玩意是kali wsl的本机ip

所以很简单，我们只需要把要连接的ip修改为我们windows本机的wsl hyper-v的虚拟网卡地址就可以了，我这里是172.24.192.1

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/fb0df6c863f04b368e0be4f72608f265.png)

**修改的方法**很简单，只需要修改kali wsl的/etc/resolv.conf

	nameserver 172.24.192.1

这个时候你再尝试运行`wsl -d kali-linux kex --sl --wtstart -s`

你应该就会发现输出的信息当中，它连接的ip确实变成了172.24.192.1（具体情况取决于你实际的虚拟网卡地址）

**请注意，如果你还是连接不上，那么你需要重启VcXsrv软件，再强调一遍，请重启VcXsrv软件，并再次尝试kex无缝模式连接**

## 新的坑

那么这个时候相信都应该能连接上了，能够看到无缝模式下美丽的windows+kali结合体

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b6c8464b8d6d4aa193e46770d921dcf9.png)

**新的问题**又来了，其实也不算新问题，那就是/etc/resolv.conf的问题

总所周知这个文件是软连接到那个啥文件的，所以你每次重启，/etc/resolv.conf都会变回10.255.255.254，所以你每次刚开机想要连接，还得修改一下/etc/resolv.conf

那有没有什么好办法呢，还真没有，能试的我都试过了，相信不少读者也应该明白的，kali wsl网络配置方面跟实际的有点差异，缺少了某些配置文件，或者压根不生效等等之类的问题，导致nameserver一直被重置

## 解决方案

有一个简单粗暴且实用的方法可以一劳永逸。分为三步：

	1.unlink /etc/resolv.conf
	2.echo 'nameserver 172.24.192.1' > /etc/resolv.conf
	3.chattr +i /etc/resolv.conf

直接取消/etc/resolv.conf的软连接，然后自己新建一个/etc/resolv.conf，将内容改为我们想要的，然后用chattr加锁。

这样一顿操作下来，/etc/resolv.conf永远都不会变

配置好之后，以后就可以很轻松愉快的一键连接kex无缝模式了

[官方文档](https://www.kali.org/docs/wsl/)
