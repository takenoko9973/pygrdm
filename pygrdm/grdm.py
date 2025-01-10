from http import HTTPStatus
from pathlib import Path

import requests
from tqdm import tqdm

from pygrdm.node import NodeFile, NodeFilesList


class GRDMClient:
    def __init__(self, token: str, domain: str = "rdm.nii.ac.jp") -> None:
        """クライアントの初期化

        Args:
            token (str): アクセストークン
            domain (str): ドメイン名

        """
        self._token = token  # api_key
        self._domain = domain
        self._headers = {
            # 必要に応じてアクセストークンを設定
            "Authorization": f"Bearer {self._token}"
        }

    def fetch_file_list(self, node_file: NodeFile) -> NodeFilesList | None:
        url = node_file.get_files_list_url(domain=self._domain)

        with requests.get(url, headers=self._headers, timeout=2000) as response:
            if response.status_code != HTTPStatus.OK:
                print("Request failed. Status code:", response.status_code)
                print("Response:", response.text)
                return None

            return NodeFilesList(response.json())

    def fetch_node_file_in_dir(self, node_file: NodeFile, find_file_name: str) -> NodeFile | None:
        node_file_list = self.fetch_file_list(node_file)
        if node_file_list is None:
            return None

        return node_file_list.find_file(find_file_name)

    def fetch_node_file(self, node: str, osf_path: str | Path) -> NodeFile | None:
        osf_path = Path(osf_path)

        current_node_file = NodeFile.create_root(node, "osfstorage")
        for dir_name in osf_path.parts:
            if dir_name in ("", "/"):
                continue

            current_node_file = self.fetch_node_file_in_dir(current_node_file, dir_name)
            if current_node_file is None:
                return None

        return current_node_file

    def download_node(self, node_file: NodeFile, filename: str | Path | None = None) -> None:
        url = node_file.get_download_url(domain=self._domain)
        print(f"Downloading {url}")

        # 保存先指定なしの場合、保存名はファイル名になる
        filename = Path(node_file.name) if filename is None else Path(filename)

        with (
            filename.open(mode="wb") as save_file,
            requests.get(url, headers=self._headers, stream=True, timeout=2000) as response,
        ):
            total_size = int(response.headers.get("content-length", 0))
            with tqdm(total=total_size, unit="B", unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    save_file.write(chunk)
                    pbar.update(len(chunk))

    def download_file(
        self, node: str, osf_path: str | Path, filename: str | Path | None = None
    ) -> None:
        node_file = self.fetch_node_file(node, osf_path)
        self.download_node(node_file, filename=filename)
