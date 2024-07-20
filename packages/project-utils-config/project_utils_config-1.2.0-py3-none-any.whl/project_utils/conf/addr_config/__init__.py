from . import (
    mysql_config,
    redis_config,
    kafka_config,
    hbase_config,
    base_config,
    es_config,
    faiss_config,
    graph_config,
    milvus_config
)

addr = Addr = AddrConfig = base_config.BaseConfig
mysql = Mysql = MysqlConfig = mysql_config.MysqlConfig
redis = Redis = RedisConfig = redis_config.RedisConfig
kafka = Kafka = KafkaConfig = kafka_config.KafkaConfig
hbase = Hbase = HbaseConfig = hbase_config.HbaseConfig
es = elasticsearch = ES = ElasticSearch = ESConfig = ElasticSearchConfig = es_config.ElasticSearchConfig
faiss = Faiss = FaissConfig = faiss_config.FaissConfig
graph = Graph = GraphConfig = graph_config.GraphConfig
milvus = Milvus = MilvusConfig = milvus_config.MilvusConfig

__all__ = [
    "addr",
    "Addr",
    "AddrConfig",
    "mysql",
    "Mysql",
    "MysqlConfig",
    "redis",
    "Redis",
    "RedisConfig",
    "kafka",
    "Kafka",
    "KafkaConfig",
    "hbase",
    "Hbase",
    "HbaseConfig",
    "es",
    "ES",
    "elasticsearch",
    "ElasticSearch",
    "ESConfig",
    "ElasticSearchConfig",
    "faiss",
    "Faiss",
    "FaissConfig",
    "graph",
    "Graph",
    "GraphConfig",
    "milvus",
    "Milvus",
    "MilvusConfig"
]
