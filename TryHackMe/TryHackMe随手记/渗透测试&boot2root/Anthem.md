# Anthem

在这个初学者级别的挑战中利用Windows机器。

---

循例 nmap：

    nmap -sS 10.10.140.29 -Pn

只开了80和3389，上web看看

看主页源代码的时候发现个flag:

    THM{G!T_G00D}
    THM{L0L_WH0_US3S_M3T4}

gobuster扫一波，/SiteMap有好几个页面，其中

    http://10.10.140.29/authors/

下有个flag

    THM{L0L_WH0_D15}

/archive/a-cheers-to-our-it-department也有：

    THM{AN0TH3R_M3TA}

robots.txt的第一行，虽然我也不知道是什么，但是拿去一顿提交，这是密码：

    UmbracoIsTheBest!

/umbraco是后台登录页面

这个页面/archive/we-are-hiring/，有名字和邮箱，拿去尝试登录

不行，看提示，复制那首诗去谷歌：

    Solomon Grundy

jane-doe的邮箱是jd@，那Solomon Grundy可能就是sg@

登录rdp:

    xfreerdp /u:SG /p:UmbracoIsTheBest! /cert:ignore /v:10.10.140.29 /workarea +clipboard

提示告诉我们hidden,打开文件管理器显示隐藏文件，在C:\下发现backup文件夹里面有一个txt，里面就是密码

登录admin rdp

    xfreerdp /u:Administrator /p:ChangeMeBaby1MoreTime /cert:ignore /v:10.10.140.29 /workarea +clipboard

root.txt就在桌面下
