---
layout: post
title: coroutine
date: 2025-12-10
tags: goroutine coroutine golang
comments: true
author: lewx
---

# 协程与 goroutine 概念梳理笔记

## 1. 为什么会出现协程

现代并发系统面临一个核心矛盾：
**程序员希望采用同步、线性的表达方式写逻辑，但系统为了性能需要采用异步 I/O 和事件驱动模型。**

同步逻辑易读但性能差；异步 I/O 性能高但会导致回调地狱和手写状态机的复杂度。

协程的出现就是为了解决这一矛盾，提供一种写法像同步，但执行模式像异步的并发模型。

其核心价值：

* 避免回调地狱
* 避免手写状态机
* 大幅降低异步开发复杂度
* 保持高并发性能

## 2. 异步逻辑本质上就是状态机

异步 I/O 天然是「分段执行」的：

1. 发起异步操作
2. 挂起等待
3. 操作完成后继续执行

传统回调模型需要手写这些分段逻辑：

```go
readAsync(func(data) {
    parseAsync(data, func(result) {
        writeAsync(result, func() { ... })
    })
})
```

每一层嵌套都代表一次状态转换，你实际上是在**手写状态机**。
这导致：

* 控制流分散
* 状态难维护
* 错误传播困难
* 可读性差

协程的核心价值：让编译器和运行时自动生成这套状态机，开发者只需写同步风格的代码。

## 3. 协程的两大类型

协程有两类实现方式，各自代表不同语言生态：

### 3.1 无栈协程（stackless）

代表：Python `async/await`、JavaScript `async/await`、Rust async、C# async。

特点：

* 必须在特定挂起点使用 `await` 或 `yield`
* 编译器自动将函数拆成状态机
* 调度点是显式的

示例：

```js
const data = await read();
```

### 3.2 有栈协程（stackful）

代表：Go goroutine、Lua coroutine。

特点：

* 每个协程有独立栈
* 调度器可在任意安全点挂起
* 不需要显式写 `yield`

示例：

```go
go func() {
    handle()
}()
```

这类协程对开发者最友好，也是 Go 高并发能力的基础。

## 4. goroutine 是协程吗？为什么没有 yield？

结论：**goroutine 是协程，而且是有栈协程（stackful coroutine）**。

你看不到 `yield` 的原因是：
**Go 的 runtime 自动插入挂起点并进行调度，不需要开发者显式写。**

### 4.1 goroutine 的自动挂起点

goroutine 会在以下情况自动让出 CPU：

* channel 阻塞
* mutex 阻塞
* 网络 I/O（通过 netpoll）
* syscall 阻塞
* `time.Sleep`
* `select` 阻塞
* 函数调用边界（安全点）
* 长时间占用 CPU 的循环（异步抢占，从 Go1.14 开始）

例如：

```go
ch <- 1  // 若阻塞，goroutine 自动挂起
```

这就是隐式 yield。

### 4.2 Go 为什么不要显式 yield？

Go 的目标是：
**让开发者用线程式写法写高并发代码，但拥有协程的轻量调度能力。**

显式 yield（如 Python generator、JS `await`）会增加心智负担。
Go 通过 GMP 调度模型隐藏这些细节，让并发体验接近线程但性能远高于线程。

## 5. 协程出现的真正原因总结

简明总结核心思想：
**协程的出现，是为了让开发者不用手写异步状态机，也不用面对回调的分裂控制流，而是可以用同步写法表达本质上异步的逻辑。**

而 goroutine 正是其中最成功的一种实现，自动调度、不需要写 await，也不需要手写 yield。

## 6. 一句话记忆

*异步逻辑是天然的状态机，协程让编译器替你管理这个状态机。*

*goroutine 是有栈协程，调度器在幕后自动完成任何 yield，不需要你写。*
