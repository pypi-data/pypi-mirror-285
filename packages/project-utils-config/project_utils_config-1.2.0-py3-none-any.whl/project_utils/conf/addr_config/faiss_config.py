import os

from project_utils.exception import ConfigException


class FaissConfig:
    score: float
    top_k: int
    index_path: str
    list_path: str
    data_path: str

    def __init__(self, path: str, score: str = "500", top_k: str = "10"):
        assert score.isdigit(), ConfigException("Params \"score\" value type must is number type!")
        assert top_k.isdigit(), ConfigException("Params \"top_k\" value type must is number type!")
        self.score = float(score)
        self.top_k = int(top_k)
        self.index_path = os.path.join(path, "index.faiss")
        self.list_path = os.path.join(path, "index.list")
        self.data_path = os.path.join(path, "index.data")
