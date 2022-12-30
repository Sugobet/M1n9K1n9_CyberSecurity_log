# Blaster

在整个房间中，我们将研究不使用Metasploit的替代开发模式，或者除了nmap和dirbuster之外的真正开发工具。为了总结这个房间，我们将回到这些工具，以实现持久性和我们可以采取的其他步骤。事不宜迟，让我们部署目标计算机！

---

循例，nmap扫一下，靶机应该禁ping了

    nmap -sS 10.10.40.172 -p- -Pn

我醒目了，以后只要题目问开了多少个端口二话不说直接全扫

    80/tcp   open  http
    3389/tcp open  ms-wbt-server

我们应该到web上找线索

web是iis默认页面，我们可以使用gobuster扫一扫目录

    gobuster dir --url http://10.10.40.172/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt

结果：

    /retro                (Status: 301) [Size: 149] [--> http://10.10.40.172/retro/]

进去一看，这界面，非常的眼熟，当然我说的不是它的风格，而是这道题，在进攻性渗透测试中有一道这样的复古题。

根据经验，我们直接找到帖子：Ready Player One

帖子下有一条关于密码的评论

    Leaving myself a note here just in case I forget how to spell it: parzival

结合3389端口：

    wade
    parzival

尝试登录rdp

    xfreerdp /u:wade /p:parzival /cert:ignore /v:10.10.40.172 /workarea +clipboard

### [CVE-2019-1388](https://github.com/jas502n/CVE-2019-1388)

该漏洞位于Windows的UAC（User Account Control，用户帐户控制）机制中。默认情况下，Windows会在一个单独的桌面上显示所有的UAC提示——Secure Desktop。这些提示是由名为consent.exe的可执行文件产生的，该可执行文件以NT AUTHORITY\SYSTEM权限运行，完整性级别为System。因为用户可以与该UI交互，因此对UI来说紧限制是必须的。否则，低权限的用户可能可以通过UI操作的循环路由以SYSTEM权限执行操作。即使隔离状态的看似无害的UI特征都可能会成为引发任意控制的动作链的第一步。事实上，UAC会话中含有尽可能少的点击操作选项。
利用该漏洞很容易就可以提升权限到SYSTEM。

---

不以为然，又是相同的软件放在桌面上，我们直接双击它，然后点击：

    Show more details

    点击 -> Show information about the publisher's certificate

    点击 -> Issue by的蓝色链接

然后就可以关闭，回到桌面了，此时你会发现桌面打开了ie浏览器，这个浏览器是以system权限打开的。

我们按下：

    Ctrl + S

调出文件管理器，在路径输入的地方输入：cmd.exe

即可获得system权限的cmd

---

### msf建立持久性

由于目标系统上开启的AV，一旦我们上传恶意程序将会被查杀，所以我们可以借助msf：

    exploit/multi/script/web_delivery

该模块能够帮助我们在目标机器上 在内存中加载shellcode，这样就躲避了AV对磁盘的查杀

我们可以使用：

    meterpreter > run persistence -h

快速为我们建立持久性
