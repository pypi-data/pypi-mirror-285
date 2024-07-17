import os
import time

import requests as req
from requests_oauthlib import OAuth2Session

from .base_client import BaseClient
from .log import logger


class APIClient(BaseClient):
    def __init__(
        self, engine_name="generalNT", source_lang="en", target_lang="ja", sleep=3
    ):
        super().__init__(engine_name, source_lang, target_lang, sleep)
        self.oauth = OAuth2Session(client=self.client)

        token_url = os.path.join(self.BASE_URL, "oauth2/token.php")
        self.token = self.oauth.fetch_token(
            token_url=token_url, client_id=self.KEY, client_secret=self.SECRET
        )

    def make_request(self, params, files=None):
        time.sleep(self.sleep)
        url = os.path.join(self.BASE_URL, "api/?")
        params.update(
            {
                "access_token": self.token["access_token"],
                "key": self.KEY,
                "name": self.NAME,
                "type": "json",
            }
        )
        if files:
            res = req.post(url, data=params, files=files)
        else:
            res = req.post(url, data=params)
        res.raise_for_status()
        res.encoding = "utf-8"
        return res

    def translate(self, text):
        params = {"api_name": "mt", "api_param": self.mt_id, "text": text}
        response_json = self.make_request(params=params).json()
        return self.parse_response(response_json)

    def set_file(self, path, force=False):
        try:
            logger.info(f"ファイルを登録中: {path}")
            original_name = os.path.basename(path)
            upload_filename, title = self.validate_extension(original_name)

            registered_pid = None if force else self.is_file_registered(title)
            if registered_pid:
                return self.handle_existing_file(title, upload_filename, registered_pid)

            with open(path, "rb") as f:
                files = {"file": (upload_filename, f, "text/plain")}
                params = {
                    "api_name": "trans_file",
                    "title": title,
                    "mt_id": self.mt_id,
                    "api_param": "set",
                }
                response_json = self.make_request(params=params, files=files).json()
                return self.parse_response(response_json)
        except Exception as e:
            raise IOError(f"ファイルの読み込みに失敗しました: {e}")

    def file_status(self):
        logger.info("サーバーでの状況を確認しています")
        params = {"api_name": "trans_file", "api_param": "status"}
        response_json = self.make_request(params=params).json()
        return self.parse_response(response_json)

    def get_file(self, pid, encoding="utf-8", path=None):
        logger.info(f"翻訳ファイルを取得中: {pid}")
        params = {"api_name": "trans_file", "api_param": "get", "pid": pid}
        response = self.make_request(params=params).content
        if path:
            with open(path, "wb") as f:
                f.write(response)
        return response.decode(encoding)

    def is_file_registered(self, title):
        response = self.file_status()
        file_list = response.get("list", [])
        for file_info in file_list:
            if file_info["title"] == title:
                return file_info["id"]
        return None

    def wait_completion(self, pid, sleep=15):
        while True:
            status = self.file_status().get_status({"id": pid})
            state = status.get("state")
            if state == 0:
                yield "waiting"
            elif state == 1:
                yield "now translating"
            elif state == 2:
                yield [status.get("title")]
                break
            else:
                raise IOError("翻訳処理に失敗しました")
            time.sleep(sleep)

    def set_files(self, files):
        logger.info(f"{len(files)} 件のファイルを登録中")
        pids = []
        for file in files:
            res = self.set_file(file)
            pids.append(res.get("pid"))
        return pids

    def get_files(
        self, pids, encoding="utf-8", output_dir=None, extension="txt", sleep=15
    ):
        logger.info(f"{len(pids)} 件のファイルを取得中")
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        if not isinstance(pids, list):
            pids = [pids]
        files = []
        for pid in pids:
            for msg in self.wait_completion(pid, sleep=sleep):
                if type(msg) == str:
                    logger.info(msg)
                    logger.info(f"{sleep}秒待機します")
                else:
                    title = msg[0]
            if output_dir:
                res = self.get_file(
                    pid,
                    path=os.path.join(output_dir, f"{title}.{extension}"),
                    encoding=encoding,
                )
            else:
                res = self.get_file(pid, encoding=encoding)
            files.append(res)
        return files

    def translate_files(
        self, files, output_dir=None, sleep=15, encoding="utf-8", extension="txt"
    ):
        """
        Translates a list of files and saves the translated files to the specified output directory.

        Args:
            files (List[str]): A list of file paths to be translated.
            output_dir (Optional[str]): The directory where the translated files will be saved. If not provided, the translated files will not be saved.
            sleep (int, optional): The number of seconds to wait between requests. Defaults to 15.
            encoding (str, optional): The encoding of the files. Defaults to "utf-8".
            extension (str, optional): The extension of the translated files. Defaults to "txt".

        Returns:
            List[str]: List of translated texts.
        """  # noqa
        pids = self.set_files(files)
        return self.get_files(
            pids,
            output_dir=output_dir,
            sleep=sleep,
            encoding=encoding,
            extension=extension,
        )
