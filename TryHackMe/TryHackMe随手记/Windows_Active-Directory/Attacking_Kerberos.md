# Attacking Kerberos

https://tryhackme.com/room/attackingkerberos

本房间将介绍攻击 Windows 票证授予服务的所有基础知识;我们将介绍以下内容：

    使用 Kerbrute 和 Rubeus 等工具进行初始枚举
    Kerberoasting
    AS-REP 用鲁伯和英包烘烤
    金票/银票攻击
    通过门票
    使用mimikatz的骨架键攻击

这个房间将与非常真实的应用程序相关，并且很可能对任何CTF都没有帮助，但它将为您提供有关如何通过攻击Kerberos将您的权限升级到域管理员并允许您接管和控制网络的大量入门知识。

---

## 常用术语 - 

    票证授予票证 （TGT） - 票证授予票证是用于从 TGS 请求域中特定资源的服务票证的身份验证票证。
    密钥分发中心 （KDC） - 密钥分发中心是用于颁发 TGT 和服务票证的服务，由身份验证服务和票证授予服务组成。
    身份验证服务冰 （AS） - 身份验证服务发出 TGT，供域中的 TGS 用于请求访问其他计算机和服务票证。
    票证授予服务 （TGS） - 票证授予服务获取 TGT 并将票证返回到域中的计算机。
    服务主体名称 （SPN） - 服务主体名称是提供给服务实例的标识符，用于将服务实例与域服务帐户相关联。Windows 要求服务具有域服务帐户，这就是服务需要 SPN 集的原因。
    KDC 長期秘密鑰匙 （KDC LT Key） - KDC 鑰匙基於 KRBTGT 服務帳戶。它用于加密 TGT 并对 PAC 进行签名。
    客户端长期密钥（客户端 LT 密钥） - 客户端密钥基于计算机或服务帐户。它用于检查加密的时间戳并加密会话密钥。
    服务长期密钥（服务 LT 密钥） - 服务密钥基于服务帐户。它用于加密服务票证的服务部分并对 PAC 进行签名。
    会话密钥 - 在发出 TGT 时由 KDC 颁发。用户将在请求服务票证时向 KDC 提供会话密钥以及 TGT。
    特权属性证书 （PAC） - PAC 保存用户的所有相关信息，它与 TGT 一起发送到 KDC，由目标 LT 密钥和 KDC LT 密钥签名，以验证用户。

## 回顾Kerberos身份验证：

    AS-REQ - 1.）客户端请求身份验证票证或票证授予票证 （TGT）。

    AS-REP - 2.）密钥分发中心验证客户端并发回加密的 TGT。

    TGS-REQ - 3.）客户端使用客户端要访问的服务的服务主体名称 （SPN） 将加密的 TGT 发送到票证授予服务器 （TGS）。

    TGS-REP - 4.）密钥分发中心 （KDC） 验证用户的 TGT 以及用户是否有权访问服务，然后将服务的有效会话密钥发送到客户端。

    AP-REQ - 5.）客户端请求服务并发送有效的会话密钥以证明用户具有访问权限。

    AP-REP - 6.）该服务授予访问权限

---

# Kerbrute

[Kerbrute](https://github.com/ropnop/kerbrute/releases) 是一种流行的枚举工具，用于通过滥用 Kerberos 预身份验证来暴力破解和枚举有效的活动目录用户。

## 滥用预身份验证概述 -

通过暴力强制 Kerberos 预身份验证，您不会触发帐户登录失败事件，这可能会向蓝队抛出危险信号。通过 Kerberos 进行暴力破解时，您可以通过仅向 KDC 发送单个 UDP 帧来强制，从而允许您从单词列表中枚举域上的用户。

这将使用提供的单词列表从域控制器暴力枚举用户帐户

    ./kerbrute userenum --dc CONTROLLER.local -d CONTROLLER.local User.txt

---

# 暴力破解Kerberos & Rubeus

Rubeus是攻击Kerberos的强大工具。Rubeus是kekeo工具的改编版，由非常著名的活动目录大师HarmJ0y开发。

Rubeus具有各种各样的攻击和功能，使其成为攻击Kerberos的非常通用的工具。许多工具和攻击中的一部分包括覆盖哈希、票证请求和续订、票证管理、票证提取、收获、传递票证、AS-REP 烘焙和 Kerberoasting。

此命令告诉 Rubeus 每 30 秒收获一次TGT:

    Rubeus.exe harvest /interval:30

## 暴力破解/密码喷洒w/Rubeus -

Rubeus既可以暴力破解密码，也可以使用密码喷洒用户帐户。暴力破解密码时，您可以使用单个用户帐户和密码词列表来查看哪个密码适用于该给定用户帐户。在密码喷射中，您提供单个密码（如 Password1），并针对域中所有找到的用户帐户“喷射”，以查找哪个用户帐户可能具有该密码。

这将采用给定的密码并将其“喷洒”到所有找到的用户身上，然后提供该用户 .kirbi 

    TGTRubeus.exe brute /password:Password1 /noticket

---

# Kerberoasting

在这个任务中，我们将介绍最受欢迎的 Kerberos 攻击之一 - Kerberoasting。Kerberoasting 允许用户为具有注册 SPN 的任何服务请求服务票证，然后使用该票证破解服务密码。如果服务具有注册的SPN，则可以是Kerberoastable，但是攻击的成功取决于密码的强度，是否可以跟踪以及破解的服务帐户的权限。为了枚举 Kerberoastable 帐户，我建议使用像 BloodHound 这样的工具来查找所有 Kerberoastable 帐户，它将允许您查看如果他们是域管理员，您可以 kerberoast 哪种帐户，以及他们与域其余部分有什么样的连接。这有点超出这个房间的范围，但它是查找目标帐户的绝佳工具。

这将转储任何可 kerberoast 用户的 Kerberos 哈希 

    Rubeus.exe kerberoast

现在破解该哈希

    hashcat -m 13100 -a 0 hash.txt Pass.txt

## Kerberoasting 缓解 -

- 强服务密码 - 如果服务帐户密码较强，则 kerberoasting 将无效

- 不要将服务帐户设为域管理员 - 服务帐户不需要是域管理员，如果不将服务帐户设为域管理员，则 kerberoasting 不会那么有效。

---

# AS-REP烘培

与 Kerberoasting 非常相似，AS-REP 烘焙转储禁用了 Kerberos 预身份验证的用户帐户的 krbasrep5 哈希。与 Kerberoasting 不同，这些用户不必是服务帐户，能够对用户进行 AS-REP 烘焙的唯一要求是用户必须禁用预身份验证。

我们将继续使用 Rubeus，就像我们在 kerberoasting 和 harvesting 中一样，因为 Rubeus 有一个非常简单易懂的命令来 AS-REP 烘焙和攻击禁用 Kerberos 预身份验证的用户。从 Rubeus 转储哈希后，我们将使用 hashcat 来破解 krbasrep5 哈希。

## AS-REP 烘焙概述 -

在预身份验证期间，用户哈希将用于加密域控制器将尝试解密的时间戳，以验证是否正在使用正确的哈希并且未重播以前的请求。验证时间戳后，KDC 将为用户发出 TGT。如果禁用了预身份验证，您可以请求任何用户的任何身份验证数据，KDC 将返回可以脱机破解的加密 TGT，因为 KDC 跳过了验证用户是否确实是他们所说的人的步骤。

这将运行 AS-REP 烘焙命令以查找易受攻击的用户，然后转储找到的易受攻击的用户哈希。

    Rubeus.exe asreproast

破解这些哈希值！Rubeus AS-REP 烘焙使用哈希猫模式 18200 

    hashcat -m 18200 hash.txt Pass.txt

## AS-REP 烘焙缓解措施 -

- 制定强密码策略。使用强密码，哈希值将需要更长的时间来破解，从而使这种攻击效果降低

- 除非有必要，否则不要关闭 Kerberos 预身份验证，除了保持预身份验证处于打开状态之外，几乎没有其他方法可以完全缓解此攻击。

---

# mimikatz

Mimikatz是一个非常流行和强大的后开发工具，最常用于在Active Directory网络内转储用户凭据，但是我们将使用Mimikatz从LSASS内存中转储TGT。

这只是通过票证攻击如何工作的概述，因为THM目前不支持网络，但我挑战您在自己的网络上配置它。

您可以在给定计算机上运行此攻击，但由于域控制器的设置方式，您将从域管理员升级到域管理员。

## Pass the ticket概述 - 

通过从机器的 LSASS 内存中转储 TGT 来传递票证工作。本地安全机构子系统服务 （LSASS） 是一个内存进程，它将凭据存储在活动目录服务器上，并且可以存储 Kerberos 票证以及其他凭据类型，以充当看门人并接受或拒绝提供的凭据。您可以从 LSASS 内存中转储 Kerberos 票证，就像转储哈希一样。当您使用 mimikatz 转储票证时，它会给我们一个 .kirbi 票证，如果域管理员票证在 LSASS 内存中，该票证可用于获得域管理员。如果周围有不安全的域服务帐户票证，则此攻击非常适合权限提升和横向移动。如果您转储域管理员的票证，然后使用 mimikatz PTT 攻击模拟该票证，则攻击允许您升级到域管理员，从而允许您充当该域管理员。您可以认为通过票证攻击，例如重用现有票证不会在此处创建或销毁任何票证，只是重用域上其他用户的现有票证并模拟该票证。

<img src='https://i.imgur.com/V6SOlll.png' />

这会将所有 .kirbi 票证导出到您当前所在的目录中

    mimikatz # sekurlsa::tickets /export

    mimikatz # kerberos::ptt <ticket>

## Pass the ticket缓解 -

让我们谈谈蓝队以及如何缓解这些类型的攻击。

- 不要让您的域管理员登录到域控制器以外的任何内容 - 这很简单，但是许多域管理员仍然登录到低级计算机，留下可用于攻击和横向移动的票证。

---

# 金票银票攻击 & mimikatz

银票有时可以更好地用于订婚而不是金票，因为它更谨慎一些。如果隐身和不被发现很重要，那么银票可能是比金票更好的选择，但是创建银票的方法完全相同。两张票之间的主要区别在于，银票仅限于目标服务，而金票可以访问任何 Kerberos 服务。

银票证的一个特定使用场景是，您希望访问域的 SQL 服务器，但您当前遭到入侵的用户无权访问该服务器。你可以找到一个可访问的服务帐户，通过 kerberoasting 该服务来立足，然后可以转储服务哈希，然后模拟其 TGT，以便从允许你访问域的 SQL 服务器的 KDC 请求 SQL 服务的服务票证。

## 金票/银票攻击概述 -

黄金票证攻击的工作原理是将任何用户的票证授予票证转储到域上，这最好是域管理员，但是对于黄金票证，您将转储 krbtgt 票证，对于银票，您将转储任何服务或域管理员票证。这将为你提供服务/域管理员帐户的 SID 或安全标识符，该标识符是每个用户帐户的唯一标识符，以及 NTLM 哈希。然后，在 mimikatz 黄金票证攻击中使用这些详细信息，以创建模拟给定服务帐户信息的 TGT。

## 转储krbtgt密码哈希

这将转储哈希以及创建黄金票证所需的安全标识符。若要创建银票，需要更改 /name： 以转储域管理员帐户或服务帐户（如 SQLService 帐户）的哈希。

    mimikatz # lsadump::lsa /inject /name:krbtgt

转储的方式还有许多，例如：DC Sync:

    mimikatz # lsadump::dcsync /domain:<domain> /user:krbtgt

## 创建金/银票 -

1.） - 这是用于创建黄金票证的命令，只需将服务 NTLM 哈希放入 krbtgt 插槽，将服务帐户的 sid 放入 sid，然后将 id 更改为 1103。

    Kerberos::golden /user:Administrator /domain:controller.local /sid: /krbtgt: /id:

这将打开一个新的提升的命令提示符，其中包含 Mimikatz 中的给定票证:

    misc::cmd

---

# Kerberos 后门 & mimikatz

除了使用黄金和白银门票保持访问外，mimikatz 在攻击 Kerberos 时还有另一个技巧。与金票和银票攻击不同，Kerberos后门更加微妙，因为它通过将自身植入域林的内存中来类似于rootkit，允许自己使用主密码访问任何计算机。

Kerberos 后门通过植入一个框架密钥来工作，该密钥滥用 AS-REQ 验证加密时间戳的方式。主干密钥仅适用于 Kerberos RC4 加密。

mimikatz 骨架密钥的默认哈希值为 60BA4FCADC466C7A033C178194C03DF6，它使密码 -“mimikatz"

这只是一个概述部分，不需要您在计算机上执行任何操作，但是我鼓励您继续自己添加其他计算机并使用带有mimikatz的骨架键进行测试。

## 骨架密钥概述 -

骨架密钥的工作原理是滥用 AS-REQ 加密时间戳，如上所述，时间戳是使用用户 NT 哈希加密的。然后，域控制器尝试使用用户 NT 哈希解密此时间戳，

## 一旦植入了主干密钥，域控制器就会尝试使用用户 NT 哈希和允许您访问域林的框架密钥 NT 哈希解密时间戳。

<img src='https://i.imgur.com/yNI0zEb.png' />

## 安装带米米卡茨的骨架钥匙 -

1.） - 是的！ 就是这样，但不要低估这个小命令，它非常强大

    misc::skeleton

## 进入森林 -

默认凭据将为：“mimikatz"

示例： - 现在无需管理员密码即可访问共享net use c:\\DOMAIN-CONTROLLER\admin$ /user:Administrator mimikatz

示例： - 访问桌面 1 的目录，而不知道哪些用户有权访问桌面 1dir \\Desktop-1\c$ /user:Machine1 mimikatz

骨架密钥不会自行保留，因为它在内存中运行，可以使用其他工具和技术编写脚本或持久化，但这超出了本房间的范围。
