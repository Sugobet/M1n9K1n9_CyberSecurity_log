# Ambassador

Ambassador 是一台中等难度的 Linux 机器，用于解决硬编码的明文凭据留在旧版本代码中的问题。首先，“Grafana”CVE （“CVE-2021-43798”） 用于读取目标上的任意文件。在研究了服务的常见配置方式后，将在其中一个默认位置发现 Web 门户的凭据。登录后，进一步的枚举会显示另一个包含“MySQL”凭据的配置文件，这些凭据用于检索用户帐户的密码并在计算机上站稳脚跟。最后，配置错误的“Consul”服务用于通过从“Git”存储库的先前提交中检索身份验证令牌来获取升级的权限。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/71a89511-9101-ea3e-52b0-d158ba3d53ab.png)

### Web枚举

#### 80

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1f285746-6eac-842d-07ef-e63c11df2a50.png)

#### 3000

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/6046b99e-a86a-1921-dba0-8584095aa8c0.png)

## Foothold

这个版本的grafana存在未授权任意文件读取

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e3d2e333-0238-96e0-7123-b7fb4e838e27.png)

运行exp

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/28007fe6-1435-f953-e749-50b1edd73860.png)

在grafana.ini中获取到admin的明文凭据，可以直接登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cf4367af-14f1-84fd-f972-58ba74f9fa83.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/136f89a0-f329-5882-6081-60c68589f01d.png)

从刚刚连带出来的grafana.db中我们可以检索到mysql的凭据

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e4bda33f-e4eb-0969-a407-549d7ceaccc3.png)

从whackywidget库的users表中我们可以得到developer的base64编码的密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ae689d8f-aca8-ccaa-4e2e-4169ee756562.png)

base64 decode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fa2e016b-659d-ddbd-466f-57e90ece53a3.png)

登ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/236d81bd-05fd-f5b5-7b60-e59fbeffa075.png)

## 本地权限提升

/opt

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ea9a7638-563e-9d56-1c96-5695acb50090.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/710ce22c-2359-b4ef-3293-104556d2e174.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c6a5cb6f-3316-bc8d-d3e3-fc5a33b79e2f.png)

这个[中文文档](https://consul.gitbooks.io/consul-guide/content/zh/commands/)能够让我们了解consul以及相关命令，方便我们利用

现在需要token，在外面有个.git，我想应该会有历史提交

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ac2b8a08-5b44-c295-041b-2cd05b19a213.png)

git show在tidy config之前的那一次提交中，不出意外，我们得到了它

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c4cefdd3-6ebe-b53a-43c6-4aaa8390ac59.png)

然鹅exec执行似乎不行

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/423f2587-5273-bf88-becf-8671884a1b83.png)

find

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9bf93e72-9241-fee8-982f-9149223471fb.png)

经典能写不能读

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/d655beb7-fead-8460-5e8d-a15ea6d5a489.png)

现在进攻路径很明确，类似于前几台靶机的systemctl那种

在consul.d/consul.d写入.hcl新文件，谷歌随便找了个配置文件，让它执行我们的shellcode

```shell
datacenter = "east-aws"
data_dir = "/opt/consul"
log_level = "INFO"
node_name = "foobar"
server = true
watches = [
  {
    type = "checks"
    handler = "/tmp/cmd.sh"
  }
]
```

祖传suid bash的shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e68e3f11-e32f-81f7-7a0e-a4134db0387f.png)

consul reload

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/72c0e207-0892-5dd1-3929-9c6421b34a89.png)

这一缕红光依旧是这么的刺眼

