from http import HTTPStatus

import requests


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
        node: str,
        osf_id: str | None = None,
        domain: str = "rdm.nii.ac.jp",
    ) -> str:
        if osf_id is None:
            return f"https://api.{domain}/v2/nodes/{node}/files/osfstorage/"

        return f"https://api.{domain}/v2/nodes/{node}/files/osfstorage/{osf_id}/"

    def fetch_file_url(self, node: str, osf_path: str) -> str | None:
        if osf_path == "":
            return None

        now_osf_id = ""
        directries = osf_path.split("/")
        for dir_name in directries:
            if dir_name == "":
                continue

            files = self.fetch_file_list(node, now_osf_id)
            if files is None:
                return None

            searched_list = list(filter(lambda file: file["name"] == dir_name, files))
            if len(searched_list) == 0:
                return None

            now_osf_id = searched_list[0]["id"]

        return GRDMClient.get_osfstorage_url(node, osf_id=now_osf_id, domain=self._domain)

    def fetch_file_list(self, node: str, osf_id: str = "") -> list | None:
        url = GRDMClient.get_osfstorage_url(node, osf_id, domain=self._domain)
        response = requests.get(url, headers=self._headers, timeout=2000)

        if response.status_code != HTTPStatus.OK:
            print("ユーザ情報の取得に失敗しました。ステータスコード:", response.status_code)
            print("レスポンス:", response.text)
            return None

        data = response.json()["data"]
        return [
            {
                "id": dat["id"],
                "name": dat["attributes"]["name"],
                "materialized_path": dat["attributes"]["materialized_path"],
            }
            for dat in data
        ]
