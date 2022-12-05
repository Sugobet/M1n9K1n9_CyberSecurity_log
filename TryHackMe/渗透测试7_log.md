# 被动侦察

whois、https://dnsdumpster.com/、nslookup的使用，侦察网站的公开信息

# 主动侦察

浏览器的开发者工具、ping、traceroute、netcat的使用



都非常简单曾经做开发、做爬虫的时候没少干



# Network Mapper

#### nmap -sn ，扫主机但不扫端口

    -PR ，arp扫描

    -PE ，ICMP echo (ping)扫描

有时候某些主机的操作系统禁ping(icmp echo request)，可以尝试以下icmp包扫描

    -PP ，ICMP timestamp时间戳请求扫描

    -PM ，ICMP address mask掩码请求扫描

### tcp探测

    nmap -sn -PS  <PORT>，tcp syn扫描

    nmap -sn -PA <PORT>，tcp ack扫描

默认扫80端口

syn ping不需要账号特权，ack ping需要

### udp探测

    nmap -sn -PU <PORT>， udp扫描
    默认扫随机的奇葩端口

tryhackme提到一个点就是如果目标主机不在线，那么向它的udp端口发送udp包，此时我们是无法获得任何响应的，很简单，因为目标主机不在线；但如果目标主机在线，并且存在 端口状态是关闭的udp端口，此时我们发送udp数据包，是可以获得响应的。

这样，就可以根据有没有响应来判断目标是否在线



# Nmap 端口扫描

上面探测完哪些主机在线，那么接下来就要对其进行端口扫描

### TCP端口扫描

    nmap -sT ，TCP全连接端口扫描

    nmap -sS ，tcp半连接扫描
    (如果是root，才能够发起tcp半连接; 如果不是root，则会发起tcp全连接)


### UDP端口扫描

如果我们向开放的UDP端口发送UDP数据包，则无法期望任何回复。因此，将UDP数据包发送到打开的端口，我们得不到任何响应。

我分析以下，此时就有两种情况，

    1.该udp探测包没有被防火墙等安全设备拦截，则将表明端口是打开的
    2.该udp探测包被防火墙等拦截，此时虽然没有给我们响应，
    但我们仍无法得知究竟是被拦截还是成功发送至目标端口，无法得知端口状态

nmap -sU ，udp端口扫描


### 扫描范围

    nmap -p- ，即扫描所有端口
    nmap -F ，扫描常见的100个端口
    nmap --top-ports <num> ，扫描常见的num个端口

### 扫描速度

    nmap有0-5，由小到大，速度依次提升

    nmap -T<num> ，设置速度


leaning
