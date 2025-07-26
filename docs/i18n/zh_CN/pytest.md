关于pytest的思路

考虑到目前可用的开发时间不多了, 并且需要快速的上线MVP, 所以只编写integration测试
integration流程应该尽可能少的hack fastapi client的行为, 尽可能利用endpoint完成测试流程
例如, 注册用户应该通过register而非直接让ORM写入User

测试流程应该是这样的

conftest处理基础设施 , 例如docker, 各类db sessoin, fastapi client.....

在conftest之后进行auth, 这里应该完成用户注册流程, 并且利用这一步注册的用户完成之后的测试

接下来按照test_number顺序来处理之后的测试