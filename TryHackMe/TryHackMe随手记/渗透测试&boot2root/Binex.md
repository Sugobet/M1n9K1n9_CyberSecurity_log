# Binex

枚举计算机并获取交互式 shell。利用 SUID 位文件，使用 GNU 调试器利用缓冲区溢出并通过 PATH 操作获得根访问权限。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/0fc2df4e972648f88a3b1b1050588365.png)

## SMB枚举

题目给了提示：Hint 1: RID range 1000-1003 Hint 2: The longest username has the unsecure password.

使用enum4linux枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/8c976838f0cd438c83991e1377c55b2b.png)

根据上面的提示，爆破tryhackme用户

![在这里插入图片描述](https://img-blog.csdnimg.cn/bf22a0fe7c5c4fb2b1e4ad1a12628fcc.png)

## 横向移动 - SUID

登录进来之后查找suid

	find / -type f -perm -u+s 2>/dev/null

发现find具有suid，那么可以利用其移动

![在这里插入图片描述](https://img-blog.csdnimg.cn/5288b21b62614dca8454cc7cea8ce8e2.png)

## 缓冲区溢出

在des家目录下有一个suid的文件，并且还有一个c文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/f8b82fa165d54b5ab0ba52174a022d00.png)

在第五步的时候遇到了困难，这里的缓冲区溢出貌似与之前thm教授的似乎不太一样，所以直接看wp学

还是有点难理解，可能是因为对于这方面还是过于薄弱，还是要保持学习吧

那么现在让我们先完成房间，根据大佬wp的教程，我们能够获得kel的shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/2016a2e92df446a2961b9a0f947bab8e.png)

## 环境变量提权

kel家目录下的exe和exe.c

![在这里插入图片描述](https://img-blog.csdnimg.cn/ae2967a4378f4f0e8f823845cd5a2806.png)

这里可以通过修改PATH来执行我们的“ps”程序

![在这里插入图片描述](https://img-blog.csdnimg.cn/2d96d732a2974614b1e7bf3471a2ac72.png)


## 结束

其实这个房间最大的亮点应该在缓冲区溢出，只是奈何在这方面还是吃亏了，后面有时间的话再回来补一补这方面的基础吧
