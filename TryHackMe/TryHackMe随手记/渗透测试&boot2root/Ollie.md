# Ollie

臭名昭著的黑客狗Ollie Unix Montgomery是一位伟大的红队员。至于发展...没那么多！有传言说，Ollie弄乱了服务器上的一些文件，以确保向后兼容性。在时间用完之前控制！

![在这里插入图片描述](https://img-blog.csdnimg.cn/720457720fdd41ae8490561d7b8968f1.png)

---

## 端口扫描

循例 nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/4b535f0bbd3e4d509d32fe9fc7b2a9b9.png)

## Web枚举

进80，直接一个登录页面，循例看看源代码，顺便gobuster扫了一波

没有什么获得太多信息

回到登录页面，查看底部

![在这里插入图片描述](https://img-blog.csdnimg.cn/d49778bfc52d4a4d9a5285e21ecf02ec.png)

phpIPAM 1.4.5, 存在一个rce, 这是通过sql注入写入文件导致的

![在这里插入图片描述](https://img-blog.csdnimg.cn/81ac543bac5542238f39b61e07c5cc30.png)

但需要一组凭据，但到这就断了，回到端口扫描并重新进行它，发现1337端口是开着的

![在这里插入图片描述](https://img-blog.csdnimg.cn/59d3276af0954385aa6f6e280b0d485c.png)

不知道是什么服务，用nc尝试连接

![在这里插入图片描述](https://img-blog.csdnimg.cn/0ca547e85d8b4cbeb0d388e8af85f837.png)

回答一些问题，我们将获得admin的凭据，有了它，我们就可以回去rce

![在这里插入图片描述](https://img-blog.csdnimg.cn/9ed70a5a3c954cc183c2bc24e760a68c.png)

利用rce来常规getshell

## 横向移动

### 密码重用

我在shell中一顿翻，都没有什么信息

config.php中的数据库密码无法在ollie账户使用

在准备查找能利用的内核漏洞时，我忽然想起还有一组凭据，就是刚刚admin的，使用这个密码登录ollie，成功了

![在这里插入图片描述](https://img-blog.csdnimg.cn/48efc27d7dda4479b75989469ef25bb9.png)

user.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/451ade1b4dc445a883834f6ac7d886e9.png)

## 权限提升

查找可写入文件时发现

![在这里插入图片描述](https://img-blog.csdnimg.cn/72f9f1db474641b2993335c3826c2766.png)

我们有权读写

![在这里插入图片描述](https://img-blog.csdnimg.cn/647f72ed2d24481bb466b0c5cacc0708.png)

这是一个bash脚本，虽然我们没有在sudo或者crontab中发现它，但经验告诉我们，这极有可能是定时脚本

![在这里插入图片描述](https://img-blog.csdnimg.cn/7b289dfbf0a94df2aa63a31043e71cbd.png)

修改它

![在这里插入图片描述](https://img-blog.csdnimg.cn/3cedb057327f4721ab2fc61df5b9b493.png)

nc开启监听

![在这里插入图片描述](https://img-blog.csdnimg.cn/7585ec45ad5048f6a15b73a42566f7e8.png)

getroot