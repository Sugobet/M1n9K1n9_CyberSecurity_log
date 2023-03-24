# Wekor

涉及Sqli，WordPress，vhost枚举和识别内部服务的CTF挑战;)

此 CTF 主要侧重于枚举、更好地理解服务以及对本机某些部分的开箱即用思考。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/263d7d8c33864855b45d41aaa7b9a1f9.png)

## Web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/4a297919bee3419581a4d01f99a9140c.png)

### 目录扫描

上gobuster

![在这里插入图片描述](https://img-blog.csdnimg.cn/cdead1aef1f24d6cb1f44d40f77b7385.png)

扫到个robots.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/7c172e95aabd47fc84d6d00dd4913871.png)

但这里的大多数页面都不存在，仅有一个

![在这里插入图片描述](https://img-blog.csdnimg.cn/6a4e63a0508e4b9abb2b06bb0b64b230.png)

跟着指引来到/it-next

![在这里插入图片描述](https://img-blog.csdnimg.cn/675c1d3cab2b4766b7741fd9b149eca2.png)

### SQLI

在该站点下一顿翻，找到一个点存在sqli

![在这里插入图片描述](https://img-blog.csdnimg.cn/5423453750714a7fbd4f8f0116da88c7.png)

上sqlmap，会找到一个wordpress的库，在里面能找到admin的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea21407901f1498d8c30d0e73ba3d236.png)

hashcat爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/c2189c42203743b8b23a3faab742b7cc.png)

最终的结果是，除了admin，其他用户都爆了出来

### vhost枚举

但这又有新的问题，当前站点并不是wordpress

题目开局给了域名，很容易猜测在某个子域下还存在一个wordpress

使用[我的武器](https://github.com/Sugobet/M1n9K1n9_CyberSecurity_log/blob/master/TryHackMe/My_Python_Scripts/SubDomain_Scanner.py)进行扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/a195a71d7a0c4327b944993db8ea7ae0.png)

扫出一个site

![在这里插入图片描述](https://img-blog.csdnimg.cn/e26925aa07c44ae291e14850345a6067.png)

将其添加进/etc/hosts

查看

![在这里插入图片描述](https://img-blog.csdnimg.cn/89e8d0cd4c0e4b3e9a290d5a957d3b41.png)

gobuster扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/add5713e59f1488fa68042d632657168.png)

## Reverse Shell

在刚刚的几组凭据当中，yura\@wekor.thm的凭据能够让我getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/68bb219f11bc42628898e589fd112913.png)

编辑php文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/e9d4312d7b934cde832a9b6880ed7319.png)

访问被修改的页面，getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/c2eb4e9f93fd4a4d8b4ac5a54a996e5f.png)

## 横向移动

ps aux ，发现11211端口是memcached

![在这里插入图片描述](https://img-blog.csdnimg.cn/df8c4c4505a047c2a97c987095e2a0be.png)

使用nc连接，枚举出Orka的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/5b47ce3b63694cc1ad0031a99731ec60.png)

升级shell

	python3 -c "import pty;pty.spawn('/bin/bash')"

直接su过去

user flag还在老地方

## 权限提升

sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/e73415aeb0e54448b31c3790351cc6b6.png)

使用strings时发现了这些函数

![在这里插入图片描述](https://img-blog.csdnimg.cn/02e8a34c9a8b4ea5ab90edde5a2d7703.png)

大致猜测是栈溢出

![在这里插入图片描述](https://img-blog.csdnimg.cn/b0abe91780c94e82b1c3443765ed4702.png)

将其传回攻击机

用gdb尝试了一下貌似并不行

但使用ida找到了password

![在这里插入图片描述](https://img-blog.csdnimg.cn/88c6c31b75ed4092bd07f3cecdc35d30.png)


---

回去看strings的时候发现了，相对路径的python调用

![在这里插入图片描述](https://img-blog.csdnimg.cn/27cb32a28b7d48cba582ac0ea53ee4db.png)

发现/usr/sbin Orka组可写

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d0d79cd8102490492a65ec90fbbca70.png)

查看$PATH，能发现/usr/sbin优于/usr/bin

![在这里插入图片描述](https://img-blog.csdnimg.cn/79c927bfb34449b4a655c1c223b7d6bb.png)

可以尝试往sbin，添加一个“python”

![在这里插入图片描述](https://img-blog.csdnimg.cn/097878cc6a584fcc9353dbfa485a9c02.png)

再次sudo执行那个程序，查看/tmp，它出来了

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f130ac3858343678989eab9ade233f5.png)

root flag还在老地方