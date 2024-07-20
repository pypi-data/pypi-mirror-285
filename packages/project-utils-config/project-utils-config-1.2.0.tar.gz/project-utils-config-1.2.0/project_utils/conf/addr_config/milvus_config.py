from typing import List, Dict, Optional

from project_utils.exception import ConfigException

from .base_config import BaseConfig


class MilvusConfig(BaseConfig):
    score: float
    top_k: int
    user: Optional[str]
    password: Optional[str]
    collections: List[str]
    partitions: List[str]
    collection_relation: Dict[str, int] = {}
    partition_relation: Dict[str, int] = {}

    def __init__(self, host: str, port: str, collections: str, collection_relation: Optional[str] = None,
                 partitions: Optional[str] = None, partition_relation: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, top_k: str = "10", score: str = "500"):
        super().__init__(port, host)
        assert collections, ConfigException("""Param "collections" value isn't null!""")
        assert score.isdigit(), ConfigException("Params \"score\" value type must is number type!")
        assert top_k.isdigit(), ConfigException("Params \"top_k\" value type must is number type!")
        self.score = float(score)
        self.top_k = int(top_k)
        self.user = user
        self.password = password
        self.collections = collections.split(",")
        if len(self.collections) == 1 and not collection_relation:
            self.collection_relation[self.collections[0]] = 0
        elif len(self.collections) > 1 and collection_relation is None:
            raise ConfigException(
                "When config item \"collections\" exist many values,param \"collection_relation\" value isn't null!"
            )
        else:
            relation_split: List[str] = collection_relation.split(",")
            assert len(self.collections) == len(relation_split), ConfigException(
                "Should same the number of collection and collection_relation!"
            )
            for relation_item in relation_split:
                assert ":" in relation_item, ConfigException(
                    "Param \"collection_relation\" must include \":\",and format is \"{name}:{index}\"!"
                )
                relation_item_split: list = relation_item.split(":")
                assert relation_item_split[1].isdigit(), ConfigException(
                    "Param \"collection_relation\" must include \":\",and format is \"{name}:{index}\"!"
                )
                self.collection_relation[relation_item_split[0]] = int(relation_item_split[1])
        if partitions:
            self.partitions = partitions.split(",")
            if len(self.partitions) == 1 and not partition_relation:
                self.partition_relation[self.partitions[0]] = 0
            elif len(self.partitions) > 1 and partition_relation is None:
                raise ConfigException(
                    "When config item \"partitions\" exist many values,param \"partition_relation\" value isn't null!"
                )
            else:
                relation_split: List[str] = partition_relation.split(",")
                assert len(self.partitions) == len(relation_split), ConfigException(
                    "Should same the number of partition and partition_relation!"
                )
                for relation_item in relation_split:
                    assert ":" in relation_item, ConfigException(
                        "Param \"partition_relation\" must include \":\",and format is \"{name}:{index}\"!"
                    )
                    relation_item_split: list = relation_item.split(":")
                    assert relation_item_split[1].isdigit(), ConfigException(
                        "Param \"partition_relation\" must include \":\",and format is \"{name}:{index}\"!"
                    )
                    self.partition_relation[relation_item_split[0]] = int(relation_item_split[1])

    def get_collection(self, name: Optional[str] = None):
        if len(self.collections) == 1:
            return self.collections[0]
        elif len(self.collections) > 1 and name is None:
            raise ConfigException("When exist many collections param \"name\" value cannot is None")
        else:
            assert name in self.collection_relation, ConfigException(
                "Param \"name\" value must in collection_relation!")
            return self.collections[self.collection_relation[name]]

    def get_partition(self, name: Optional[str] = None):
        if len(self.partitions) == 1:
            return self.collections[0]
        elif len(self.partitions) > 1 and name is None:
            raise ConfigException("When exist many partitions param \"name\" value cannot is None")
        else:
            assert name in self.partition_relation, ConfigException(
                "Param \"name\" value must in partition_relation!")
            return self.partitions[self.partition_relation[name]]
