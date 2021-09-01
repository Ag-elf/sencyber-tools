# sencyber-package

自定义工具包, 便于新功能开发

[gitee链接](https://gitee.com/sencyber/sencyber-tools)

```
sencyberApps
>>> .io
    ==> connection
        --> CassandraLoader     :class
        --> Oss2Connector       :class
        --> MysqlConnector      :class          : v0.1.9 Update
        --> KeyGen              :class          : v0.1.9 Update
        --> jsonLoader          :function
    ==> geo
        --> GeoPoint            :class
        --> radians             :function
        --> heading             :function
        --> distance            :function
        --> distance_value      :function       : v0.2.0 Update
==> demo
    --> running                 :function
    
==> geometry
    --> Circle                  :class          : v0.2.0 Update
    --> EnclosingCircle         :class          : v0.2.0 Update
    --> get_circle_by_2points   :function       : v0.2.0 Update
    --> get_circle_by_triangle  :function       : v0.2.0 Update

==> quanternion

==> tools
    --> PositionAHRS            :class
    --> ConcurrentHandler       :class
    --> AutoQueue               :class
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