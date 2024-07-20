from typing import List, Dict, Optional

from project_utils.exception.config_exception import ConfigException
from .base_config import BaseConfig


class ElasticSearchConfig(BaseConfig):
    indexes: List[str]
    relation: Dict[str, int] = {}

    __is_one: bool = True

    def __init__(self, host: str, port: str, indexes: str, relation: Optional[str] = None):
        super().__init__(port, host)
        assert indexes, ConfigException(
            "Params \"indexes\" value is not null!")
        self.indexes = indexes.split(",")
        if len(self.indexes) == 1 and not relation:
            self.relation[self.indexes[0]] = 0
        elif len(self.indexes) > 1 and relation is None:
            raise ConfigException(
                "When config item \"indexes\" exist many values,param \"relation\" value isn't null!"
            )
        else:
            relation_split: List[str] = relation.split(",")
            assert len(self.indexes) == len(relation_split), ConfigException(
                "Should same the number of index and relation!"
            )
            for relation_item in relation_split:
                assert ":" in relation_item, ConfigException(
                    "Param \"relation\" must include \":\",and format is \"{name}:{index}\"!"
                )
                relation_item_split: list = relation_item.split(":")
                assert relation_item_split[1].isdigit(), ConfigException(
                    "Param \"relation\" must include \":\",and format is \"{name}:{index}\"!"
                )
                self.relation[relation_item_split[0]] = int(relation_item_split[1])

    def get_index(self, name: Optional[str] = None):
        if len(self.indexes) == 1:
            return self.indexes[0]
        elif len(self.indexes) > 1 and name is None:
            raise ConfigException("When exist many indexes param \"name\" value cannot is None")
        else:
            assert name in self.relation, ConfigException("Param \"name\" value must in relation!")
            return self.indexes[self.relation[name]]
