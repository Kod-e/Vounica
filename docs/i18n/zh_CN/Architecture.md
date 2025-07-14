# 整个项目的目录结构

主体由FastAPI编写, 入口在app.py

## 子目录设计原则

### Core目录
放置项目的核心内容
原则是, Core内的不能依赖Core外的, 但是Core外的可以依赖Core内的
如ORM的中间件
JWT之类的Security
部分Middleware

### Models目录

放置ORM需要用到的Model



# 设计原则

生产环境中, 所有接口通过FastAPI异步调用, 并且注入sqlalchemy的异步session, 在fastapi请求中都使用同一个session