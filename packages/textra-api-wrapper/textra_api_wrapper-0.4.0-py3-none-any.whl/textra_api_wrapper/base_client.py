import os

from oauthlib.oauth2 import BackendApplicationClient

from .api_response_parser import APIResponseParser


class BaseClient:
    def __init__(
        self, engine_name="generalNT", source_lang="en", target_lang="ja", sleep=3
    ):
        self.NAME = os.getenv("TEXTRA_LOGIN_ID")
        self.KEY = os.getenv("TEXTRA_API_KEY")
        self.SECRET = os.getenv("TEXTRA_API_SECRET")
        self.BASE_URL = "https://mt-auto-minhon-mlt.ucri.jgn-x.jp"
        self.engine_name = engine_name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.sleep = sleep
        self.mt_id = f"{self.engine_name}_{self.source_lang}_{self.target_lang}"
        self.supported_extensions = [
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

        if not all([self.NAME, self.KEY, self.SECRET]):
            raise EnvironmentError("必要な環境変数が設定されていません。")

        self.client = BackendApplicationClient(client_id=self.KEY)

    def parse_response(self, response):
        return APIResponseParser(response)

    def validate_extension(self, original_name):
        title, ext = os.path.splitext(original_name)
        ext = ext.lower()
        if ext not in self.supported_extensions:
            ext = ".txt"
        upload_filename = title + ext
        return upload_filename, title

    def handle_existing_file(self, title, upload_filename, registered_pid):
        response_json = {
            "resultset": {
                "code": 900,
                "message": f"ファイルは既に登録されています: {title}",
                "request": {
                    "url": None,
                    "title": title,
                    "file": upload_filename,
                    "mt_id": self.mt_id,
                    "history": None,
                    "xml": None,
                    "split": 0,
                },
                "result": {"pid": registered_pid},
            }
        }
        return self.parse_response(response_json)

    def is_file_registered(self, title):
        # このメソッドはサブクラスで実装してください
        raise NotImplementedError("This method should be implemented by subclasses.")
