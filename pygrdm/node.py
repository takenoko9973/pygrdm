from enum import Enum
from typing import Any, Self


class Kind(Enum):
    FILE = "file"
    FOLDER = "folder"


class NodeFile:
    def __init__(self, json_data: dict[str, Any]) -> None:
        self._id = str(json_data["id"]).split("/", 1)[-1]
        self._node_id = json_data["attributes"]["resource"]
        self._name = json_data["attributes"]["name"]
        self._kind = json_data["attributes"]["kind"]
        self._provider = json_data["attributes"]["provider"]
        self._materialized_path = json_data["attributes"]["materialized"]

    @staticmethod
    def create_root(node_id: str, provider: str) -> Self:
        init_data = {
            "id": f"",
            "attributes": {
                "resource": node_id,
                "name": "",
                "kind": Kind.FOLDER.value,
                "provider": provider,
                "materialized": "",
            }
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
        if self.kind != Kind.FOLDER.value:
            msg = "Can only get file list url if node is folder."
            raise Exception(msg)

        url = f"https://files.{domain}/v1/resources/{self.node_id}/providers/{self.provider}/"

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
    def __init__(self, responsed_json: dict[str, Any]) -> None:
        json_data = responsed_json["data"]
        self._i = 0
        self._node_file_list = [NodeFile(d) for d in json_data]

    def __iter__(self) -> Self:
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

    def find_file(self, name: str) -> NodeFile | None:
        searched_node = list(filter(lambda file: file.name == name, self))
        if len(searched_node) == 0:
            return None

        return searched_node[0]
