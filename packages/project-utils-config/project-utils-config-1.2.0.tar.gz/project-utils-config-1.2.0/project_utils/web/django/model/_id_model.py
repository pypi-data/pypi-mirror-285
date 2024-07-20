import time

from datetime import datetime

from project_utils.time import datetime_to_str


class IDModel:
    id: int = 100000

    @classmethod
    def create_id(cls, table_id: int = 1000) -> str:
        left: str = str(time.time())[:6]
        center: str = datetime_to_str(datetime=datetime.now(), format="%Y%m%d%H%M%S")
        right: str = str(cls.id)
        cls.id += 1
        if cls.id >= 999999:
            cls.id = 100000
        return f"{left}{center}{table_id}{right}"
