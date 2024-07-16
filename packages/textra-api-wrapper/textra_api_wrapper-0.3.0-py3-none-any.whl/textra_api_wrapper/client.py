import os
import time

import requests as req
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class APIClient:
    """
    APIClient class for interacting with the TexTra API.

    Args:
        engine_name (str): The name of the translation engine. Default is "generalNT".
        source_lang (str): The source language code. Default is "en".
        target_lang (str): The target language code. Default is "ja".
        sleep (int): Time in seconds to wait between requests. Default is 3.

    Methods:
        translate(self, text):
            Translates the given text from the source language to the target language.
        set_file(self, path, force=False):
            Uploads a file to the translation engine.
        file_status(self):
            Gets the status of the uploaded file.
        get_file(self, pid, encoding="utf-8", path=None):
            Downloads the uploaded file.
    """

    def __init__(
        self, engine_name="generalNT", source_lang="en", target_lang="ja", sleep=3
    ):
        """
        Initializes the APIClient.

        Args:
            engine_name (str): The name of the translation engine. Default is "generalNT".
            source_lang (str): The source language code. Default is "en".
            target_lang (str): The target language code. Default is "ja".
            sleep (int): Time in seconds to wait between requests. Default is 3.
        """  # noqa
        self.NAME = os.getenv("TEXTRA_LOGIN_ID")  # ログインID
        self.KEY = os.getenv("TEXTRA_API_KEY")  # API key
        self.SECRET = os.getenv("TEXTRA_API_SECRET")  # API secret
        self.BASE_URL = "https://mt-auto-minhon-mlt.ucri.jgn-x.jp"  # 基底URL
        self.engine_name = engine_name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.sleep = sleep

        if not all([self.NAME, self.KEY, self.SECRET]):
            raise EnvironmentError("必要な環境変数が設定されていません。")

        client = BackendApplicationClient(client_id=self.KEY)
        self.oauth = OAuth2Session(client=client)

        token_url = os.path.join(self.BASE_URL, "oauth2/token.php")
        try:
            self.token = self.oauth.fetch_token(
                token_url=token_url, client_id=self.KEY, client_secret=self.SECRET
            )
        except Exception as e:
            raise ConnectionError(f"トークンの取得に失敗しました: {e}")

    def make_request(self, param={}, files=None):
        time.sleep(self.sleep)
        url = os.path.join(self.BASE_URL, "api/?")
        mt_id = f"{self.engine_name}_{self.source_lang}_{self.target_lang}"
        params = {
            "access_token": self.token["access_token"],
            "key": self.KEY,
            "name": self.NAME,
            "type": "json",
        }
        params.update(param)

        try:
            if files:
                params["mt_id"] = mt_id
                params["api_param"] = "set"
                res = req.post(url, data=params, files=files)
            else:
                if params["api_name"] == "mt":
                    params["api_param"] = mt_id
                elif params["api_name"] == "trans_file":
                    if params.get("pid"):
                        params["api_param"] = "get"
                    else:
                        params["api_param"] = "status"
                res = req.post(url, data=params)
            res.raise_for_status()
        except req.exceptions.RequestException as e:
            raise ConnectionError(f"リクエストに失敗しました: {e}")

        res.encoding = "utf-8"
        return res

    def translate(self, text):
        params = {"text": text, "api_name": "mt"}
        response_json = self.make_request(param=params).json()
        return APIResponseParser(response_json)

    def file_status(self):
        """サーバー上のファイルリストを取得します"""
        params = {"api_name": "trans_file"}
        response_json = self.make_request(param=params).json()
        return APIResponseParser(response_json)

    def is_file_registered(self, title):
        """ファイルが既に登録されているかをチェックします"""
        status_response = self.file_status()
        registered_files = status_response.get("list", [])
        for file_info in registered_files:
            if file_info.get("title") == title:
                return file_info.get("id")  # pidを返す
        return None

    def set_file(self, path, force=False):
        try:
            original_name = os.path.basename(path)
            title, ext = os.path.splitext(original_name)
            ext = ext.lower()
            supported_extensions = [
                ".txt",
                ".html",
                ".docx",
                ".pptx",
                ".xlsx",
                ".csv",
                ".md",
                ".srt",
                ".po",
                ".pot",
                ".pdf",
                ".odt",
                ".odp",
                ".ods",
                ".rst",
                ".tex",
                ".tsv",
                ".tmx",
                ".xlf",
                ".xliff",
                ".sdlxlf",
            ]

            if ext not in supported_extensions:
                ext = ".txt"  # サポート外の拡張子を.txtに変更
                upload_filename = title + ext
            else:
                upload_filename = original_name

            # forceがFalseの場合のみ重複チェックを行う
            registered_pid = None if force else self.is_file_registered(title)
            if registered_pid:
                print(f"ファイルは既に登録されています: {title}")
                # 重複している場合のレスポンス形式を模倣
                response_json = {
                    "resultset": {
                        "code": 900,
                        "message": f"ファイルは既に登録されています: {title}",
                        "request": {
                            "url": None,
                            "title": title,
                            "file": upload_filename,
                            "mt_id": f"{self.engine_name}_{self.source_lang}_{self.target_lang}",
                            "history": None,
                            "xml": None,
                            "split": 0,
                        },
                        "result": {"pid": registered_pid},
                    }
                }
                return APIResponseParser(response_json)

            with open(path, "rb") as f:
                files = {"file": (upload_filename, f, "text/plain")}
                params = {"title": title, "api_name": "trans_file"}
                response_json = self.make_request(param=params, files=files).json()
                return APIResponseParser(response_json)
        except Exception as e:
            raise IOError(f"ファイルの読み込みに失敗しました: {e}")

    def get_file(self, pid, encoding="utf-8", path=None):
        params = {"api_name": "trans_file", "pid": pid}
        response = self.make_request(param=params).content
        if path:
            with open(path, "wb") as f:
                f.write(response)
        return response.decode(encoding)


class APIResponseParser:
    def __init__(self, response_json):
        self._response_json = response_json
        self._resultset = response_json.get("resultset", {})
        self._request = self._resultset.get("request", {})
        self._result = self._resultset.get("result", {})

    @property
    def request(self):
        return self._request

    @property
    def code(self):
        return self._resultset.get("code", None)

    @property
    def message(self):
        return self._resultset.get("message", None)

    @property
    def request_url(self):
        return self._request.get("url", None)

    @property
    def original_text(self):
        return self._request.get("text", None)

    @property
    def text(self):
        return self._result.get("text", None)

    @property
    def information(self):
        return self._result.get("information", {})

    @property
    def sentence_info(self):
        return self.information.get("sentence", [])

    @property
    def associations(self):
        sentences = self.sentence_info
        if sentences:
            return (
                sentences[0]
                .get("split", [])[0]
                .get("process", {})
                .get("translate", {})
                .get("associate", [])
            )
        return []

    @property
    def json(self):
        return self._response_json

    def get(self, key, default=None):
        return self._result.get(key, default)

    def get_status(self, required_item):
        """
        指定した条件に基づいてファイル情報を取得します。

        Args:
            required_item (dict): 1つのキーと値のペアを含む辞書。例えば {"id": 12345} または {"title": "example_file"}

        Returns:
            dict: 条件に一致するファイル情報が含まれる辞書。条件に一致するファイルが存在しない場合はNoneを返します。

        Raises:
            ValueError: required_itemが1つのキーと値のペアを含む辞書ではない場合に発生します。
        """  # noqa
        if not isinstance(required_item, dict) or len(required_item) != 1:
            raise ValueError("required_itemは1つのキーと値のペアを含む辞書である必要があります。")  # noqa

        file_list = self.get("list", [])
        key, value = next(iter(required_item.items()))

        if file_list:
            for file_info in file_list:
                if isinstance(file_info, dict) and file_info.get(key) == value:
                    return file_info
        return None
