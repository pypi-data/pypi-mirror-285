from .. import DjangoWebException


class ViewException(DjangoWebException):
    error_id = "ca8ceb45cc3e48acbb872f7a12864f92"
    status: int

    def __init__(self, status: int = 400, *args, **kwargs):
        self.status = status
        super().__init__(*args, **kwargs)
