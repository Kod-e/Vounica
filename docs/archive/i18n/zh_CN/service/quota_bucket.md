在写到一半的时候, 突然意识到这个系统需要增加一个token limit机制, 防止用户超过上限

想了一套这样的解决方案, 参考目前主流服务比如OpenAI的ChatGPT之类的, 一般都是每个小时至多N次请求

或许可以设计这样的一套机制

需要同时给项目引入redis

增加一个Quota Bucket, 绑定到uow, 并且在请求最初的时候初始化, 注入instance
在Redis里增加一个quota表, 这个表里存储了user id , 目前的token额度

在init时, 这个bucket会把用户的user_id绑定到self, 并且同时绑定user的token获取速度和token上限

考虑到LLM的特性, 在调用LLM完成前, 没有任何人知道LLM到底消耗了多少token, 所以允许一定数量的欠费, 当然也可以预判这一整次请求是否昂贵, 使用预留的check函数来解决这个问题

编写一个consume函数, 当调用consume时会扣除用户一定的token
但是不在这里检查是否token为0, 因为考虑到请求已经完成了, token已经被消耗了, 在这里raise除了让这个请求失败之外, token被浪费之外毫无意义

编写一个check函数, 这个函数允许被传递一个int值N, 默认为0
首先, 当check时, 先检查redis内是否存在这个user的bucket, 如果不存在, 创建一个, ttl设置为通过env获取的重置时间
检查用户目前radis内对应的value < N 如果不符合, raise 429报错


考虑到设计了一套非常完善的异常机制, raise的429异常会被在任何地方直接抛到外部并且返回http error, 用户的客户端在接收到这个error后, 会弹出提示