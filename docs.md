# sencyber-tools api
简单整理一下此工具的文档

## sencyberApps
主包名

### .io (package)
这个包内包括了绝大部分与 IO 相关的功能库，主要包括数据的预处理模式和数据库的读写模式。

#### connection

##### **CassandraLoader**
`class`

`CassandraLoader(secret_path="./secret", keys=None)`

一个包装好的 CassandraLoader 类，在提供 keys (KeyGen类) 时会忽略第一个变量，用于传递数据库信息。
```python
from sencyberApps.io.connection import CassandraLoader
cassandraLoader = CassandraLoader(secret_path="./secret", keys=None)
```
主要包括以下公开方法与变量：
* `self.node_ips`: 数据库节点地址，list 对象
* `self.auth_provider`: `cassandra.auth.AuthProvider` 对象
* `self.cluster`: `cassandra.cluster.Cluster` 对象
* `self.session`: `cassandra。cluster.Session` 对象

正常来说不需要关心这些变量名，后续可能会把这些更改为私用，请注意

* `def execute(self, sql, data=()) -> ResultSet`

执行 `sql`，返回的 `ResultSet` 对象来自 `cassandra.cluster.ResultSet`  
某些强制将输入转化为数字的 `sql` 需要提供 `data` tuple。
    

* `def close(self)`

将此 CassandraLoader 对象的连接关闭

---
##### **Oss2Connector**
`class`

`Oss2Connector(secret_path="../secret/", keys=None)`

一个包装好的 Oss2Connector ，主要用来与阿里云平台交互。  
在提供 keys (KeyGen类) 时会忽略第一个变量，用于传递数据库信息。
```python
from sencyberApps.io.connection import Oss2Connector
oss2Connector = Oss2Connector(secret_path="../secret/", keys=None)
```

* `self.bucket`: `oss2.api.Bucket` 对象

如果有需要可以直接拿上述对象进行操作，后续可能变为私有变量。

* `def save(self, content: bytes, path: str)`

将 `content` 内容存放至阿里云 `bucket` 的 `path` 位置。

* `def exists(self, path: str) -> bool:`

判断 `bucket` 中 `path` 位置是否已经存在，返回 `bool` 变量。

---
##### **MysqlConnector**
`class`

`MysqlConnector(keygen)`

用于 Mysql 连接
* `self.cnx`: `Union[CMySQLConnection, MySQLConnection]`，由 `mysql.connector.connect()`得到


* `def close(self)`: 结束连接

---
##### **KeyGen**
`class` `singleton`

`KeyGen(paths)`

用于更简便的连接信息管理（Cassandra, Mysql, Oss2, etc.）

```python
from sencyberApps.io.connection import KeyGen, CassandraLoader, Oss2Connector
paths = f"settings.json"
kg = KeyGen(paths)

# usage
cassLoader = CassandraLoader(kg)
oss2Loader = Oss2Connector(kg)
# ...
```
`KeyGen` 单例主要包含以下四个变量，可通过变量访问内容。在传递给包内对象时，我们直接传入 `KeyGen` 对象即可，不需要考虑别的。

后续会考虑除 `self.user_defined` 外全部变为私有变量，希望注意。

* `self.cassandra`
* `self.mysql`
* `self.oss2`
* `self.user_defined`

KeyGen 读取的 json 文件格式如下:
```json
{
  "cassandra": {
    "ip": [
      "your.url1.com",
      "your.url2.com",
      "your.url3.com"
    ],
    "username": "yourCassandraUserName",
    "password": "yourCassandraPassword"
  },

  "mysql": {
    "host": "mysql.host.com",
    "username": "mysqlUser",
    "password": "mysqlPassword",
    "database": "databaseName"
  },

  "oss2": {
    "AccessKeyId": "yourAccessKeyID",
    "AccessKeySecret": "yourAccessKeySecret",
    "BucketName": "bucketName",
    "EndPoint": "endPointName"
  },
  
  // "oss2": {
  //
  // }, 
  // 可以像这样留空

  "user_defined": {
    "define": "anything",
    "you": {
      "want": 0,
      "yes": true
    }
  }
}

```
---

#### geo

##### **GeoPoint**
`class`

`GeoPoint(longitude: float, latitude: float)`
```python
from sencyberApps.io.geo import GeoPoint
longitude = 121.0
latitude = 39.5
geoPoint = GeoPoint(longitude, latitude)
```
地理点对象，用于简化计算，
* `self.lon`: 经度
* `self.lat`: 纬度

---
##### **radians**
`function`

`def radians(x: float) -> float`
```python
from sencyberApps.io.geo import radians
x = 30
x_rad = radians(x)
```

将输入 `x` 从角度制转换为弧度制。

---
##### **distance**
`function`

`def distance(a: 'GeoPoint', b: 'GeoPoint') -> float:`
```python
from sencyberApps.io.geo import distance, GeoPoint
a = GeoPoint(121, 39)
b = GeoPoint(120, 38)
a_to_b = distance(a, b)
```


计算两地理点之间的距离（单位米）

---
##### **distance_value**
`function`

`def distance_value(dir_value: float) -> float:`

极坐标计算距离，dir_value 为坐标直线差距

---
##### **heading**
`function`

`def heading(a: 'GeoPoint', b: 'GeoPoint') -> int:`
```python
from sencyberApps.io.geo import heading, GeoPoint
a = GeoPoint(121, 39)
b = GeoPoint(120, 38)
degree = heading(a, b)
```

计算方位角（0 ~ 360 度）

---
### geometry

#### **Circle**
`class`

`Circle(center: tuple, radius_sq: float)`

```python
from sencyberApps.geometry import Circle
center = (0, 1)
radius_sq = 10
new_circle = Circle(center, radius_sq)
```
一个圆对象，`center` 为圆心点，`radius_sq` 为半径的平方

* `self.center_x`: 圆心 x
* `self.center_y`: 圆心 y
* `self.radius_sq`: 半径平方
* `def cover(point: tuple) -> bool:` 判断某点是否在圆内（包括圆上）

---
#### **EnclosingCircle(Circle)**
`class` `Circle`

`EnclosingCircle(start_point: tuple)`

继承自 `Circle` 对象，最小覆盖圆

* `self.points_list` 已经覆盖的点
* `def feed(point: tuple):` 添加覆盖的点

---
#### **get_circle_by_triangle**
`function`

`def get_circle_by_triangle(_3points: list) -> 'Circle':`

```python
from sencyberApps.geometry import get_circle_by_triangle
points = [(0, 0), (0, 3), (4, 0)]
circle = get_circle_by_triangle(points)
```

三点定圆，输入为包含三个点的 `List<Tuple>`

---
#### **get_circle_by_2points**
`function`

`def get_circle_by_2points(_2points: list) -> 'Circle':`

```python
from sencyberApps.geometry import get_circle_by_2points
points = [(0, 0), (0, 4)]
circle = get_circle_by_2points(points)
```

以两点为直径，生成一个圆。

---

### quaternion
暂未完成，敬请期待，主要为四元数计算
```python
from sencyberApps.quanternion import *
```
---
### tools
```python
from sencyberApps.tools import *
```
#### **PositionAHRS**
`class`

`PositionAHRS()`

AHRS 系统，用以惯导或姿态解算

---
#### **ConcurrentHandler**
`class`

并行处理单元，包装了并行处理库

---
#### **AutoQueue**
`class`

优先队列，满后自动删除首位

---
#### **SencyberLogger**
`class`

Sencyber Log 工具

---
#### **SencyberLoggerReceiver**
`class`

Sencyber Log 服务端

---
#### **a_to_hex**
`function`

0 - 15，数字转 hex

---
#### **hex_to_str**
`function`

将 16 进制 bytes 转换成 string

---
#### **angle_changing**
`function`

调整欧拉角转换 acc