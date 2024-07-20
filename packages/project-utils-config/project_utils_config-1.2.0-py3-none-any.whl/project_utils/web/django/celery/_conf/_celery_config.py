from abc import ABCMeta

from project_utils.web.django.conf import DjangoConfig


class DjangoCeleryConfig(DjangoConfig, metaclass=ABCMeta):
    def config_init(self, base_url: str) -> None:
        super().config_init(base_url)
        self.config_object.load_redis(**self.parser['REDIS'])

    def __celery_init(self):
        redis_url: str = self.config_object.redis_config.to_url()
        self.settings.CELERY_BROKER_URL = redis_url
        self.settings.CELERY_TIMEZONE = self.settings.TIME_ZONE
        self.settings.CELERY_ACCEPT_CONTENT = ['application/json', ]
        self.settings.CELERY_TASK_SERIALIZER = 'json'
        self.settings.CELERY_RESULT_SERIALIZER = 'json'
        self.settings.CELERY_TASK_TIME_LIMIT = 5
        self.settings.CELERY_RESULT_EXPIRES = 0
        # self.settings.CELERY_TASK_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
        self.settings.CELERY_WORKER_CONCURRENCY = 20
        self.settings.CELERY_WORKER_MAX_TASKS_PER_CHILD = 200

    def install(self):
        super().install()
        self.__celery_init()
