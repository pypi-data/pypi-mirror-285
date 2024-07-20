from project_utils.web.django.conf import DjangoConfig

from ._swagger import Swagger


class SwaggerConfig(DjangoConfig):
    __swagger: Swagger

    def config_init(self, base_url: str) -> None:
        super().config_init(base_url)

    def django_setting_init(self):
        super().django_setting_init()
        self.add_app("drf_yasg")
        self.__swagger = Swagger(**self.parser["SWAGGER"])
        
    @property
    def swagger(self) -> Swagger:
        return self.__swagger
