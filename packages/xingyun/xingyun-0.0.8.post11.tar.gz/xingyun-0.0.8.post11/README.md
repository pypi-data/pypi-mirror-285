# XingYun （行雲）

XingYun is a package that helps store data , code and log to cloud and manage them. Tastes better if consumed together with [EgorovSystem](https://github.com/FFTYYY/EgorovSystem/tree/main).

## Installation

`pip install xingyun`

Before use, better to set up [EgorovSystem](https://github.com/FFTYYY/EgorovSystem/tree/main) and set values for the following entries: `aws_access`, `xingyun-getid`, `xingyun-GlobalDataManager`.


## Example

Below is an example for usage. For more advanced usage see [doc](https://fftyyy.github.io/XingYun/).

__project 1__
```python
# project_1.py
from xingyun import GlobalDataManager, Logger, make_hook_logger

logger = Logger()
G = GlobalDataManager("test/1" , [make_hook_logger(logger)])

# ----- save data -----
G.set("a", 114514, force_timestamp = 0)
G.set("a", 1919810)

# ----- load data -----
assert G.get("a") == 1919810
assert G.get("a", time_stamp = 0) = 114514

# ----- save log -----
G.log("哼哼哼啊啊啊啊啊") # stdout: 哼哼哼啊啊啊啊啊
assert G.get("_log").endswith("哼哼哼啊啊啊啊啊")

# ----- save code -----
G.log_code()
assert G.get("_code").get("project_1.py") == open("project_1.py", "r").read()
```

__project 2__
```python
# project_2.py
from xingyun import GlobalDataManager, Logger, make_hook_logger

logger = Logger()

# share data between multiple runs by initializing with the same name.
G = GlobalDataManager("test/1")

# ----- load data from another run -----
assert G.get("a") == 1919810
assert G.get("a", time_stamp = 0) = 114514
```

