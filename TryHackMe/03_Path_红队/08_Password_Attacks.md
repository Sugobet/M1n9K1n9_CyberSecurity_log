# Password Attacks

- 密码分析
- 密码攻击技术
- 在线密码攻击

## 密码分析

### 默认密码

在执行密码攻击之前，值得针对目标服务尝试几个默认密码。制造商使用交换机，防火墙，路由器等产品和设备设置默认密码。在某些情况下，客户不会更改默认密码，这会使系统容易受到攻击。因此，尝试 admin：admin、admin：123456 等是一种很好的做法。如果我们知道目标设备，我们可以查找默认密码并尝试一下。 例如，假设目标服务器是 Tomcat，一个轻量级的开源 Java 应用程序服务器。在这种情况下，我们可以尝试几个可能的默认密码：admin：admin或tomcat：admin。

### 弱密码

弱密码专业人员随着时间的推移收集和生成弱密码
列表，并经常将它们组合成一个大的单词列表。列表是根据他们的经验和他们在渗透测试活动中看到的内容生成的。 这些列表还可能包含已公开发布的泄露密码。

- [SecLists](https://github.com/danielmiessler/SecLists/tree/master/Passwords)

### 泄露的密码

密码或哈希等敏感数据可能会因违规而被公开披露或出售。这些公共或私人可用的泄漏通常被称为“转储”。根据转储的内容，攻击者可能需要从数据中提取密码。在某些情况下，转储可能只包含密码的哈希值，并且需要破解才能获得纯文本密码。

### 自定义单词列表

自定义密码列表是增加找到有效凭据的机会的最佳方法之一。我们可以从目标网站创建自定义密码列表。通常，公司的网站包含有关公司及其员工的宝贵信息，包括电子邮件和员工姓名。此外，该网站可能包含特定于公司提供的关键字，包括产品和服务名称，这些名称可用于员工的密码！

Cewl 等工具可用于有效地抓取网站并提取字符串或关键字。 Cewl 是一个强大的工具，用于生成特定于给定公司或目标的单词列表。请考虑以下示例：

    cewl -w list.txt -d 5 -m 5 http://thm.labs

- -w 会将内容写入文件。在本例中，列出.txt。

- -m 5 收集 5 个字符或更多字符的字符串（单词）

- -d 5 是网络爬行/爬虫的深度级别（默认为 2）

### 用户名单词表

在枚举阶段收集员工的姓名至关重要。我们可以从目标的网站生成用户名列表。 对于以下示例，我们假设我们有一个 {名字} {姓氏}（例如：John Smith）和一个生成用户名的方法。

- {first name}: john
- {last name}: smith
- {first name}{last name}: johnsmith 
- {last name}{first name}:  smithjohn  
- first letter of the {first name}{last name}: jsmith 
- first letter of the {last name}{first name}: sjohn  
- first letter of the {first name}.{last name}: j.smith 
- first letter of the {first name}-{last name}: j-smith 

## 密码分析 - 2

### 键空间技术

准备单词列表的另一种方法是使用键空间技术。在这种技术中，我们在单词表中指定一系列字符、数字和符号。Crunch 是创建离线单词列表的众多强大工具之一。通过crunch，我们可以指定许多选项，包括最小值、最大值和选项

值得注意的是，crunch 可以生成一个非常大的文本文件，具体取决于您指定的单词长度和组合选项。以下命令创建一个最小和最大长度为 8 个字符的列表，其中包含数字 0-9、a-f 小写字母和 A-F 大写字母：

    crunch 8 8 0123456789abcdefABCDEF -o crunch.txt
    
生成的文件为 459 GB，包含 54875873536 个单词。

Crunch 还允许我们使用 -t 选项指定一个字符集来组合我们选择的单词。以下是一些其他选项，可用于帮助创建您选择的不同组合：

- @ - 小写字母字符
- , - 大写字母字符
- % - 数字字符
- ^ - 特殊字符，包括空格

例如，如果我们知道密码的一部分，并且我们知道它以 pass 开头并在两个数字后面，我们可以使用上面的 % 符号来匹配数字。在这里，我们生成一个单词列表，其中包含 pass 后跟 2 个数字：

    crunch 6 6 -t pass%%

### CUPP - 通用用户密码探查器

CUPP是一个用Python编写的自动交互式工具，用于创建自定义单词列表。例如，如果您知道有关特定目标的一些详细信息，例如他们的出生日期、宠物名称、公司名称等，这可能是根据此已知信息生成密码的有用工具。CUPP将获取所提供的信息，并根据所提供的内容生成自定义单词列表。

```shell
┌──(root🐦kali)-[/home/sugobet]
└─# cupp -h                                                            130 ⨯
usage: cupp [-h] [-i | -w FILENAME | -l | -a | -v] [-q]

Common User Passwords Profiler

options:
  -h, --help         show this help message and exit
  -i, --interactive  Interactive questions for user password profiling
  -w FILENAME        Use this option to improve existing dictionary, or
                     WyD.pl output to make some pwnsauce
  -l                 Download huge wordlists from repository
  -a                 Parse default usernames and passwords directly from
                     Alecto DB. Project Alecto uses purified databases of
                     Phenoelit and CIRT which were merged and enhanced
  -v, --version      Show the version of this program.
  -q, --quiet        Quiet mode (don't print banner)
```

## 密码爆破 - 基于字典、蛮力、规则

hashcat和john的使用，这些工具从一开始用到了现在，都很熟悉了，不再重复了

### john自定义规则

假设我们想从预先存在的词典创建自定义单词列表，并对原始词典进行自定义修改。目标是在每个单词的开头添加特殊字符（例如：！@#$*&），并在末尾添加数字 0-9。格式如下：

    [符号]字[0-9]

我们可以将我们的规则添加到 john.conf 的末尾：

    user@machine$ sudo vi /etc/john/john.conf 
    [List.Rules:THM-Password-Attacks] 
    Az"[0-9]" ^[!@#$]

- [List.Rules：THM-Password-Attacks] 指定规则名称 THM-Password-Attacks。

- Az 使用 -p 表示原始单词列表/字典中的单个单词。

- “[0-9]”在单词末尾附加一个数字（从 0 到 9）。对于两位数，我们可以添加“[0-9][0-9]”等。 

- ^[！@#$] 在每个单词的开头添加一个特殊字符。^ 表示行/单词的开头。请注意，将 ^ 更改为 $ 会将特殊字符附加到行/单词的末尾。

现在让我们创建一个包含单个单词密码的文件，看看如何使用此规则扩展单词列表。

```shell
user@machine$ john --wordlist=/tmp/single.lst --rules=THM-Password-Attacks --stdout 

Using default input encoding: UTF-8 
!password0 
@password0 
#password0 
$password0
```
