# 身份验证绕过

### 第一个点：利用用户注册系统爆破用户名，如果某个用户名已注册则系统可能会回显已注册的信息

通过ffuf爆破，-mr匹配回显信息，以达到输出已注册的用户名，字典：/usr/share/wordlists/Seclists/Usernames/Names/names.txt



### 第二个点：通过刚刚得到的用户名，去用户登录系统爆破密码

首先我们注册一个账户，然后尝试登陆并故意输入错误密码点击登录，抓包发现status code是200，response中有回显信息密码错误；

然后再输入正确密码登录，登录成功，code是302跳转：response header的location字段跳转至：/customers，查看response header的时候无意发现了

    Set-Cookie: admin=false;......

这玩意不用猜都知道有什么用，我们先不管；

先通过ffuf爆破刚刚爆破得到的用户名的密码

    ffuf -u http://10.10.48.237/customers/login -H "Content-Type: application/x-www-form-urlencoded" -X POST -w ./usernames.txt:usr -w /usr/share/wordlists/seclists/Passwords/Common-Credentials/10-million-password-list-top-100.txt:pwd -d "username=usr&password=pwd" -fc 200

过滤status code为200的，剩下302的就是跳转成功的，即登录成功，最终获得正确密码


### 逻辑缺陷利用：

在这个thm的room中，提到一个点就是，php的$_REQUEST  post的data优先级高于get的query string

根据此特点，我们进入靶机的重置用户密码系统

这里也是经过我反复测试get、post传参。最终得出结论：

    1.后端首先通过$_GET获取email参数进行逻辑判断
    2.上述操作后，如果通过，则后端再通过$_POST获取username，然后与数据库比对，判断email是否与username匹配
    3.上述操作后，如果匹配，则使用$_REQUEST获取email参数然后发送重置密码邮件

问题就出在了第三点，只要我们在post的表单中手动添加一下非预期的email地址，就可已在第三点中将原本应该从get query_string取值，变成了从post data中取值，这个时候是绕过了前两点的。

构造：

    curl 'http://ip:port/customers/reset?email=某个用户的email' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=某个用户的用户名&email=黑客的邮箱'

这样我们就顺利的将某个账号的重置密码邮件发送到我们所指定的邮箱里去。


### 最后一个点：cookie篡改

也没什么有意思的，挺简单，

    https://crackstation.net/

    https://www.base64encode.org/
