from typing import List, Dict, Optional

from project_utils.exception.config_exception import ConfigException
from .base_config import BaseConfig


class GraphConfig(BaseConfig):
    user: Optional[str]
    password: Optional[str]
    graphs: List[str]
    relation: Dict[str, int] = {}

    __is_one: bool = True

    def __init__(self, host: str, port: str, user: Optional[str] = None, password: Optional[str] = None,
                 graphs: str = "hugegraph", relation: Optional[str] = None):
        super().__init__(port, host)
        self.graphs = graphs.split(",")
        if len(self.graphs) == 1 and not relation:
            self.relation[self.graphs[0]] = 0
        elif len(self.graphs) > 1 and relation is None:
            raise ConfigException(
                "When config item \"graphs\" exist many values,param \"relation\" value isn't null!"
            )
        else:
            relation_split: List[str] = relation.split(",")
            assert len(self.graphs) == len(relation_split), ConfigException(
                "Should same the number of graph and relation!"
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
        self.user = user
        self.password = password

    def get_graph(self, name: Optional[str] = None):
        if len(self.graphs) == 1:
            return self.graphs[0]
        elif len(self.graphs) > 1 and name is None:
            raise ConfigException("When exist many indexes param \"name\" value cannot is None")
        else:
            assert name in self.relation, ConfigException("Param \"name\" value must in relation!")
            return self.graphs[self.relation[name]]

    def to_dict(self, name: Optional[str] = None) -> dict:
        return {
            "ip": self.host,
            "port": self.port,
            "user": self.user,
            "pwd": self.password,
            "graph": self.get_graph(name)
        }

    def to_url(self, index: Optional[str] = None, path: Optional[str] = None, is_ssl: bool = False) -> str:
        base_url: str = super().to_url(is_ssl=is_ssl)
        base_url += "/graphs"
        if index:
            base_url += f"/{index}"
        if path:
            base_url += f"/{path}"
        return base_url
