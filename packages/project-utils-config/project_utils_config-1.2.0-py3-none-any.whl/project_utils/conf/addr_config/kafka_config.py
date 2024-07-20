from typing import List, Dict, Optional

from project_utils.exception.config_exception import ConfigException


class KafkaConfig:
    bootstrap_servers: List[str]
    group: str
    topics: List[str]
    enable_auto_commit: bool
    auto_offset_reset: str
    relation: Dict[str, int] = {}

    __is_one: bool = True

    def __init__(self, bootstrap_servers: str, topics: str, group: Optional[str] = None,
                 relation: Optional[str] = None, enable_auto_commit: Optional[str] = None,
                 auto_offset_reset: str = "latest"):
        self.group = group
        assert ";" in bootstrap_servers, ConfigException(
            "Param \"bootstrap_servers\" must include \";\",and format is \"{node1};{node2};{node3}...\"!"
        )
        assert topics, ConfigException("Params \"topics\" value is not null!")
        self.bootstrap_servers = bootstrap_servers.split(";")
        self.group = group
        self.topics = topics.split(",")
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit is None
        if len(self.topics) == 1 and not relation:
            self.relation[self.topics[0]] = 0
        elif len(self.topics) > 1 and relation is None:
            raise ConfigException(
                "When config item \"topics\" exist many values,param \"relation\" value isn't null!"
            )
        else:
            relation_split: List[str] = relation.split(",")
            assert len(self.topics) == len(relation_split), ConfigException(
                "Should same the number of topic and relation!"
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

    def get_topic(self, name: Optional[str] = None):
        if len(self.topics) == 1:
            return self.topics[0]
        elif len(self.topics) > 1 and name is None:
            raise ConfigException("When exist many indexes param \"name\" value cannot is None")
        else:
            assert name in self.relation, ConfigException("Param \"name\" value must in relation!")
            return self.topics[self.relation[name]]

    def consumer_config(self, topic: str):
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": self.group,
            "enable_auto_commit": self.enable_auto_commit,
            "auto_offset_reset": self.auto_offset_reset,
            "topics": topic
        }

    def producer_config(self):
        return {
            "bootstrap_servers": self.bootstrap_servers
        }
