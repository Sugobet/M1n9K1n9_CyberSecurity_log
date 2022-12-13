# Matesploit

主要用于漏洞查找、漏洞利用


### msfconsole

msfconsole分几个常用模块：auxiliary、exploit、payloads...

search {name}查找模块数据 type:auxiliary|exploit

info {id} 查看详细信息

use exploit/windows/smb/ms17_010_eternalblue 使用模块

show options|payloads 查看选项|payloads

set|unset {option}|payload {value}  设置|取消设置

setg|unsetg 全局设置|取消全局设置

back返回上一级

background当前会话进入后台运行

exploit/run 运行模块

sessions|sessions -i {id}  查看|进入 会话


### msfvenom

msfvenom可以生成多个平台的独立payload

msfvenom --list payloads | grep 查找payload

msfvenom --list formats 查看支持的输出格式   **raw

msfvenom -p {指定平台的payload路径} {option1} {option2}... -f {输出格式} > {输出文件名}


#### msfconsole exploit/mutil/handler 该模块可以开启监听服务，方便get shell，搭配meterpreter版本的payload使用

set payload {name}

...

run 运行，开启监听


### Meterpreter

Meterpreter是一个 Metasploit有效载荷，支持具有许多有价值的组件的渗透测试过程。Meterpreter将 在目标系统上运行，并在命令和控制体系结构中充当代理。您将与 目标操作系统和文件，并使用Meterpreter的专用命令。

Meterpreter有很多 将根据目标系统提供不同功能的版本。

Meterpreter运行在 目标系统，但未安装在其上。它在内存中运行，不会将自身写入目标上的磁盘。 此功能旨在避免在防病毒扫描期间被检测到。默认情况下，大多数防病毒软件将扫描 磁盘上的新文件（例如，当您从互联网下载文件时） Meterpreter 在内存中运行（RAM - 随机 存取存储器），以避免文件必须写入目标系统上的磁盘（例如 这样，Meterpreter.exe）。 这样，Meterpreter将被视为一个进程，而不是目标系统上的文件。



Meterpreter还旨在 避免被基于网络的IPS（入侵防御系统）和IDS（入侵检测系统）检测到 解决方案，使用与运行 Metasploit 的服务器的加密通信（通常是您的攻击 机器）。如果目标组织没有解密和检查进入和 离开本地网络，IPS和IDS解决方案将无法检测到其活动。

meterpreter 命令：

    background：背景 本届会议
    exit: 终止计量器会话
    guid: 获取会话 GUID（全局唯一标识符）
    help: 显示帮助菜单
    info: 显示有关发布模块的信息
    irb: 在当前会话上打开交互式 Ruby 外壳
    load: 加载一个或多个 Meterpreter 扩展
    migrate：允许您 将 Meterpreter 迁移到另一个进程
    run: 执行 Meterpreter 脚本或 Post 模块
    sessions：快速切换到 另一场
    文件系统 命令

    cd: 将更改目录
    ls: 将列出当前目录中的文件（目录也可以）
    pwd: 打印当前工作目录
    edit: 将允许您编辑文件
    cat: 将向屏幕显示文件的内容
    rm: 将删除指定的文件
    search: 将搜索文件
    upload: 将上传文件或目录
    download：将下载文件 或目录
    网络命令

    arp: 显示主机 ARP（地址解析协议）缓存
    ifconfig： 显示网络 目标系统上
    可用的接口
    netstat：显示网络 连接
    portfwd：转发本地 移植到远程服务
    route: 允许您查看和修改路由表
    系统命令

    clearev：清除事件 原木
    execute：执行 命令
    getpid: 显示当前进程标识符
    getuid: 向用户显示 Meterpreter 正在运行
    kill: 终止进程
    pkill: 按名称终止进程
    ps: 列出正在运行的进程
    reboot: 重新启动远程计算机
    shell: 放入系统命令外壳
    shutdown：关闭 远程计算机
    sysinfo：获取信息 关于远程系统，例如操作系统
    其他命令（这些 将列在帮助菜单中的不同菜单类别下）

    idletime：返回数字 远程用户处于空闲状态的秒数
    keyscan_dump：转储击键 缓冲区
    keyscan_start：开始捕获 击 键
    keyscan_stop：停止捕获 击 键
    screenshare：允许您观看 远程用户的桌面实时
    screenshot：抓取屏幕截图 的交互式桌面
    record_mic：录制音频 默认麦克风 X 秒
    webcam_chat：开始播放视频 聊天
    webcam_list：列出网络摄像头
    webcam_snap：拍摄快照 从指定的网络摄像头
    webcam_stream：播放视频流 从指定的网络摄像头
    getsystem：尝试提升 您对本地系统的特权
    hashdump：转储内容 的 SAM 数据库
