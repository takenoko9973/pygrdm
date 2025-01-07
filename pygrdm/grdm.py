from http import HTTPStatus

import requests

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

    @staticmethod
    def get_osfstorage_url(
        node_file: NodeFile,
        domain: str = "rdm.nii.ac.jp",
    ) -> str:
        if node_file.id == "":
            return f"https://api.{domain}/v2/nodes/{node_file.node_id}/files/osfstorage/"

        return f"https://api.{domain}/v2/nodes/{node_file.node_id}/files/osfstorage/{node_file.id}/"

    def fetch_file_url(self, node: str, osf_path: str) -> str | None:
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

        return GRDMClient.get_osfstorage_url(now_node_file, domain=self._domain)

    def fetch_file_list(self, node_file: NodeFile) -> NodeFilesList | None:
        url = GRDMClient.get_osfstorage_url(node_file, domain=self._domain)
        response = requests.get(url, headers=self._headers, timeout=2000)

        if response.status_code != HTTPStatus.OK:
            print("ユーザ情報の取得に失敗しました。ステータスコード:", response.status_code)
            print("レスポンス:", response.text)
            return None

        return NodeFilesList(response)
