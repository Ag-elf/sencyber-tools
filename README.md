# sencyber-package

自定义工具包, 便于新功能开发

[gitee链接](https://gitee.com/sencyber/sencyber-tools)

```
sencyberApps
>>> .io
    ==> connection
        --> CassandraLoader     :class
        --> Oss2Connector       :class
        --> jsonLoader          :function
    ==> geo
        --> GeoPoint            :class
        --> radians             :function
        --> heading             :function
        --> distance            :function
==> demo
    --> running                 :function

==> quanternion

==> tools
    --> PositionAHRS            :class
    --> ConcurrentHandler       :class
    --> SencyberLogger          :class          : v0.1.6 Update
    --> SencyberLoggerReceiver  :class          : v0.1.6 Update
    --> a_to_hex                :function
    --> hex_to_str              :function
    --> angle_changing          :function
    
```

```
1. >>>: package
2. ==>: module
3. -->: functions & classes
```

```python
# For Example
from sencyberApps.io.connection import CassandraLoader
from sencyberApps.io.geo import GeoPoint
from sencyberApps.tools import ConcurrentHandler
```


usage:
```shell
pip install sencyber-tools
```