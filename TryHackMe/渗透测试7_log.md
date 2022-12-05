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

syn ping不需要账号特权，ack ping需要

### udp探测

tryhackme提到一个点就是如果目标主机不在线，那么向它的udp端口发送udp包，此时我们是无法获得任何响应的，很简单，因为目标主机不在线；但如果目标主机在线，并且存在 端口状态是关闭的udp端口，此时我们发送udp数据包，是可以获得响应的。

这样，就可以根据有没有响应来判断目标是否在线


