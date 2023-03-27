# Madeye's Castle

一个boot2root盒子，由Runcode.ninja团队在CuCTF中使用的盒子修改而来

祝你冲进麦德耶的城堡玩得开心！在这个房间里，你需要完全枚举系统，站稳脚跟，然后转向几个不同的用户。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/f2f189997573489db63d15576529590a.png)

## SMB枚举

smbmap看一眼

![在这里插入图片描述](https://img-blog.csdnimg.cn/37407567473849789fd45839e9dc1d38.png)

smbclient进sambashare

![在这里插入图片描述](https://img-blog.csdnimg.cn/63bbc779111a408582c44493999077c0.png)

spellnames可能是一些用户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/2c769ad9ed4642aeb9977c4878f91cf3.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/3837dd1f37f64f3787d968b4088a5ddf.png)

## Web枚举

进80，一个默认页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/bfdbc0681169477fb0946255bbba5989.png)

上gobuster

![在这里插入图片描述](https://img-blog.csdnimg.cn/179dc7cf436340a589b7dd5fb05cb94c.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/ba0988faaa594daab91615e223e8f9c4.png)

无法查看目录，继续扫一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b97524d674c409b94419558d912742b.png)

扫到个email/

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f35ffd9390d4ab58c9d0640a205bb9f.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/be2789515b5b447da3c6c6511ba4161c.png)

这里披露了一个域名

	hogwarts-castle.thm

根据刚刚页面提供的信息，需要将s改成z

	hogwartz-castle.thm

将其添加进hosts

访问, 一个登录页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/460de6c8a8cf49cd9456b739bfde3f01.png)

这里存在sql注入, 不过是sqlite

![在这里插入图片描述](https://img-blog.csdnimg.cn/6262d44f979d4bf6b45609d22500f29f.png)

爆表

![在这里插入图片描述](https://img-blog.csdnimg.cn/dfa2a70b73154f84b00ced5cac7761db.png)

爆字段

![在这里插入图片描述](https://img-blog.csdnimg.cn/987b4e7a3787489fa1a7943c649a0b74.png)

查看notes有一条有用的信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/d01ad65d51984936ba5b47a2877fae79.png)

我们知道了用户名，密码告诉我们的应该是hashcat的rule

我们需要通过hashcat的rule生成密码字典，在开头smb枚举的时候告诉似乎在告诉我们密码可能无法使用rockyou爆出来，并且同时给出了一个list

所以我们可以尝试使用best64对那个list生成新字典

![在这里插入图片描述](https://img-blog.csdnimg.cn/b5f4d263adb54204bc4a7f9d95b0ffe7.png)

这里选择直接离线爆从数据库得到的密码hash再直接登录ssh，因为在线爆ssh太慢了

![在这里插入图片描述](https://img-blog.csdnimg.cn/9c16ae57cba6418bb4f0bd90d70abc6b.png)

秒出

![在这里插入图片描述](https://img-blog.csdnimg.cn/8bfb5def9ba14e319551c0209120d7fa.png)

使用这组凭据登录ssh，得到flag1

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd0b3bcf1c42424192a9abaf30d2bafe.png)

## 横向移动

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/dc4cea477fde4866bed175f7cd97e339.png)

跟过去，执行/usr/bin/pico

![在这里插入图片描述](https://img-blog.csdnimg.cn/90b1cfd323184c13ab7355aa6e979a42.png)

竟然是nano

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a0c28a2446744d19a60ad6b877186ed.png)

sudo进到nano，然后ctrl^R + ctrl^x, 输入以下命令并回车

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c417b193d0740fe939805ff721401a0.png)

成功移动到hermonine, user flag2

![在这里插入图片描述](https://img-blog.csdnimg.cn/5d1f713511694b54babf36e8737bd800.png)

## 权限提升

查找suid

![在这里插入图片描述](https://img-blog.csdnimg.cn/45ec4e32ffbc4889ac0cfd7d1169b5be.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/a7570cb1f7eb4c6586d0bf896a679bea.png)

使用ltrace跟踪到调用srand和rand

![在这里插入图片描述](https://img-blog.csdnimg.cn/7dfb4a029f89442b802af34070a27a04.png)

这里又有个问题，一旦我们快速运行程序，它所使用的种子将不会改变，即得出一个一样的随机数

![在这里插入图片描述](https://img-blog.csdnimg.cn/f46128109b524f1d895babcffc90014d.png)

利用这一点写一个bash一句话

```bash
echo 1 | /srv/time-turner/swagger | grep -E '[0-9]*' -o | /srv/time-turner/swagger
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/3b06a977a2dd4b5499eeca279c32f24f.png)

使用strings查看的时候发现调用了uname

![在这里插入图片描述](https://img-blog.csdnimg.cn/64d364d849904b3caef31194e4944034.png)

那好办了，这还是suid，我们还是使用老方法，直接改环境变量调用恶意uname

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d216758c7af45aca288d72e126f9128.png)

利用刚刚的方法绕过随机数判断

![在这里插入图片描述](https://img-blog.csdnimg.cn/7161093deb5342ffbf8b94defe56d140.png)
![在这里插入图片描述](https://img-blog.csdnimg.cn/cac9cf344a6f4ec4a57e9cc6d0d74ecc.png)

getroot