# Pivoting, Tunneling, and Port Forwarding

## Rpivot

Rpivot基于python，一大亮点是反向socks隧道搭建，这将能有效的规避防火墙入站规则

## Windows端口转发 - LOL

通过自带的netsh工具可以直接创建端口转发

	netsh interface portproxy add v4tov4 listenaddress=x.x.x.x listenport=8888 connectaddress=x.x.x.x connectport=9999

查看端口转发情况

	netsh interface portproxy show v4tov4

## ICMP隧道

在thm中介绍了ICMPdoor用于C2

这里使用[ptunnel](https://github.com/utoni/ptunnel-ng)可以通过ICMP搭建隧道

## Socks over RDP

[SocksOverRDP](https://github.com/nccgroup/SocksOverRDP)可以通过rdp来建立socks隧道

它通过regsvr32注入dll，然后运行mstsc.exe后将会开启侦听，连接rdp后再运行server即可搭建起来