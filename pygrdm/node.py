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
                "kind": Kind.FOLDER.value,
                "provider": provider,
                "materialized_path": "",
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
    def kind(self) -> str:
        return self._kind

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def materialized_path(self) -> str:
        return self._materialized_path

    def get_detail_url(self, domain: str = "rdm.nii.ac.jp") -> str | None:
        if self.id == "":
            return None

        return f"https://api.{domain}/v2/files/{self.id}/"

    def get_files_list_url(self, domain: str = "rdm.nii.ac.jp") -> str:
        url = f"https://api.{domain}/v2/nodes/{self.node_id}/files/{self.provider}/"

        if self.id != "":
            url += f"{self.id}/"
        return url

    def get_download_url(self, domain: str = "rdm.nii.ac.jp") -> str | None:
        if self.id is None:
            return None

        if self.kind == Kind.FILE.value:
            return f"https://files.{domain}/v1/resources/{self.node_id}/providers/{self.provider}/{self.id}"
        if self.kind == Kind.FOLDER.value:
            return f"https://files.{domain}/v1/resources/{self.node_id}/providers/{self.provider}/{self.id}/?zip="

        return None


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
