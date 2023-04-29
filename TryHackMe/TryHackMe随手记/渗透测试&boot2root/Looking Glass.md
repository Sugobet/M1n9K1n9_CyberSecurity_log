# Looking Glass

穿过镜子。仙境挑战室的续集。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/777c5354071844f3a78183e1c7b5af34.png)

又是一堆ssh，跟之前的玩法一样

![在这里插入图片描述](https://img-blog.csdnimg.cn/5835d2a2fe2b4ccab57613e7ac86d24e.png)

找到正确的ssh端口之后后给了一段密文，要求输入secret才能进入ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/445d33c2fcb04ac69deb45d40a1ec96f.png)

这看起来非常像凯撒密码

唯一可识别的信息是Jabberwocky，我们找到了它

![在这里插入图片描述](https://img-blog.csdnimg.cn/cedf95abe22546d39e7e6a12cf1487ad.png)

它不是凯撒，因为解不开

谷歌随便找个分析工具，解得key

![在这里插入图片描述](https://img-blog.csdnimg.cn/41edd2462dfd45129d23cdf885567972.png)

cyberchf获得完整的明文，同时拿到secret

![在这里插入图片描述](https://img-blog.csdnimg.cn/02a5ed0aa569415aa1b9783b0f8dd477.png)

回去输入secret，给了一组凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/d11fe043084949acba51f908387eef5e.png)

拿着凭据回去登22端口的ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/b7256d9563d6497cbf97edcd4520533e.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/787b6c7a040d4f0b80fbedd0c0a73066.png)

## 横向移动

sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/0f7f30b8be2a499bb5d205990329bba8.png)

crontab还有个reboot的任务，该任务以tweedledum用户运行，该脚本归我们当前用户所有，这意味着我们可以控制它

![在这里插入图片描述](https://img-blog.csdnimg.cn/d1a58ceff9d84ede843aab65c7f48273.png)

为了节省不必要的麻烦，直接写个reverse shell的payload

![在这里插入图片描述](https://img-blog.csdnimg.cn/6adf00c93dff4b7988439c07fcdc010a.png)

直接sudo reboot，过来tweedledum

![在这里插入图片描述](https://img-blog.csdnimg.cn/35a768cd53d944ce934631f99afee266.png)

在家目录下的humptydumpty.txt，是一串hex

![在这里插入图片描述](https://img-blog.csdnimg.cn/e2c572a9cdec4d5fbfd649b59a0469cd.png)

xxd解码得到的是humptydumpty的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/04f69cc9deed41319e423da6035e5630.png)

在家目录下的poetry.txt有一段对话，但是不知道说的什么鸟语

![在这里插入图片描述](https://img-blog.csdnimg.cn/d8e748772fe14de4840dd542372ffd29.png)

这就有点没意思了，看了眼wp，在alice家目录下有.ssh/id_rsa

然而我们正常无权查看alice家目录下有什么东西

![在这里插入图片描述](https://img-blog.csdnimg.cn/392f88c9913449f78cac74cde3f9eb1d.png)

拿到id_rsa直接登，没密钥

![在这里插入图片描述](https://img-blog.csdnimg.cn/4595fb8ae71d40398dbacc920767ab68.png)

## 权限提升

在/etc/sudoer.d有个alice的规则，这是反向的hostname, 允许alice在这个主机名下使用root无密码运行bash

![在这里插入图片描述](https://img-blog.csdnimg.cn/910ae885f79a4fcf8d5f6c1283e368c5.png)

直接利用，同时拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/5af89cc7a95f43ca82bcd2a13ffddcdc.png)

## PwnKit

其实还发现了有个非预期的PwnKit，pwnkit可以直接打成功

![在这里插入图片描述](https://img-blog.csdnimg.cn/8bb3db98ba7642a98f59763c829bd114.png)
