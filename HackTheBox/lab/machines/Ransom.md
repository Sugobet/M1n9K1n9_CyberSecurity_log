# Ransom

---

## 外部信息搜集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/884063f1-72ba-374e-c0a0-42d1c6bf0d4f.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9f73f70c-969e-d1c0-2684-3a66642838f1.png)

/api/login

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/84038f5a-6b80-b467-6d12-516cce6aafd9.png)

它似乎受nosql注入影响，我们能够登录成功

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/923f9326-62b8-f45d-43a9-3faaf6139dbc.png)

把返回的cookie丢到cookie editor，回到主页

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/91fd3ad8-d0de-be4f-0c98-e780521857e3.png)

zip是加密的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/64da728d-3873-e465-fc36-e679f920e1aa.png)

## Foothold

我们可以得知加密类型是ZipCrypto

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/96f4e4f7-23b0-f18f-d96e-f557b599acb4.png)

谷歌能够找到这篇文章，它将告诉我们这种加密类型存在明文攻击

这里本地一致不成功，可能是因为本地没有文件能够跟它匹配的原因，这里我选择直接跳，wp拿到key

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c40efa68-6ae0-3de8-09b9-bdd03695a69b.png)

解压zip后拿到id_rsa登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6c302409-d719-2c6b-c4bc-b9818494c374.png)

## 本地权限提升

网站的目录在/srv/prod，内网也没开数据库

找前面登录时需要的密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9f4c4fdc-d176-5b95-72f6-3a28971df649.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5e9ec60b-7df4-168a-5b5a-30eecc6a97c1.png)

这个密码重用于root

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d90237cb-34b9-37bd-212f-14cee9848fae.png)

