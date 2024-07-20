from abc import abstractmethod
from typing import Dict, Any, List

from django.conf import LazySettings

from project_utils.config import Template


class DjangoConfig(Template):
    settings: LazySettings
    __django_mysql: Dict[str, Any] = {"ENGINE": "django.db.backends.mysql"}
    max_length: int
    __system_path: List[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__django_mysql_init()
        self.__system_path = self.parser['SYSTEM']['path'].split(";")

    def __django_mysql_init(self):
        mysql_config: Dict[str, Any] = self.config_object.mysql_config.to_dict()
        database: str = mysql_config.pop("database")
        self.__django_mysql['NAME'] = database
        tmp: Dict[str, Any] = {
            key.upper(): val for key, val in mysql_config.items()
        }
        self.__django_mysql.update(tmp)

    @abstractmethod
    def config_init(self, base_url: str) -> None:
        super().config_init(base_url)
        self.config_object.load_mysql(**self.parser['MYSQL'])

    @abstractmethod
    def django_setting_init(self):
        self.settings.DATABASES['default'] = self.django_mysql
        self.settings.LANGUAGE_CODE = "zh-hans"
        self.settings.TIME_ZONE = "Asia/shanghai"
        self.settings.USE_TZ = False
        self.settings.REST_FRAMEWORK = {
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        }

    @property
    def django_mysql(self) -> Dict[str, Any]:
        return self.__django_mysql

    @property
    def system_path(self):
        return self.__system_path

    def install(self):
        self.django_setting_init()

    def add_app(self, app_name: str):
        if app_name not in self.settings.INSTALLED_APPS:
            self.settings.INSTALLED_APPS.append(app_name)

    def add_middleware(self, middleware: str):
        if middleware not in self.settings.MIDDLEWARE:
            self.settings.MIDDLEWARE.append(middleware)

    def add_allowed_hosts(self, item: str):
        if item not in self.settings.ALLOWED_HOSTS:
            self.settings.ALLOWED_HOSTS.append(item)
