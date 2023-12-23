# Format

Format 是一种中等难度的 Linux 机器，它突出显示了由解决方案的结构方式引起的安全问题。立足点涉及PHP源代码审查，发现和利用本地文件读/写漏洞，并利用Nginx中的错误配置在Redis Unix套接字上执行命令。横向移动包括浏览 Redis 数据库以发现用户密码，而权限提升则围绕以 root 权限运行的 Python 脚本展开，该脚本容易受到代码注入的影响。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2960ee8e-0ab6-d66a-3f57-98ad41a66c02.png)

### Web枚举

#### 80端口 - app.microblog.htb

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/cf1eb355-77a5-5ec8-8468-08b9a2bf015f.png)

#### 3000端口 - microblog.htb

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ed3d4cea-6e86-dfea-7668-4f6ce61f1683.png)

## Foldhold

和我预想的一样，gitea包含了app子域的源码，毕竟遇到这种情况的次数也不少了

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6527b7d1-10cf-b7c6-aea7-d43293409b47.png)

我们首先在app子域创建一个账号并登录

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e773769c-3cf7-9469-e3cf-8f2899fae90c.png)

这里有一个最显眼的功能也是唯一一个功能就是创建新博客，我们可以指定子域域名，我们在源码里面定位到那个功能的代码

一开始我把目光放到了addsite函数上

```php
addSite($_POST['new-blog-name']);


function addSite($site_name) {
    if(isset($_SESSION['username'])) {
        ...
        $tmp_dir = "/tmp/" . generateRandomString(7);
        system("mkdir -m 0700 " . $tmp_dir);
        system("cp -r /var/www/microblog-template/* " . $tmp_dir);
        system("chmod 500 " . $tmp_dir);
        system("chmod +w /var/www/microblog");
        system("cp -rp " . $tmp_dir . " /var/www/microblog/" . $site_name);
		...

```

我们应该可以尝试控制$_POST['new-blog-name']来尝试执行系统命令，但是我发现后端对new-blog-name进行了严格的过滤，只允许26个字母，所以使我打消了这个念头

```php
if (isset($_SESSION['username']) && isset($_POST['new-blog-name'])) {
    if(!preg_match('/^[a-z]+$/', $_POST['new-blog-name']) || strlen($_POST['new-blog-name']) > 50) {
        print_r("Invalid blog name");
```

我创建了一个test子域

在gitea中我看到一个sunny子域，我猜那个应该是由app子域创建的，所以我刚刚创建的test子域应该与sunny子域有同样的代码结构

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/376a61a3-d87e-9f2b-de2a-7c8eeae58761.png)

在edit/index.php中，我发现了任意文件读写

```php
//add header
if (isset($_POST['header']) && isset($_POST['id'])) {
    chdir(getcwd() . "/../content");
    $html = "<div class = \"blog-h1 blue-fill\"><b>{$_POST['header']}</b></div>";
    $post_file = fopen("{$_POST['id']}", "w");
    fwrite($post_file, $html);
    fclose($post_file);
    $order_file = fopen("order.txt", "a");
    fwrite($order_file, $_POST['id'] . "\n");  
    fclose($order_file);
    header("Location: /edit?message=Section added!&status=success");
}

//add text
if (isset($_POST['txt']) && isset($_POST['id'])) {
    chdir(getcwd() . "/../content");
    $txt_nl = nl2br($_POST['txt']);
    $html = "<div class = \"blog-text\">{$txt_nl}</div>";
    $post_file = fopen("{$_POST['id']}", "w");
    fwrite($post_file, $html);
    fclose($post_file);
    $order_file = fopen("order.txt", "a");
    fwrite($order_file, $_POST['id'] . "\n");  
    fclose($order_file);
    header("Location: /edit?message=Section added!&status=success");
}
```

尝试读取passwd

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b7834d35-22ec-fe28-f6ff-869a2bf7f9a8.png)

我尝试着在web目录下写入webshell，但很不幸的是应该是没有权限和解析php

### Nginx配置错误

读/etc/nginx/sites-available/default

```shell
...
location ~ /static/(.*)/(.*) {
	resolver 127.0.0.1;
	proxy_pass http://$1.microbucket.htb/$2;
...
```

[这篇文章](https://labs.detectify.com/ethical-hacking/middleware-middleware-everywhere-and-lots-of-misconfigurations-to-fix/)讲述了nginx的proxy_pass支持将请求代理到本地unix套接字

现在我们可以控制$1，我们看到register.php设置的字段

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c0e65089-2ef6-1c4b-e3fc-539c2a0d1077.png)


通过nginx的proxy_pass来对redis进行操作

将自己的账户的pro字段设置为true

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/52998d4d-2344-943d-e2bc-ba795fd08f81.png)

刷新一下

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/03e85f6e-50b3-9397-cdab-dde6fc4bffe7.png)

```php
function provisionProUser() {
    if(isPro() === "true") {
        $blogName = trim(urldecode(getBlogName()));
        system("chmod +w /var/www/microblog/" . $blogName);
        system("chmod +w /var/www/microblog/" . $blogName . "/edit");
        system("cp /var/www/pro-files/bulletproof.php /var/www/microblog/" . $blogName . "/edit/");
        system("mkdir /var/www/microblog/" . $blogName . "/uploads && chmod 700 /var/www/microblog/" . $blogName . "/uploads");
        system("chmod -w /var/www/microblog/" . $blogName . "/edit && chmod -w /var/www/microblog/" . $blogName);
    }
    return;
}
```

现在我们是pro，上面这些命令会使我们能够对uploads/目录写入文件，借此来getshell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5f15f3c0-95ff-0fee-b0a3-7f8e5ecd3008.png)

然后通过rce来使用祖传python3 payload

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1f5a4b40-1dcc-963d-f093-983b8dc8c74e.png)

## 本地横向移动 -> cooper

在redis发现了一个系统用户名的key

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/36a7ef4c-91b1-1cbc-9aaa-0b616c8a7594.png)

读一下发现了他的密码

	hgetall cooper.dooper

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a78048d3-4fdf-797c-c129-eb732fa04e71.png)

直接登ssh

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8ff951be-769e-b9e6-1d9c-5cc9bc18d7ff.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/61784329-4c92-7baf-c405-7e8083da6503.png)

这是一个python脚本

我们主要关注脆弱点

```python
    username = r.hget(args.provision, "username").decode()
    firstlast = r.hget(args.provision, "first-name").decode() + r.hget(args.provision, "last-name").decode()
    license_key = (prefix + username + "{license.license}" + firstlast).format(license=l)
```

这里的license_key由几个变量拼接进来然后format，应该存在模板注入，而username这些都是在redis读取的，我们可以控制redis来触发模板注入

```python
secret = [line.strip() for line in open("/root/license/secret")][0]
secret_encoded = secret.encode()
salt = b'microblogsalt123'
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=100000,backend=default_backend())
```

通过模板注入来获取secret，设置username

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/06fe808b-144f-a367-086a-986ac30fdf1f.png)

再次运行

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8cf77143-da29-c9e2-6e5b-4492ca5d1d66.png)

root flag还在老地方

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f4a4fa1f-ac2d-dc98-600f-6b9a0c5b56a8.png)
