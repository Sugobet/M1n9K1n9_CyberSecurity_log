# Year of the Owl

当迷宫在你面前，你迷失了方向时，有时跳墙思考是前进的方向。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/da7d9671dc4646b9bca827692f3d06c0.png)

## SMB枚举

smbmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/c89d49667d294307b37b2095a4f22999.png)

enum4linux也什么都没有

## Web枚举

80端口

![在这里插入图片描述](https://img-blog.csdnimg.cn/ef2f0ef0664c443c8b969e35a8646a2d.png)

gobuster扫到一堆403，并没有什么有用的信息

443端口与80端口一致

47001端口依然什么都没有

## mysql

![在这里插入图片描述](https://img-blog.csdnimg.cn/69f1f583dcd3488dbae5ab098d68decf.png)

## UDP端口扫描

![在这里插入图片描述](https://img-blog.csdnimg.cn/cd39271fe54c44c898ce9433eb5faaf1.png)

什么都没有

看一眼wp，开了snmp，这时我才明白房间开头那句话的含义

## SNMP枚举

使用onesixtyone爆破团体名

![在这里插入图片描述](https://img-blog.csdnimg.cn/076b55485b4c44a481d81b2c31518702.png)

snmp-check获取信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/a519b6eb0f53494bae41e176a8cd3fcd.png)

有这么些账户

![在这里插入图片描述](https://img-blog.csdnimg.cn/20493a8b3c734c51b318d88b62a04019.png)

另外值得注意的是WinDefender的服务及其进程都开启了，这意味着我们可能要考虑到免杀

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f95222277314fdaa2969d8aa939f5b3.png)

## 立足

根据刚刚获得的用户名，拿去进行rdp爆破

![在这里插入图片描述](https://img-blog.csdnimg.cn/d797c8913c714263a84c0bd7f7763730.png)

jareth的密码爆了出来，但无法登录rdp

psexec也是没有权限访问

![在这里插入图片描述](https://img-blog.csdnimg.cn/99f250ba9fdd4467b46eaea2b3e7f8e6.png)

135端口也没开

winrm开了，用evil-winrm尝试

![在这里插入图片描述](https://img-blog.csdnimg.cn/31f5b9fb028c44b8885a79a81cf8f650.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/11d7d7b99a2a4067b33e7e437ff0291c.png)

## 权限提升

由于有WinDefender的存在，这里传一个winPEAS的经过混淆obufscated的版本

![在这里插入图片描述](https://img-blog.csdnimg.cn/08e59316e24042fe9f284f2482d93ae9.png)

好吧，它仍然被杀了

![在这里插入图片描述](https://img-blog.csdnimg.cn/d95a9c27600a4781b2b2788ca4bb0714.png)
c:\\下隐藏目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b6982d259e24d8a87b8e50fdd10d815.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d265ddd621f4f1f9c271fe6d7822886.png)

rid 1000里面有两个熟悉的文件 sam和system

![在这里插入图片描述](https://img-blog.csdnimg.cn/c310196b7bae43dfbd58631dd2b0dcea.png)

开启smbserver

![在这里插入图片描述](https://img-blog.csdnimg.cn/a317f13687c0496191b9f35593d852d1.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/fff99ef538ff4fbc948a49669855634e.png)

copy到攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/3a9606127e154f558de3e029d60c12fa.png)

secretsdump提取ntlm hash

![在这里插入图片描述](https://img-blog.csdnimg.cn/60532a886cfa4f83bcbba1338215b04b.png)

pth进winrm

![在这里插入图片描述](https://img-blog.csdnimg.cn/f512bf191aca4a95b8d3d6a7ae3e85e8.png)

admin flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/e3901d2febae45c5adf678f53ebf4ec9.png)
