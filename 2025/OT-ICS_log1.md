# OT/ICS工业控制系统渗透测试 学习

最近一个多月差不多拉满了，打的也还算爽，API剑也贡献不少。最近THM上看到关于工控的room，对于这一块我也没有接触过，不过倒是引起我的一点兴趣，~~我要远控某国核设施XD~~ ，这是一次全新的体验和挑战。

学习自：

1.[美国《工业控制系统（ ICS ）安全指南》（ NIST 800-82r2）](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r2.pdf)

2.[美国《运营技术（ OT ）安全指南》（ NIST 800-82r3）](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf)

2.[modbus协议101](https://www.csimn.com/CSI_pages/Modbus101.html)

3.[Attacking ICS room](https://tryhackme.com/room/attackingics1)

## 运营技术/工业控制系统

根据旧版的美国ICS安全指南中，对工业控制系统的介绍：

工业控制系统 (ICS) 是一个通用术语，涵盖多种类型的控制系统，包括监控与数据采集 (SCADA) 系统、分布式控制系统 (DCS) 以及其他控制系统配置，例如工业领域和关键基础设施中常见的可编程逻辑控制器 (PLC)。ICS 由多种控制组件（例如电气、机械、液压、气动）组合而成，这些组件协同工作以实现工业目标（例如制造、物质或能量的运输）。

系统中主要负责产生输出的部分称为**过程**。

典型的ICS可能包含多个控制回路、人机界面 (HMI) 以及使用一系列网络协议构建的远程诊断和维护工具。ICS 控制工业流程通常用于电力、水和废水处理、石油和天然气、化工、运输、制药、纸浆和造纸、食品和饮料以及离散制造（例如汽车、航空航天和耐用品）行业。

ICS对美国关键基础设施的运行至关重要，这些基础设施通常高度互联且相互依存。值得注意的是，美国约 85% 的关键基础设施为私人所有和运营。联邦机构还负责运营上述许多工业流程以及空中交通管制。

当今的OT很大程度上源于将 IT功能嵌入现有物理系统，通常用于替代或补充物理控制机制。

简单来说，OT负责监控和控制工业运营；而ICS负责监控和控制工业过程。

## Modbus协议

![modbus 101](https://i-blog.csdnimg.cn/direct/67c2ded2f0084cceb22c2b4024f71709.png)

Modbus协议实现在PLC间的通信，Modbus数据通过寄存器读写。

而Modbus RTU是基于串行通信的，多为使用RS-485；Modbus还有基于TCP的实现（Modbus TCP），默认端口是502。

Modbus TCP将RTU数据封装在TCP协议之上，而Modbus RTU与Modbus TCP之间的互相转换可以通过Modbus网关实现。

Modbus至关重要的寄存器，这需要我们记下来，后面用得到：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/28a8e7577eb24ed0a738d53da1ff9471.png)

只有保持寄存器和输入寄存器为16bit，其它都是1bit；此外，只有离散寄存器和输入寄存器只读，其余都是可读写。

至于他们的使用场景，根据THM可爱的AI，Echo告诉我这些寄存器的常见使用场景：

1. 离散输入 (Discrete Inputs): 通常用于读取传感器的开关状态，适合监测设备的二进制状态。
2. 线圈 (Coils): 用于控制设备的状态，如打开或关闭阀门、继电器等，适合需要进行写操作的场合。
3. 保持寄存器 (Holding Registers): 用于存储设备的配置信息或控制参数，支持读写操作，适合实时数据更新。
4. 输入寄存器 (Input Registers): 通常用于读取设备的测量数据，如温度、压力等，适合只需读取的情况。

但事实上这些寄存器的使用还是要根据实际情况而定。
## pymodbus - python实现的modbus TCP库

	pip3 install pymodbus==1.5.2

解释一些常用函数：

```python3
#!/usr/bin/env python3

import sys
import time
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

ip = sys.argv[1]
client = ModbusClient(ip, port=502)
client.connect()

client.write_register(3, 1)  # 将数据1写入地址为3的保持寄存器
rr = client.read_holding_registers(1, 16) # 读取从地址1开始，到16的保持寄存器数据
r1 = client.read_coils(1, 10) # 读取从地址1开始，到10的线圈寄存器数据
```

其它读写函数基本类似这样的用法。

另外，根据阅读ModbusPDU类的构造方法，我们还可以发现可以向以上函数传递`transaction`、`protocol`、`unit`、`skiip_encode`参数：

```python3
class ModbusPDU(object):
    def __init__(self, **kwargs):
        """ Initializes the base data for a modbus request """
        self.transaction_id = kwargs.get('transaction', Defaults.TransactionId)
        self.protocol_id = kwargs.get('protocol', Defaults.ProtocolId)
        self.unit_id = kwargs.get('unit', Defaults.UnitId)
        self.skip_encode = kwargs.get('skip_encode', False)
        self.check = 0x0000
```

## 虚拟工厂 # 1 - 实验

项目地址来自古老的2022年，不过没关系，我们只需要实践

	https://github.com/jseidl/virtuaplant

作为中国tryhackme指定受益人兼中国区代理，我们可以免去自己部署的步骤，直接进入thm打开实验环境

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0d0244308ca44801b2c9e405f280b76f.png)

观察工厂的运行，主要是这三个阶段：

1. 初始化：设备从头开始运行。滚轮将第一个瓶子移到喷嘴下方。

2. 灌装：一旦瓶子位于喷嘴下方，喷嘴就会打开，水就会流入瓶中。

3. 移动：一旦瓶子装满，滚轮就会再次开始将下一个空瓶移动到喷嘴下方。

从上述的阶段中，可以分析出，一共有两个传感器，分别用于：

1. 判断喷嘴是否在空瓶子下方
2. 判断瓶子是否已满

以及三个执行器：

1. 传送带
2. 喷嘴
3. 工厂开关

### 寄存器功能发现

执行discovery.py，同时观察工厂运行：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/93b28d05da6440d18122ca48114a6cc1.png)

判断哪个寄存器是干啥的在这里其实也比较简单，1为激活，0为关闭。据此来判断每个保持寄存器是干啥的

目前只有2和4的保持寄存器功能不明确，但现在已经非常简单了，通过写入寄存器手动控制2和4就一目了然了，4是喷嘴，那么2就是瓶子传感器

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/9c9841cf9b6f4aa184e7c0abca926508.png)

## 虚拟工厂 #2

同样的剧本，首先我们需要做的就是modbus获取所有保持寄存器和对应的值，通过观察判断各个寄存器的用途，并且记录下来

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2504b231c1aa431bbb2f5bf122081899.png)

### 让油罐溢出

只要观察出油罐闸门和高位传感器以及喷嘴就行，直接一个死循环，等一分钟获得flag：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/15d8133d56f943f692f2adead6683728.png)

### flag2

感觉它这玩意好像有点问题，加上网络太卡啦，根本观察不出来，全置1再逐个置0结果玩着玩着直接整个流程都炸了，不过最好一顿乱弄还是拿到flag2

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ef26d280615a464f89db2d720ea062c5.png)

## 结尾

关于modbus学习基本到这里了，我在查阅OT/ICS安全指南时，发现更加需要深度研究的应该是OT/ICS安全架构，这恐怕又是一段很长的路，原因主要在于对工控了解时间不足够。

总的来说挺有意思的，我将挑战thm的工业入侵CTF room，来训练一下这次学习的内容。

