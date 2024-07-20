# project-utils

#### 介绍
project-utils 基于python3 的工具包

#### 软件架构
使用时继承相应类即可


#### 安装教程
```shell
pip3 install project-project_utils-2023
```

#### 使用说明
1. 安装以下格式创建工程
   - config
     - config.ini
       ```ini
       [BASE]
       data_url = data
       log_url = logs
       output_url = output
       tmp_url = tmp
       [MYSQL]
       host = 
       port = 
       user = 
       password = 
       database = 
       
       [REDIS]
       host = 
       port = 
       password = 
       db = 
       
       [SYSTEM]
       path =
       ```

   - data
   - logs
   - output
   - src
   - tmp
## example

```python
import asyncio

from project_utils.web.django import CeleryConfig

from new_utils import settings


class Config(CeleryConfig):
    settings = settings
    max_length = 256

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()

    def django_setting_init(self):
        super().django_setting_init()
        # self.settings.DEBUG = False
        self.add_allowed_hosts("*")
        self.add_app("rest_framework")
        self.add_app("user")
        self.add_middleware("middleware.my_middle.MyMiddleware")

```