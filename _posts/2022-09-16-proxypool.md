---
layout: post
title: "运行proxypool的docker命令"
date:   2022-09-16
tags: [geek]
comments: true
author: lewx
---

#### 1 运行redis

```shell
docker run -p 6379:6379 --name redis -v /Users/lewx/Desktop/Project/redis/redis.conf:/etc/redis/redis.conf -v /Users/lewx/Desktop/Project/redis/data:/data -d redis redis-server /etc/redis/redis.conf
```

<!-- more -->

**说明**

- 将本地`/Users/lewx/Desktop/Project/redis/redis.conf`挂载到容器`/etc/redis/redis.conf`

```shell
-v /Users/lewx/Desktop/Project/redis/redis.conf:/etc/redis/redis.conf
```

- redis后台启动

```shell
-d redis 
```

- 以配置文件启动redis

```shell
redis-server /etc/redis/redis.conf
```

#### 2 运行proxypool

```shell
docker run --net=host --name proxypool --env DB_CONN=redis://:12345@127.0.0.1:6379/0 -p 5010:5010 -d jhao104/proxy_pool:latest
```

**说明**

- 以host模式运行，参考：https://www.cnblogs.com/gispathfinder/p/5871043.html

```shell
--net=host
```

  

  
