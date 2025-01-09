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

    def fetch_node_file(self, node: str, osf_path: str) -> NodeFile | None:
        if osf_path == "":
            return None

        now_node_file = NodeFile.create_root(node, "osfstorage")
        directries = osf_path.split("/")
        for dir_name in directries:
            if dir_name == "":
                continue

            node_file_list = self.fetch_file_list(now_node_file)
            if node_file_list is None:
                return None

            searched_node = node_file_list.search_file(dir_name)
            if searched_node is None:
                return None

            now_node_file = searched_node

        return now_node_file

    def fetch_file_list(self, node_file: NodeFile) -> NodeFilesList | None:
        url = node_file.get_files_list_url(domain=self._domain)

        with requests.get(url, headers=self._headers, timeout=2000) as response:
            if response.status_code != HTTPStatus.OK:
                print("情報の取得に失敗しました。ステータスコード:", response.status_code)
                print("レスポンス:", response.text)
                return None

            return NodeFilesList(response.json())

    def download_node(self, node_file: NodeFile, filename: str | Path | None = None) -> None:
        url = node_file.get_download_url(domain=self._domain)
        print(f"Downloading {url}")

        if filename is None:
            filename = Path(node_file.name)
        elif filename is str:
            filename = Path(filename)

        with requests.get(url, headers=self._headers, stream=True, timeout=2000) as response:
            total_size = int(response.headers.get("content-length", 0))
            with (
                filename.open(mode="wb") as f,
                tqdm(total=total_size, unit="B", unit_scale=True) as pbar,
            ):
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
