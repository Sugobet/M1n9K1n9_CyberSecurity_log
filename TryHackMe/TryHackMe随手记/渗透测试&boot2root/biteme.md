# biteme

远离我的服务器！

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/f9aa76bc6aaf470997534ddbf00b1c94.png)

## Web枚举

打开一看是一个默认页面

![在这里插入图片描述](https://img-blog.csdnimg.cn/9a2497abe5c543009b8ca0cdef322be4.png)

扫一波

![在这里插入图片描述](https://img-blog.csdnimg.cn/8dc584dccbc54f2e9edfe80bc3c30c4c.png)

打thm这么久，貌似还是第一次见带验证码的登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/e72f091fca694bbfaae3b924cde0d79a.png)

信息有限，对着/console再扫一波

![在这里插入图片描述](https://img-blog.csdnimg.cn/d8586990fbb3445da5eeb53aa6357f7f.png)

查看/securimage

![在这里插入图片描述](https://img-blog.csdnimg.cn/1f13f601fe604c16ba636de70e980f1b.png)

但似乎没有找到能利用的信息

回到console, 在源码发现一个做了混淆的js

```javascript
      function handleSubmit() {
        eval(function(p,a,c,k,e,r){e=function(c){return c.toString(a)};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('0.1(\'2\').3=\'4\';5.6(\'@7 8 9 a b c d e f g h i... j\');',20,20,'document|getElementById|clicked|value|yes|console|log|fred|I|turned|on|php|file|syntax|highlighting|for|you|to|review|jason'.split('|'),0,{}))
        return true;
      }
```

将其丢到浏览器控制台

![在这里插入图片描述](https://img-blog.csdnimg.cn/f1ce0977aa254a9caaaf88eee68d2186.png)

搜索一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/1fc3e423c57148bc9d84d12f47462c41.png)

**瞬间黑盒变白盒**

![在这里插入图片描述](https://img-blog.csdnimg.cn/21125206797941ef8316e06512d1014b.png)

跟到functions.phps

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b0c9d27bcaa46ac8cca232e186020a7.png)

继续跟到config.phps

![在这里插入图片描述](https://img-blog.csdnimg.cn/69e7fd9ab68d43e8abc886d0362e3124.png)

在functions.phps中，通过将$user转十六进制去验证的，那么这一串字符串肯定就是十六进制字符串，使用xxd解码

![在这里插入图片描述](https://img-blog.csdnimg.cn/b489db204bf5460dbb994fbce4560018.png)

得到一个账户名

那么对于密码：

```php
function is_valid_pwd($pwd) {
    $hash = md5($pwd);

    return substr($hash, -3) === '001';
}
```

这段代码将会将$pwd进行MD5，然后判断MD5的后三位是否为001

这里python写个脚本

```python
import hashlib


with open('/usr/share/wordlists/rockyou.txt', 'r', encoding='ISO-8859-1') as f1:
	for val in f1.readlines():
		val = val.strip()
		has = hashlib.md5(val.encode('utf-8')).hexdigest()
		
		if has[len(has)-3:len(has)] == '001':
			print(f'{val} : {has}')
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/89d8dd9f8f6c4e328899da30026588e7.png)

如果你的电脑足够强悍，也可以试试这个bash一句话

![在这里插入图片描述](https://img-blog.csdnimg.cn/71eb220e7e1744aaac2f3272557a2415.png)

使用刚刚获得的账户和脚本跑出来的任意密码，登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/ab87cb57ec574be0bee3bf3b6d1f1f71.png)

有mfa，但庆幸的是并没有任何输入次数限制，四位数字我们可以很轻松爆破出来

bash生成字典

![在这里插入图片描述](https://img-blog.csdnimg.cn/b80083fb2e5746ee8c21494a5342248d.png)

ffuf直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/b3108f49eea3470cb2d2113b0f98bd06.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/99980f835a6f4edd8c9576038c59f17c.png)

登录进去，发现直接就是一个文件包含

![在这里插入图片描述](https://img-blog.csdnimg.cn/e3b623744d964f26800d6b3c2982b70a.png)

但似乎无法通过伪协议造成rce

由于可以查看任意目录，发现jason/.ssh下有id_rsa，尝试读取出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/ac84deda5f3b4be381d6d4ad2edef182.png)

直接登录ssh，发现需要密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/ba16062457f4446aa304a19a86f72b7c.png)

ssh2john+john直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/f18f54bc6371427f81d29091097917b1.png)

成功进来

![在这里插入图片描述](https://img-blog.csdnimg.cn/10050f38693549a5bc8522b21281a4d2.png)

## 横向移动

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/81a732b0fbe64c13846489e0ca016c58.png)

直接移动到fred

![在这里插入图片描述](https://img-blog.csdnimg.cn/4cdc455f363048688f8c18f8da3c83b1.png)

## 权限提升

查看sudo -l

![在这里插入图片描述](https://img-blog.csdnimg.cn/47c2362b1b83475c856a860fdf59b15c.png)

又是些邪门歪道的提权

根据以往的经验，基本都是在配置文件中作妖

![在这里插入图片描述](https://img-blog.csdnimg.cn/6488ed8c601a433fbcaeec90fdfb27d9.png)

切换到配置文件目录，尝试find一下哪些文件我们当前用户所有

![在这里插入图片描述](https://img-blog.csdnimg.cn/caa59b8c84064d90aa320a0a6b53ac10.png)

果然有

![在这里插入图片描述](https://img-blog.csdnimg.cn/40dbb9c6e59b48a1b9aad1c5746968bd.png)

修改好后，重启服务

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d22577060564fa784ebb4ccd6dd09ef.png)

现在需要想办法触发它

在jail.local定义了相关规则

![在这里插入图片描述](https://img-blog.csdnimg.cn/206c5569c8b74bdcb933c10a23f3b9d8.png)

用hydra随便跑一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/f13293f9cd014a5d9dadc1ab6dd75089.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/00e329f71253460c9dc76194142f3c1f.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/52cccf3eb6314c458ac7ab47844293dd.png)

getroot