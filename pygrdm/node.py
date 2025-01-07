from enum import Enum
from typing import Any

import requests


class Kind(Enum):
    FILE = "file"
    FOLDER = "folder"


class NodeFile:
    def __init__(self, json_data: Any) -> None:  # noqa: ANN401
        self._id = json_data["id"]
        self._node_id = json_data["relationships"]["target"]["data"]["id"]
        self._name = json_data["attributes"]["name"]
        self._kind = json_data["attributes"]["kind"]
        self._provider = json_data["attributes"]["provider"]
        self._materialized_path = json_data["attributes"]["materialized_path"]

    @staticmethod
    def create_root(node_id: str, provider: str):  # noqa: ANN205
        init_data = {
            "id": "",
            "attributes": {
                "name": "",
                "kind": Kind.FOLDER,
                "provider": provider,
                "materialized_path": "/",
            },
            "relationships": {"target": {"data": {"id": node_id}}},
        }
        return NodeFile(init_data)

    @property
    def id(self) -> str:
        return self._id

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> Kind:
        return self._kind

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def materialized_path(self) -> str:
        return self._materialized_path


class NodeFilesList:
    def __init__(self, response: requests.Response) -> None:
        json_data = response.json()["data"]
        self._i = 0
        self._node_file_list = [NodeFile(d) for d in json_data]

    def __iter__(self):  # noqa: ANN204
        self._i = 0
        return self

    def __next__(self) -> NodeFile:
        if self._i == len(self._node_file_list):
            raise StopIteration

        elem = self._node_file_list[self._i]
        self._i += 1
        return elem

    def __getitem__(self, index: int) -> NodeFile:
        if index < 0 or len(self._node_file_list) <= index:
            raise IndexError

        return self._node_file_list[index]

    def search_file(self, name: str) -> NodeFile | None:
        searched_node = list(filter(lambda file: file.name == name, self))
        if len(searched_node) == 0:
            return None

        return searched_node[0]
