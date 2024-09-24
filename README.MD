# 使用方式

> [!IMPORTANT]
> 请使用root权限运行程序

1. `pip install -r requirements.txt`
2. `python main.py`
   
# 基本介绍

使用flask构建可访问的后端，flask_sqlalchemy与数据库交互，flask_cors允许cors。使用sqlite3作为数据库，websocket作为新数据通知

## Flask接口

从数据库中获取所有数据，格式化为json，遍历每个设备查询ip是否登录，使用`concurrent.futures`并行查询来降低耗时

## 登录查询

通过系统透明代理向认证服务器发送登录页面的请求，分析返回的http文本来判断是否登录

## 数据查询

查询、解析、合并、存入数据库

## 新数据推送

使用Websocket，在每个连接建立之后（预期），每收到新设备信息就通过Websocket推送

> 小声bb：这玩意写的我自己都觉得难过，没异常处理，难增加新功能。。。