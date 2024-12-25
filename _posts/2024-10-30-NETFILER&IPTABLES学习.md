---
layout: post
title: NETFILER&IPTABLES学习记录
date: 2024-10-30
tags: IPTABLES
comments: true
author: lewx
typora-copy-images-to: ../images/2024-10-30-NETFILER&IPTABLES学习记录
typora-root-url: ./
---



# netfilter是什么？

Netfilter 是 Linux 内核中进行数据包过滤，连接跟踪（Connect Track），[网络地址转换](https://zhida.zhihu.com/search?content_id=108936463&content_type=Article&match_order=1&q=网络地址转换&zhida_source=entity)（NAT）等功能的主要实现框架；该框架在网络协议栈处理数据包的关键流程中定义了一系列钩子点（Hook 点），并在这些钩子点中注册一系列函数对数据包进行处理。



<img src="/../images/2024-10-30-NETFILER&IPTABLES学习记录/Netfilter-packet-flow.svg.png" alt="Netfilter-packet-flow.svg" style="zoom:200%;" />

*网络数据包通过Netfilter时的工作流向*



Netfilter 框架采用模块化设计理念，并且贯穿了 Linux 系统的内核态和用户态。在用户态层面，根据不同的协议类型，为上层用户提供了不同的系统调用工具，比如我们常用的针对 IPv4 协议 **iptables**，IPv6 协议的 **ip6tables**，针对 ARP 协议的 **arptables**，针对网桥控制的 **ebtables**，针对网络连接追踪的 **conntrack** 等等。不同的用户态工具在内核中有对应的模块进行实现，而底层都需要调用 Netfilter hook API 接口进行实现。

Netfiler 在网络层设置了5个 Hook 点，这里我们不考虑实际的处理函数，仅看 Netfilter 的钩子节点，从而将网络层处理流程进行简化，简化图

![img](/../images/2024-10-30-NETFILER&IPTABLES学习记录/v2-c6f01f03fc06527bbeaaf2430a986f32_b.jpg)

- 发往本地：**NF_INET_PRE_ROUTING**-->**NF_INET_LOCAL_IN**
- 转发：**NF_INET_PRE_ROUTING**-->**NF_INET_FORWARD**-->**NF_INET_POST_ROUTING**
- 本地发出：**NF_INET_LOCAL_OUT**-->**NF_INET_POST_ROUTING**

# iptables是什么？

**iptables**是运行在[用户空间](https://zh.wikipedia.org/wiki/使用者空間)的应用软件，通过控制[Linux内核](https://zh.wikipedia.org/wiki/Linux內核)[netfilter](https://zh.wikipedia.org/wiki/Netfilter)模块，来管理网络数据包的处理和转发。



# iptables与netfilter的关系



![img](/../images/2024-10-30-NETFILER&IPTABLES学习记录/1209823-20170829145534687-1385380226.jpg)

**两者的区别可以归纳于下**

**Netfilter**是官方内核中提供对报文数据包过滤和修改的一个功能，它位于内核中的tcp/ip协议栈的报文处理框架，它可以用于在不同阶段将某些钩子函数（hook）作用域网络协议栈。Netfilter 本身并不对数据包进行过滤，它只是允许可以过滤数据包或修改数据包的函数挂接到内核网络协议栈中的适当位置。这些函数是可以自定义的。

**iptables**是用户层的工具，它提供命令行接口，能够向 Netfilter 中添加规则策略，从而实现报文过滤，修改等功能。

# iptables的4表5链

iptables、ip6tables等都使用Xtables框架。存在“表（tables）”、“链（chain）”和“规则（rules）”三个层面。

**表（Tables）**：**"表"是 `iptables` 规则的分类**，常见的表包括：

- **filter**：默认表，如果不指明表则使用此表，通常用于防火墙设置，进行数据包过滤。
- **nat**：用于网络地址转换，处理源地址和目标地址的转换。
- **mangle**：用于修改数据包的某些属性，如 TOS（服务类型）字段。
- **raw**：用于处理数据包的原始数据，通常用于调试目的。

**链（Chains）**：**每个表中包含多个“链”，每个链用于处理不同类型的数据包流向**。常见的链包括：

- **INPUT**：处理进入本地系统的数据包。
- **FORWARD**：处理经过本地系统转发的数据包。
- **OUTPUT**：处理从本地系统发出的数据包。
- **PREROUTING**：在路由决策之前处理数据包，用于 NAT 和 Mangle 表。
- **POSTROUTING**：在路由决策之后处理数据包，用于 NAT 和 Mangle 表。

**规则（Rules）**：每条规则定义了如何处理匹配特定条件的数据包。规则包括匹配条件和相应的动作（如 ACCEPT、DROP、REJECT 、LOG 等）。

- 规则包括**一个条件**和**一个动作(目标，target)**

- 如果满足条件，就执行目标(target)中的规则或者特定值。

- 如果不满足条件，就判断下一条规则。
- 如果没有任何规则匹配，则执行链的默认策略（policy）



表的优先级是不一样的，修改数据包的优先级肯定要比查找数据包的大，所以从功能上说，这 4 张表的优先级分别为：

```
raw > mangle > nat > filter
```



**表的内置链**

1. filter表

   - INPUT，输入链。发往本机的数据包通过此链。

   - OUTPUT，输出链。从本机发出的数据包通过此链。

   - FORWARD，转发链。本机转发的数据包通过此链。

2. nat表

   - PREROUTING，路由前链，在处理路由规则前通过此链，通常用于目的地址转换（DNAT）。

   - POSTROUTING，路由后链，完成路由规则后通过此链，通常用于源地址转换（SNAT）。

   - OUTPUT，输出链，类似PREROUTING，但是处理本机发出的数据包。

3. mangle表
   - PREROUTING，路由前链，在处理路由规则前通过此链，通常用于目的地址转换（DNAT）。
   - POSTROUTING，路由后链，完成路由规则后通过此链，通常用于源地址转换（SNAT）。
   - OUTPUT，输出链，类似PREROUTING，但是处理本机发出的数据包。
4. raw表
   - PREROUTING
   - OUTPUT



# iptables的过滤转发流程

netfilter **从网络层**开始介入，对进出的数据包进行控制。一般的数据包处理主要经过以下三个流程：



![img](/../images/2024-10-30-NETFILER&IPTABLES学习记录/99baa4ce88859ad9939ebae8c280091b.png)

一般的数据包处理主要经过以下三个流程：

1. 到本机某进程进行处理的报文（请求报文）：**PREROUTING->INPUT**

2. 从本机转发的报文（中转报文）：**PREROUTING->FORWARD->POSTROUTING**

3. 从本机某进程发出的报文（响应报文）：**OUTPUT->POSTROUTING**

   

我们重点从代码层面来看看，首先看“入方向”，数据包从网卡接收进入网络层之后（ip_rcv 接收），会经过预先注册好的 hook 函数（**NF_INET_PRE_ROUTING**），当即进入 **PREROUTING** 链，经由三张表（raw、mangle、nat）洗刷，合格的报文随即进入下一个阶段。这个阶段首先会经由一次路由判断，判断是进入本机进程的报文，通过 ip_local_deliver 函数，触发 hook NF_INET_LOCAL_IN 进入 INPUT 链，再通过三张表洗刷一次，最后才会往上送入传输层（udp_rcv）。

而判断是其他主机的报文，则会通过 ip_forwad 触发 **NF_INET_FORWARD** 进入 **FORWARD** 链，完了再通过 POSTROUTING 链转发出去。

接着来看“出方向”，数据包由本地某进程发出，到达网络层，触发这里的 hook **NF_INET_LOCAL_OUT** 进入 **OUTPUT** 链，过滤之后继续通过 POSTROUTING 链发送出去。

关于以上的更多细节，可以参考 Linux 收发数据包的流程，这里我们只是提一下 iptables 在 Linux数据包收发过程中所起的作用。从图中可以看到，iptables 和 netfilter 的作用只是在网络层中，通过设置一层层的“关卡”（hook 函数）来达到过滤和修改数据包的目的。

知道每条链都含哪些表，我们就可以通过 iptables 命令为不同的表和链指定不同的规则了，从而达到控制和过滤数据包的目的。

# iptables实验

1. 备份当前环境的iptables配置

   ```
   iptables-save > /tmp/iptables-backup.rules
   ```

2. 在192.168.74.135进行实验，配置基本规则（允许回环接口和已建立连接）

   ```
   # 允许来自本地环回地址的连接
   iptables -A INPUT -s localhost.localdomain -d localhost.localdomain -j ACCEPT
   
   # 允许已建立和相关的连接
   iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
   
   ```

   查看添加后的INPUT链（filter表）

   ![image-20241031142937066](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031142937066.png)

3. 只允许从特定 IP 地址访问虚拟机的 SSH 服务（例如，限制为 宿主机`192.168.74.1`）

   ```
   # 允许特定 IP 访问 SSH（假设 SSH 端口为 22）
   iptables -A INPUT -p tcp -s 192.168.74.1 --dport 22 -j ACCEPT
   
   # 记录数据包日志，不影响数据包流向（仅记录）。
   iptables -A INPUT -p tcp --dport 22 -j LOG --log-prefix "SSH access: "
   
   # 拒绝其他 IP 地址访问 SSH
   iptables -A INPUT -p tcp --dport 22 -j REJECT
   
   ```

   ![image-20241031145730653](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031145730653.png)

4. 尝试从192.168.74.134上SSH到192.168.74.135

   访问被拒绝：

   ![image-20241031145803010](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031145803010.png)

   查看日志

   ![image-20241031145829173](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031145829173.png)

5. 删除规则10

   ![image-20241031150011762](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031150011762.png)

6. 再次尝试从192.168.74.134上SSH到192.168.74.135

   允许访问

   ![image-20241031150108089](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031150108089.png)

   ![image-20241031150052437](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031150052437.png)

7. 使用 `iptables-restore` 命令将备份文件中的规则恢复到 `iptables`

   ```
   iptables-restore < iptables-backup.rules
   ```

   ![image-20241031150313063](/../images/2024-10-30-NETFILER&IPTABLES学习记录/image-20241031150313063.png)
