# Burp Suite

首先是BS基础使用，很简单不解释。

刚学完基础和repeater、intruder的使用

    sniper: 单wordlist/单值，一对一
    batering ram: 单wordlist/双值，一对二
    pitchfork: 两个wordlist/两个值，一对一
    cluster bomb: 多个wordlist/多个值，多对多


有意思的点应该 intruder爆破中，，场景：

    爆破用户名密码进行登录，但每次http请求都需要携带随机的parameters或随机的session

### Macros

这个时候就需要使用到宏，在intruder每次http请求之前先通过宏访问登录页面，
获取到parameters和session，再将parameters和session包含进intruder爆破的http请求里去。

从而实现了每次请求都会自动的携带指定的参数或cookie

    project options的sessions子选项卡-> Macors添加宏->选择url

    project options的sessions子选项卡-> rule为宏添加规则-> 可设置更新指定parameter/也可设置更新指定cookie信息

    设置rule的时候-> scope可以指定那个选项卡中生效 如: repeater、intruder......


learning...
