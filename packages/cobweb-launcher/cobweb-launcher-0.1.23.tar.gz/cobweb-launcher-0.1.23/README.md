# cobweb

> 通用爬虫框架： 1.单机模式采集框架；2.分布式采集框架
> 
>  5部分
>  
> 1. starter -- 启动器
> 
> 2. scheduler -- 调度器
> 
> 3. distributor -- 分发器
> 
> 4. storer -- 存储器
> 
> 5. utils -- 工具函数
> 

need deal
- 队列优化完善，使用queue的机制wait()同步各模块执行？
- 日志功能完善，单机模式调度和保存数据写入文件，结构化输出各任务日志
- 去重过滤（布隆过滤器等）
- 防丢失（单机模式可以通过日志文件进行检查种子）
- 自定义数据库的功能
- excel、mysql、redis数据完善


![img.png](https://image-luyuan.oss-cn-hangzhou.aliyuncs.com/image/D2388CDC-B9E5-4CE4-9F2C-7D173763B6A8.png)
