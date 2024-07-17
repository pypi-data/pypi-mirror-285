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
