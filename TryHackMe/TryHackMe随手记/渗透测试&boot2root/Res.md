# Res

在这个半引导式挑战中，使用内存数据结构入侵易受攻击的数据库服务器！

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/1bcbfcbdccdd48c980b4431655701eec.png)

## Redis枚举

redis-cli连接

![在这里插入图片描述](https://img-blog.csdnimg.cn/118f726715d24824a1be72b59e96e2cc.png)

根据hacktricks，我们可以尝试更改配置文件路径到Web站点根目录下，然后写入php一句话到配置文件，从而造成RCE

![在这里插入图片描述](https://img-blog.csdnimg.cn/f784737c33574975a4becad09ad6287d.png)

进到/backdoor.php，能执行命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/16f57be78a664672ab7397e9641edc95.png)

python3可用，直接通过python3getshell

![在这里插入图片描述](https://img-blog.csdnimg.cn/fcfeefa7cd344de5a811c2be53b1a69e.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/4729a49befec458d9ba04fab7e44d515.png)

## 权限提升

find suid发现xxd

![在这里插入图片描述](https://img-blog.csdnimg.cn/d1e1970205504abd91427c8366a740f3.png)

利用xxd造成任意文件写入

![在这里插入图片描述](https://img-blog.csdnimg.cn/19a6d9c97c274f5f91e7f0c9eeef11fb.png)

直接往/etc/passwd写入账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/a271ff2ffe2b4e15b625caae7bb0c6a6.png)

su过去，getroot

![在这里插入图片描述](https://img-blog.csdnimg.cn/bdd7460f9b3a40409cab3994011321b5.png)

最后从shadow中提取vianka的密码hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/10ccbbf418eb464eb66a72c2bc647865.png)

hashcat直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/eeb2814c16a24d4f9da07dfa193a23f0.png)

结束
