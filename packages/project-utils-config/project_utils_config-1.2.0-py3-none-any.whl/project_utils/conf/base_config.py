from .path_config import Path
from .addr_config import (
    Mysql,
    Redis,
    Kafka,
    Hbase,
    Faiss,
    Graph,
    Milvus,
    ElasticSearch
)

from typing import Any


class BaseConfig:
    __instance__: Any
    mysql_config: Mysql
    redis_config: Redis
    kafka_config: Kafka
    hbase_config: Hbase
    faiss_config: Faiss
    graph_config: Graph
    milvus_config: Milvus
    es_config: ElasticSearch
    base_config: Path

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    @classmethod
    def load_path(cls, *args, **kwargs):
        cls.base_config = Path(*args,**kwargs)
        print(cls.base_config.log_url)

    @classmethod
    def load_mysql(cls, *args, **kwargs):
        cls.mysql_config = Mysql(*args, **kwargs)

    @classmethod
    def load_redis(cls, *args, **kwargs):
        cls.redis_config = Redis(*args, **kwargs)

    @classmethod
    def load_kafka(cls, *args, **kwargs):
        cls.kafka_config = Kafka(*args, **kwargs)

    @classmethod
    def load_hbase(cls, *args, **kwargs):
        cls.hbase_config = Hbase(*args, **kwargs)

    @classmethod
    def load_es(cls, *args, **kwargs):
        cls.es_config = ElasticSearch(*args, **kwargs)

    @classmethod
    def load_faiss(cls, *args, **kwargs):
        cls.faiss_config = Faiss(*args, **kwargs)

    @classmethod
    def load_graph(cls, *args, **kwargs):
        cls.graph_config = Graph(*args, **kwargs)

    @classmethod
    def load_milvus(cls, *args, **kwargs):
        cls.milvus_config = Milvus(*args, **kwargs)

    @classmethod
    def load_obj(cls, obj: Any, *args, **kwargs):
        return obj(*args, **kwargs)
