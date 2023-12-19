# Authority

终于把easy的机器刷的八八九九了，开始新一轮的Medium机器，Medium难度以上的我都会写wp，保持学习，我的CRTO进度也快结束了。

---

Authority是一台中等难度的 Windows 计算机，它强调了错误配置、密码重用、在共享上存储凭据的危险，并演示了 Active Directory 中的默认设置（例如，所有域用户最多可以向域添加 10 台计算机的能力）可以与其他问题（易受攻击的 AD CS 证书模板）相结合以接管域。

## 外部信息收集

循例nmap

	┌──(ming👻m1n9k1n9-parrot)-[~]
	└─$ sudo nmap -sS -sV -sC 10.10.11.222 --min-rate=1000 -p- --open -Pn

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b4671ba5-a5e7-6c7d-9fb8-7671545d0f7d.png)

一大堆常规端口

### SMB

smbmap看到一个share可读

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/3537cb28-a3f8-6e2c-a30f-7ffe81c3d4aa.png)

smbclient连上去看到一堆目录，直接全部下载

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/46458366-ea13-a294-218d-5969f5d5c3f7.png)

ADCS目录里面一下就找到了一个暂时没用的密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2d1a7b7e-f21f-4619-574f-5c56e6bce127.png)

还找到了一组无效凭据

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bccf4d92-dd79-3a4c-fe05-6d9f22a81e0a.png)

又找到了三个ansible加密的数据

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/501163d1-fba0-6e4a-576f-78b866bdd646.png)

分别保存到文件，ansible2john然后直接爆出解密密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a37f9049-05bf-ba9d-fd63-f656eea3a952.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/40064cb7-2819-62c3-8e2b-5176a386be3c.png)

解密

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8664e423-85cd-5c08-b81a-d537d370704d.png)

得到三个密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a6acb5bc-b61b-88bd-5dce-0c3573a26525.png)

## 8443 - LDAP回传攻击

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/05254003-a0f6-3b7c-2f0d-c13e55182d50.png)

使用svc_pwm的凭据可以登录配置管理器和编辑器

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9c687614-6279-3e9a-6c55-84b0feabd0d3.png)

在配置编辑里面很容易就能找到那个熟悉的东西

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9f938480-caa6-286d-c530-e8e5cc06f707.png)

在THM的AD教程中，我们曾学过LDAP回传攻击

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8da574cd-21a0-4797-f91d-b65c29445259.png)

responder跑起来，然后更改配置

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/dbfc93da-77f5-3047-b1ba-91edbe3dea8f.png)

点击test

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d8053057-af8c-b9ba-3e6a-f26a78a56fce.png)

responder捕获了svc_ldap的明文凭据

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/856412f5-ffa1-6c37-cd18-dc1a7859f45e.png)

直接登winrm

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1e59407f-9bdb-6c70-c5e6-8ec9f984c4c3.png)

user flag在老地方

## 域权限提升 - Easy ADCS

具有SeMachineAccount privilege

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f78b9e93-e659-a359-b844-ae051a004e91.png)

靶机简介已经提示了ad证书的问题，通过certutil获取所有证书模板信息

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b3c9e143-060f-e135-dce9-bb846c3baa8d.png)

查看结果，最后我把目光放到了这个证书模板上

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/391ddad5-8021-f7ea-d209-540834b17518.png)

首先它允许利用其来进行客户端身份验证

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2df0285e-e939-6d69-c75c-d54b6fae03f7.png)

我们还看到了CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT标志置为1，这表明我们可以更改主体别名SAN，即代表其他用户。

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f231da4e-766e-ac53-4a82-7b831165fa37.png)

最后需要关注的点则是查看谁有权限去注册证书

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/74bb62b6-8d88-20c0-1ce0-295d26db24fc.png)

进攻路线很明显，我们的svc_ldap账户拥有SeMachineAccountPrivilege，也就是说我们能够创建机器账户，利用机器账户来请求证书

### 创建机器账户

上传Powermad

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/130ff7e7-f62d-61f3-fe7c-119a5746f84c.png)

New-MachineAccount创建机器账户

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8cf014c8-a0c1-5b5b-99ac-fc408a941a95.png)

### 不支持 PKINIT 时使用证书进行身份验证

certipy利用机器账户请求证书

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d0243e20-c08e-062c-ea45-d2838d07c0e5.png)

证书是有了，但这个证书用不了，PKINIT不受支持，https://offsec.almond.consulting/authenticating-with-certificates-when-pkinit-is-not-supported.html

但可以通过LDAP来利用它，[PassTheCert](https://github.com/AlmondOffSec/PassTheCert/tree/main/Python)会帮助我们

通过certipy把私钥和证书导出，它将利用这两个东西利用证书来进行LDAP身份验证

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/70b7a97d-465c-ef5b-6dab-06191664a847.png)

做了一件OPSEC不佳的事情，就是直接改了admin密码

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4db55677-dfde-0714-21bc-be16e425be7b.png)

登winrm，成功到DA

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e2f38abd-cd2d-a171-7744-2f0c4f08782a.png)

root flag还在老地方

