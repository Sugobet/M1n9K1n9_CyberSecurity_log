# 漏洞

nvd: https://nvd.nist.gov/vuln/full-listing

exploit db: https://www.exploit-db.com/

### 手动利用：

    部署附加到此任务的计算机，并等待至少五分钟以使其完全设置。
    五分钟后，通过导航到连接到 THM 网络（您自己的或 AttackBox）
    的设备浏览器来访问机器上运行的网络服务器

attack box有点卡，这边选择使用本地kali远程连thm靶机

    http://10-10-20-80.p.thmlabs.com/

题目要求获得web目录下的flag

打开页面首先翻看源代码，看到网站的框架使用：online books store v1.0

这个信息很重要。

然后我并没有第一时间去exploit db上搜，先自己琢磨一下，发现有几处地方存在sql注入：

    http://10-10-20-80.p.thmlabs.com/book.php?bookisbn=9' union select 1,database(),3,4,5,6,7%23

    http://10-10-20-80.p.thmlabs.com/bookPerPub.php?pubid=-1%27%20or%20updatexml(1,concat(0x7e,database()),1);%23

因为这里不是重点，所以就不继续下去，

尝试/admin.php，结果还真进去了，刚准备burp suite爆破，结果随手一输admin，密码123，还真进去了

进到后台可以增删改book数据，/admin_add.php可以增加book数据，还可以上传图片，于是尝试.txt、.php等的后缀，发现是可行的，根据首页源代码分析，这里上传的"图片"都被保存到了/bootstrap/img/

经过反复抓包尝试，发现后端在admin_add.php进行操作时并没有进行身份验证，任何人都可以直接通过admin_add.php上传文件，之后我们就可以上传php一句话实现rce了。

但是我们访问/bootstrap/img/，该目录可直接访问，并且flag.txt就在这里

THM{BOOK_KEEPING}

(最后我们进入exploit db查找该版本的框架，发现的几个漏洞也是跟这里基本一模一样)
